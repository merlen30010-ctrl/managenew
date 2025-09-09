from flask import Blueprint, request, jsonify
from app import db
from app.models.employee import Employee
from app.utils.anti_spam import anti_spam_required, record_submission_attempt, anti_spam
from datetime import datetime
import re

application_bp = Blueprint('application_api', __name__)

def validate_id_card(id_card):
    """验证身份证号格式"""
    if not id_card:
        return False
    
    # 18位身份证号正则表达式
    pattern = r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$'
    return bool(re.match(pattern, id_card))

def validate_phone(phone):
    """验证手机号格式"""
    if not phone:
        return False
    
    # 中国手机号正则表达式
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_email(email):
    """验证邮箱格式"""
    if not email:
        return False
    
    # 邮箱正则表达式
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

@application_bp.route('/application/submit', methods=['POST'])
@anti_spam_required
def submit_application():
    """公开的应聘信息提交API接口"""
    ip = anti_spam.get_client_ip()
    
    try:
        # 获取JSON数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
        
        # 必填字段验证
        required_fields = {
            'name': '姓名',
            'id_card': '身份证号',
            'phone': '手机号',
            'email': '邮箱'
        }
        
        for field, field_name in required_fields.items():
            if not data.get(field) or not str(data.get(field)).strip():
                return jsonify({
                    'success': False,
                    'message': f'{field_name}不能为空'
                }), 400
        
        # 数据格式验证
        if not validate_id_card(data['id_card']):
            return jsonify({
                'success': False,
                'message': '身份证号格式不正确'
            }), 400
        
        if not validate_phone(data['phone']):
            return jsonify({
                'success': False,
                'message': '手机号格式不正确'
            }), 400
        
        if not validate_email(data['email']):
            return jsonify({
                'success': False,
                'message': '邮箱格式不正确'
            }), 400
        
        # 检查身份证号是否已存在
        existing_employee = Employee.query.filter_by(id_card=data['id_card']).first()
        if existing_employee:
            return jsonify({
                'success': False,
                'message': '该身份证号已存在记录'
            }), 400
        
        # 检查手机号是否已存在
        existing_phone = Employee.query.filter_by(phone=data['phone']).first()
        if existing_phone:
            return jsonify({
                'success': False,
                'message': '该手机号已存在记录'
            }), 400
        
        # 检查邮箱是否已存在
        existing_email = Employee.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({
                'success': False,
                'message': '该邮箱已存在记录'
            }), 400
        
        # 处理出生日期
        birth_date = None
        if data.get('birth_date'):
            try:
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '出生日期格式不正确，请使用YYYY-MM-DD格式'
                }), 400
        
        # 验证性别
        if data.get('gender') and data['gender'] not in ['男', '女']:
            return jsonify({
                'success': False,
                'message': '性别只能是"男"或"女"'
            }), 400
        
        # 验证学历
        valid_educations = ['小学', '初中', '高中', '中专', '大专', '本科', '硕士', '博士']
        if data.get('education') and data['education'] not in valid_educations:
            return jsonify({
                'success': False,
                'message': f'学历必须是以下之一：{", ".join(valid_educations)}'
            }), 400
        
        # 创建员工记录
        employee = Employee(
            name=data['name'].strip(),
            id_card=data['id_card'].strip(),
            phone=data['phone'].strip(),
            email=data['email'].strip(),
            gender=data.get('gender'),
            birth_date=birth_date,
            address=data.get('address', '').strip() if data.get('address') else None,
            emergency_contact=data.get('emergency_contact', '').strip() if data.get('emergency_contact') else None,
            emergency_phone=data.get('emergency_phone', '').strip() if data.get('emergency_phone') else None,
            education=data.get('education'),
            major=data.get('major', '').strip() if data.get('major') else None,
            work_experience=data.get('work_experience', '').strip() if data.get('work_experience') else None,
            skills=data.get('skills', '').strip() if data.get('skills') else None,
            employment_status='储备'  # 默认为储备状态
        )
        
        db.session.add(employee)
        db.session.commit()
        
        # 记录成功提交
        record_submission_attempt(ip, data)
        
        return jsonify({
            'success': True,
            'message': '应聘信息提交成功！我们会尽快与您联系。',
            'data': {
                'employee_id': employee.id,
                'name': employee.name,
                'submission_time': employee.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # 即使失败也记录提交尝试（防止恶意重试）
        record_submission_attempt(ip, data if 'data' in locals() else None)
        
        return jsonify({
            'success': False,
            'message': '提交失败，请稍后重试'
        }), 500

@application_bp.route('/application/check-duplicate', methods=['POST'])
def check_duplicate():
    """检查重复信息（身份证号、手机号、邮箱）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
        
        result = {
            'success': True,
            'duplicates': {}
        }
        
        # 检查身份证号
        if data.get('id_card'):
            existing = Employee.query.filter_by(id_card=data['id_card']).first()
            if existing:
                result['duplicates']['id_card'] = '该身份证号已存在记录'
        
        # 检查手机号
        if data.get('phone'):
            existing = Employee.query.filter_by(phone=data['phone']).first()
            if existing:
                result['duplicates']['phone'] = '该手机号已存在记录'
        
        # 检查邮箱
        if data.get('email'):
            existing = Employee.query.filter_by(email=data['email']).first()
            if existing:
                result['duplicates']['email'] = '该邮箱已存在记录'
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '检查失败，请稍后重试'
        }), 500

@application_bp.route('/application/validate', methods=['POST'])
def validate_fields():
    """验证字段格式"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
        
        result = {
            'success': True,
            'errors': {}
        }
        
        # 验证身份证号
        if data.get('id_card'):
            if not validate_id_card(data['id_card']):
                result['errors']['id_card'] = '身份证号格式不正确'
        
        # 验证手机号
        if data.get('phone'):
            if not validate_phone(data['phone']):
                result['errors']['phone'] = '手机号格式不正确'
        
        # 验证邮箱
        if data.get('email'):
            if not validate_email(data['email']):
                result['errors']['email'] = '邮箱格式不正确'
        
        # 验证出生日期
        if data.get('birth_date'):
            try:
                datetime.strptime(data['birth_date'], '%Y-%m-%d')
            except ValueError:
                result['errors']['birth_date'] = '出生日期格式不正确，请使用YYYY-MM-DD格式'
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '验证失败，请稍后重试'
        }), 500