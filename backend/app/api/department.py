from flask import Blueprint, jsonify, request
from app import db
from app.models.department import Department
from app.api.decorators import api_login_required, permission_required

# 创建部门API蓝图
api_department_bp = Blueprint('api_department', __name__, url_prefix='/api')

@api_department_bp.route('/departments', methods=['GET'])
@api_login_required
@permission_required('department_read')
def get_departments():
    departments = Department.query.all()
    return jsonify([{
        'id': department.id,
        'name': department.name,
        'short_name': department.short_name,
        'full_name': department.full_name,
        'level': department.level,
        'parent_id': department.parent_id,
        'phone': department.phone
    } for department in departments])

@api_department_bp.route('/departments/<int:department_id>', methods=['GET'])
@api_login_required
@permission_required('department_read')
def get_department(department_id):
    department = Department.query.get_or_404(department_id)
    return jsonify({
        'id': department.id,
        'name': department.name,
        'short_name': department.short_name,
        'full_name': department.full_name,
        'level': department.level,
        'parent_id': department.parent_id,
        'phone': department.phone
    })

@api_department_bp.route('/departments', methods=['POST'])
@api_login_required
@permission_required('department_create')
def create_department():
    data = request.get_json()
    
    # 检查必填字段
    if not data or not data.get('name'):
        return jsonify({'error': '部门名称是必填字段'}), 400
    
    # 创建新部门
    department = Department(
        name=data['name'],
        short_name=data.get('short_name', ''),
        full_name=data.get('full_name', ''),
        level=data.get('level', 1),
        phone=data.get('phone', '')
    )
    
    if data.get('parent_id'):
        department.parent_id = data['parent_id']
    
    db.session.add(department)
    db.session.commit()
    
    return jsonify({
        'id': department.id,
        'name': department.name,
        'short_name': department.short_name,
        'full_name': department.full_name,
        'level': department.level,
        'parent_id': department.parent_id,
        'phone': department.phone
    }), 201

@api_department_bp.route('/departments/<int:department_id>', methods=['PUT'])
@api_login_required
@permission_required('department_update')
def update_department(department_id):
    department = Department.query.get_or_404(department_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新部门信息
    if 'name' in data:
        department.name = data['name']
    
    if 'short_name' in data:
        department.short_name = data['short_name']
    
    if 'full_name' in data:
        department.full_name = data['full_name']
    
    if 'level' in data:
        department.level = data['level']
    
    if 'parent_id' in data:
        department.parent_id = data['parent_id']
    
    if 'phone' in data:
        department.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        'id': department.id,
        'name': department.name,
        'short_name': department.short_name,
        'full_name': department.full_name,
        'level': department.level,
        'parent_id': department.parent_id,
        'phone': department.phone
    })

@api_department_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@api_login_required
@permission_required('department_delete')
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    return jsonify({'message': '部门删除成功'})