from flask import request, jsonify, current_app
from app import db
from app.models import EmployeeRewardPunishment, RewardPunishmentType, Employee
from app.api.decorators import api_login_required, admin_required, permission_required
from app.utils.validators import validate_required_fields
from app.api import api_bp
from datetime import datetime
import os
from werkzeug.utils import secure_filename

@api_bp.route('/employee-reward-punishments', methods=['GET'])
@api_login_required
@permission_required('employee_reward_punishment_read')
def get_employee_reward_punishments():
    """获取员工奖惩记录列表"""
    try:
        employee_id = request.args.get('employee_id')
        type_filter = request.args.get('type')  # 奖励/惩罚
        category = request.args.get('category')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = EmployeeRewardPunishment.query
        
        if employee_id:
            query = query.filter(EmployeeRewardPunishment.employee_id == employee_id)
        if type_filter:
            query = query.filter(EmployeeRewardPunishment.type == type_filter)
        if category:
            query = query.filter(EmployeeRewardPunishment.category == category)
        if status:
            query = query.filter(EmployeeRewardPunishment.status == status)
        if start_date:
            query = query.filter(EmployeeRewardPunishment.decision_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(EmployeeRewardPunishment.decision_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
            
        # 按决定日期倒序排列
        query = query.order_by(EmployeeRewardPunishment.decision_date.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        records = [record.to_dict() for record in pagination.items]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'records': records,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'total': pagination.total,
                    'per_page': pagination.per_page,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next,
                    'prev_num': pagination.prev_num,
                    'next_num': pagination.next_num
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取员工奖惩记录列表失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-reward-punishments/<int:record_id>', methods=['GET'])
@api_login_required
@permission_required('employee_reward_punishment_read')
def get_employee_reward_punishment(record_id):
    """获取单个员工奖惩记录详情"""
    try:
        record = EmployeeRewardPunishment.query.get_or_404(record_id)
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': record.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取员工奖惩记录详情失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-reward-punishments', methods=['POST'])
@admin_required
def create_employee_reward_punishment():
    """创建员工奖惩记录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['employee_id', 'type', 'category', 'title', 'decision_date']
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
            
        # 验证类型
        if data['type'] not in ['奖励', '惩罚']:
            return jsonify({'code': 400, 'message': '类型必须是奖励或惩罚'}), 400
            
        # 创建奖惩记录
        record = EmployeeRewardPunishment(
            employee_id=data['employee_id'],
            type=data['type'],
            category=data['category'],
            title=data['title'],
            description=data.get('description'),
            reason=data.get('reason'),
            amount=data.get('amount'),
            decision_date=datetime.strptime(data['decision_date'], '%Y-%m-%d').date(),
            effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d').date() if data.get('effective_date') else None,
            decision_maker=data.get('decision_maker'),
            decision_department=data.get('decision_department'),
            approval_level=data.get('approval_level'),
            status=data.get('status', '生效'),
            is_public=data.get('is_public', False),
            notes=data.get('notes')
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '奖惩记录创建成功',
            'data': record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建员工奖惩记录失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-reward-punishments/<int:record_id>', methods=['PUT'])
@admin_required
def update_employee_reward_punishment(record_id):
    """更新员工奖惩记录"""
    try:
        record = EmployeeRewardPunishment.query.get_or_404(record_id)
        data = request.get_json()
        
        # 更新字段
        if 'type' in data:
            if data['type'] not in ['奖励', '惩罚']:
                return jsonify({'code': 400, 'message': '类型必须是奖励或惩罚'}), 400
            record.type = data['type']
        if 'category' in data:
            record.category = data['category']
        if 'title' in data:
            record.title = data['title']
        if 'description' in data:
            record.description = data['description']
        if 'reason' in data:
            record.reason = data['reason']
        if 'amount' in data:
            record.amount = data['amount']
        if 'decision_date' in data:
            record.decision_date = datetime.strptime(data['decision_date'], '%Y-%m-%d').date()
        if 'effective_date' in data:
            record.effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d').date() if data['effective_date'] else None
        if 'decision_maker' in data:
            record.decision_maker = data['decision_maker']
        if 'decision_department' in data:
            record.decision_department = data['decision_department']
        if 'approval_level' in data:
            record.approval_level = data['approval_level']
        if 'status' in data:
            record.status = data['status']
        if 'is_public' in data:
            record.is_public = data['is_public']
        if 'notes' in data:
            record.notes = data['notes']
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '奖惩记录更新成功',
            'data': record.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新员工奖惩记录失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-reward-punishments/<int:record_id>', methods=['DELETE'])
@admin_required
def delete_employee_reward_punishment(record_id):
    """删除员工奖惩记录"""
    try:
        record = EmployeeRewardPunishment.query.get_or_404(record_id)
        
        # 删除关联附件
        if record.attachment_path and os.path.exists(record.attachment_path):
            os.remove(record.attachment_path)
            
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '奖惩记录删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除员工奖惩记录失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/reward-punishment-types', methods=['GET'])
@api_login_required
@permission_required('employee_reward_punishment_read')
def get_reward_punishment_types():
    """获取奖惩类型列表"""
    try:
        types = RewardPunishmentType.query.order_by(RewardPunishmentType.category, RewardPunishmentType.type_name).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [rp_type.to_dict() for rp_type in types]
        })
        
    except Exception as e:
        current_app.logger.error(f"获取奖惩类型列表失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@api_bp.route('/employee-reward-punishments/summary', methods=['GET'])
@api_login_required
@permission_required('employee_reward_punishment_read')
def get_employee_reward_punishment_summary():
    """获取员工奖惩统计摘要"""
    try:
        employee_id = request.args.get('employee_id')
        year = request.args.get('year', datetime.now().year)
        
        query = EmployeeRewardPunishment.query
        
        if employee_id:
            query = query.filter(EmployeeRewardPunishment.employee_id == employee_id)
            
        # 按年份过滤
        query = query.filter(db.extract('year', EmployeeRewardPunishment.decision_date) == year)
        
        records = query.all()
        
        # 统计数据
        summary = {
            'total_records': len(records),
            'rewards': len([r for r in records if r.type == '奖励']),
            'punishments': len([r for r in records if r.type == '惩罚']),
            'total_reward_amount': sum([float(r.amount) for r in records if r.type == '奖励' and r.amount]),
            'total_punishment_amount': sum([float(r.amount) for r in records if r.type == '惩罚' and r.amount]),
            'categories': {}
        }
        
        # 按类别统计
        for record in records:
            if record.category not in summary['categories']:
                summary['categories'][record.category] = {'count': 0, 'type': record.type}
            summary['categories'][record.category]['count'] += 1
            
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': summary
        })
        
    except Exception as e:
        current_app.logger.error(f"获取员工奖惩统计摘要失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500