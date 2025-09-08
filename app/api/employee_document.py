from flask import request, jsonify, current_app
from app import db
from app.models import EmployeeDocument, DocumentType, Employee
from app.api.decorators import api_login_required, admin_required, permission_required
from app.utils.validators import validate_required_fields
from app.api import api_bp
from datetime import datetime
import os
from werkzeug.utils import secure_filename

@api_bp.route('/employee-documents', methods=['GET'])
@api_login_required
@permission_required('employee_document_read')
def get_employee_documents():
    """获取员工证件列表"""
    try:
        employee_id = request.args.get('employee_id')
        document_type = request.args.get('document_type')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = EmployeeDocument.query
        
        if employee_id:
            query = query.filter(EmployeeDocument.employee_id == employee_id)
        if document_type:
            query = query.filter(EmployeeDocument.document_type == document_type)
        if status:
            query = query.filter(EmployeeDocument.status == status)
            
        # 按创建时间倒序排列
        query = query.order_by(EmployeeDocument.created_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        documents = [doc.to_dict() for doc in pagination.items]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'documents': documents,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取员工证件列表失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-documents/<int:document_id>', methods=['GET'])
@api_login_required
@permission_required('employee_document_read')
def get_employee_document(document_id):
    """获取单个员工证件详情"""
    try:
        document = EmployeeDocument.query.get_or_404(document_id)
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': document.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取员工证件详情失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-documents', methods=['POST'])
@admin_required
def create_employee_document():
    """创建员工证件"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['employee_id', 'document_type', 'document_name']
        validation_result = validate_required_fields(data, required_fields)
        if not validation_result['valid']:
            return jsonify({
                'code': 400,
                'message': f"缺少必填字段: {', '.join(validation_result['missing_fields'])}"
            }), 400
            
        # 验证员工是否存在
        employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
        if not employee:
            return jsonify({'code': 404, 'message': '员工不存在'}), 404
            
        # 创建证件记录
        document = EmployeeDocument(
            employee_id=data['employee_id'],
            document_type=data['document_type'],
            document_name=data['document_name'],
            document_number=data.get('document_number'),
            issuing_authority=data.get('issuing_authority'),
            issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date() if data.get('issue_date') else None,
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            status=data.get('status', '有效'),
            is_original=data.get('is_original', True),
            notes=data.get('notes')
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '证件创建成功',
            'data': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建员工证件失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-documents/<int:document_id>', methods=['PUT'])
@admin_required
def update_employee_document(document_id):
    """更新员工证件"""
    try:
        document = EmployeeDocument.query.get_or_404(document_id)
        data = request.get_json()
        
        # 更新字段
        if 'document_type' in data:
            document.document_type = data['document_type']
        if 'document_name' in data:
            document.document_name = data['document_name']
        if 'document_number' in data:
            document.document_number = data['document_number']
        if 'issuing_authority' in data:
            document.issuing_authority = data['issuing_authority']
        if 'issue_date' in data:
            document.issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d').date() if data['issue_date'] else None
        if 'expiry_date' in data:
            document.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data['expiry_date'] else None
        if 'status' in data:
            document.status = data['status']
        if 'is_original' in data:
            document.is_original = data['is_original']
        if 'notes' in data:
            document.notes = data['notes']
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '证件更新成功',
            'data': document.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新员工证件失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-documents/<int:document_id>', methods=['DELETE'])
@admin_required
def delete_employee_document(document_id):
    """删除员工证件"""
    try:
        document = EmployeeDocument.query.get_or_404(document_id)
        
        # 删除关联文件
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
            
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '证件删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除员工证件失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/document-types', methods=['GET'])
@api_login_required
@permission_required('employee_document_read')
def get_document_types():
    """获取证件类型列表"""
    try:
        types = DocumentType.query.order_by(DocumentType.category, DocumentType.type_name).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [doc_type.to_dict() for doc_type in types]
        })
        
    except Exception as e:
        current_app.logger.error(f"获取证件类型列表失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-documents/expiring', methods=['GET'])
@api_login_required
@permission_required('employee_document_read')
def get_expiring_documents():
    """获取即将过期的证件"""
    try:
        days = int(request.args.get('days', 30))
        
        from datetime import date, timedelta
        expiry_threshold = date.today() + timedelta(days=days)
        
        documents = EmployeeDocument.query.filter(
            EmployeeDocument.expiry_date.isnot(None),
            EmployeeDocument.expiry_date <= expiry_threshold,
            EmployeeDocument.status == '有效'
        ).order_by(EmployeeDocument.expiry_date).all()
        
        result = []
        for doc in documents:
            doc_dict = doc.to_dict()
            doc_dict['days_to_expiry'] = doc.days_to_expiry
            doc_dict['is_expired'] = doc.is_expired
            result.append(doc_dict)
            
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取即将过期证件失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500