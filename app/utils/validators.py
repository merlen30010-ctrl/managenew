import re

def validate_phone(phone):
    """验证电话号码"""
    if not phone:
        return False
    # 简单的电话号码验证
    pattern = r'^1[3-9]\d{9}$|^0\d{2,3}-?\d{7,8}$'
    return re.match(pattern, phone) is not None

def validate_email(email):
    """验证邮箱"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if not password or len(password) < 6:
        return False
    # 至少包含一个字母和一个数字
    if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
        return False
    return True

def validate_required_fields(data, required_fields):
    """验证必填字段"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    return missing_fields