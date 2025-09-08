from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.employee import Employee
from app.models.user import User
from app.models.department import Department
from app.api.decorators import admin_required, api_login_required, permission_required
from app.utils.pagination_service import PaginationService
from datetime import datetime
import os
from werkzeug.utils import secure_filename

employee_bp = Blueprint('employee_api', __name__)
pagination_service = PaginationService()

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@employee_bp.route('/employees', methods=['GET'])
@login_required
@admin_required
def get_employees():
    """获取员工列表"""
    try:
        # 构建查询
        query = db.session.query(Employee).join(User).join(Department, Employee.department_id == Department.id, isouter=True)
        
        # 搜索过滤
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(
                db.or_(
                    Employee.employee_id.like(f'%{search}%'),
                    Employee.name.like(f'%{search}%'),
                    Employee.phone.like(f'%{search}%'),
                    # User表不再包含name字段，只搜索Employee表
                )
            )
        
        # 部门过滤
        department_id = request.args.get('department_id')
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        # 在职状态过滤
        employment_status = request.args.get('employment_status')
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status)
        
        # 分页查询
        result = pagination_service.paginate_query(
            query=query,
            model_class=Employee,
            default_sort='created_at',
            allowed_sorts=['name', 'employee_id', 'created_at', 'updated_at'],
            eager_load=['department']
        )
        
        # 格式化数据
        employees_data = []
        for employee in result['items']:
            employee_dict = employee.to_dict()
            # Employee表已包含name字段，无需从User表获取
            employee_dict['department_name'] = employee.department.name if employee.department else None
            employees_data.append(employee_dict)
        
        result['items'] = employees_data
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取员工列表失败: {str(e)}'
        }), 500

@employee_bp.route('/employees/<int:user_id>', methods=['GET'])
@api_login_required
@permission_required('employee_read')
def get_employee(user_id):
    """获取单个员工信息"""
    try:
        # 检查权限：管理员或本人
        if not current_user.is_admin() and current_user.id != user_id:
            return jsonify({
                'success': False,
                'message': '权限不足'
            }), 403
        
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return jsonify({
                'success': False,
                'message': '员工信息不存在'
            }), 404
        
        employee_dict = employee.to_dict()
        # Employee表已包含name字段，无需从User表获取
        employee_dict['department_name'] = employee.department.name if employee.department else None
        
        return jsonify({
            'success': True,
            'data': employee_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取员工信息失败: {str(e)}'
        }), 500

@employee_bp.route('/employees', methods=['POST'])
@login_required
@admin_required
def create_employee():
    """创建员工信息"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['user_id', 'employee_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 检查用户是否存在
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 400
        
        # 检查员工工号是否已存在
        existing_employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
        if existing_employee:
            return jsonify({
                'success': False,
                'message': '员工工号已存在'
            }), 400
        
        # 检查用户是否已有员工信息
        existing_user_employee = Employee.query.filter_by(user_id=data['user_id']).first()
        if existing_user_employee:
            return jsonify({
                'success': False,
                'message': '该用户已有员工信息'
            }), 400
        
        # 创建员工信息
        employee = Employee(
            user_id=data['user_id'],
            employee_id=data['employee_id'],
            department_id=data.get('department_id'),
            job_title=data.get('job_title'),
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None,
            work_years=data.get('work_years'),
            name=data.get('name'),  # 使用传入的name
            gender=data.get('gender'),
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            id_card=data.get('id_card'),
            native_place=data.get('native_place'),
            nationality=data.get('nationality'),
            education=data.get('education'),
            marital_status=data.get('marital_status'),
            phone=data.get('phone'),  # 使用传入的phone
            address=data.get('address'),
            employment_status=data.get('employment_status', '在职'),
            emergency_contact=data.get('emergency_contact'),
            emergency_phone=data.get('emergency_phone')
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '员工信息创建成功',
            'data': employee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建员工信息失败: {str(e)}'
        }), 500

@employee_bp.route('/employees/<int:user_id>', methods=['PUT'])
@api_login_required
@permission_required('employee_update')
def update_employee(user_id):
    """更新员工信息"""
    try:
        # 检查权限：管理员或本人
        if not current_user.is_admin() and current_user.id != user_id:
            return jsonify({
                'success': False,
                'message': '权限不足'
            }), 403
        
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return jsonify({
                'success': False,
                'message': '员工信息不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'employee_id' in data and data['employee_id'] != employee.employee_id:
            # 检查新工号是否已存在
            existing = Employee.query.filter_by(employee_id=data['employee_id']).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': '员工工号已存在'
                }), 400
            employee.employee_id = data['employee_id']
        
        # 只有管理员可以修改的字段
        if current_user.is_admin():
            if 'department_id' in data:
                employee.department_id = data['department_id']
            if 'job_title' in data:
                employee.job_title = data['job_title']
            if 'hire_date' in data:
                employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data['hire_date'] else None
            if 'work_years' in data:
                employee.work_years = data['work_years']
            if 'employment_status' in data:
                employee.employment_status = data['employment_status']
        
        # 员工可以修改的字段
        if 'name' in data:
            employee.name = data['name']
        if 'gender' in data:
            employee.gender = data['gender']
        if 'birth_date' in data:
            employee.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data['birth_date'] else None
        if 'id_card' in data:
            employee.id_card = data['id_card']
        if 'native_place' in data:
            employee.native_place = data['native_place']
        if 'nationality' in data:
            employee.nationality = data['nationality']
        if 'education' in data:
            employee.education = data['education']
        if 'marital_status' in data:
            employee.marital_status = data['marital_status']
        if 'phone' in data:
            employee.phone = data['phone']
        if 'address' in data:
            employee.address = data['address']
        if 'emergency_contact' in data:
            employee.emergency_contact = data['emergency_contact']
        if 'emergency_phone' in data:
            employee.emergency_phone = data['emergency_phone']
        
        employee.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '员工信息更新成功',
            'data': employee.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新员工信息失败: {str(e)}'
        }), 500

@employee_bp.route('/employees/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_employee(user_id):
    """删除员工信息"""
    try:
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return jsonify({
                'success': False,
                'message': '员工信息不存在'
            }), 404
        
        # 删除头像文件
        if employee.avatar_path and os.path.exists(employee.avatar_path):
            os.remove(employee.avatar_path)
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '员工信息删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除员工信息失败: {str(e)}'
        }), 500

@employee_bp.route('/employees/<int:user_id>/avatar', methods=['POST'])
@api_login_required
@permission_required('employee_avatar_upload')
def upload_avatar(user_id):
    """上传员工头像"""
    try:
        # 检查权限：管理员或本人
        if not current_user.is_admin() and current_user.id != user_id:
            return jsonify({
                'success': False,
                'message': '权限不足'
            }), 403
        
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return jsonify({
                'success': False,
                'message': '员工信息不存在'
            }), 404
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        if file and allowed_file(file.filename):
            # 创建上传目录
            upload_dir = os.path.join('uploads', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{employee.employee_id}_{timestamp}_{filename}"
            file_path = os.path.join(upload_dir, filename)
            
            # 删除旧头像
            if employee.avatar_path and os.path.exists(employee.avatar_path):
                os.remove(employee.avatar_path)
            
            # 保存新头像
            file.save(file_path)
            employee.avatar_path = file_path
            employee.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '头像上传成功',
                'data': {
                    'avatar_path': file_path
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '不支持的文件格式，请上传 PNG、JPG、JPEG 或 GIF 格式的图片'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'上传头像失败: {str(e)}'
        }), 500

@employee_bp.route('/employees/statistics', methods=['GET'])
@login_required
@admin_required
def get_employee_statistics():
    """获取员工统计信息"""
    try:
        # 总员工数
        total_count = Employee.query.count()
        
        # 在职员工数
        active_count = Employee.query.filter_by(employment_status='在职').count()
        
        # 按部门统计
        department_stats = db.session.query(
            Department.name,
            db.func.count(Employee.user_id)
        ).join(Employee, Department.id == Employee.department_id, isouter=True)\
         .group_by(Department.name).all()
        
        # 按性别统计
        gender_stats = db.session.query(
            Employee.gender,
            db.func.count(Employee.user_id)
        ).group_by(Employee.gender).all()
        
        # 按学历统计
        education_stats = db.session.query(
            Employee.education,
            db.func.count(Employee.user_id)
        ).group_by(Employee.education).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'active_count': active_count,
                'department_stats': [{'name': name, 'count': count} for name, count in department_stats],
                'gender_stats': [{'gender': gender, 'count': count} for gender, count in gender_stats],
                'education_stats': [{'education': education, 'count': count} for education, count in education_stats]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500