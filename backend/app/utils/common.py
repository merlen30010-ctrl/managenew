def format_date(date):
    """格式化日期"""
    if date:
        return date.strftime('%Y-%m-%d')
    return ''

def format_datetime(datetime):
    """格式化日期时间"""
    if datetime:
        return datetime.strftime('%Y-%m-%d %H:%M:%S')
    return ''

def generate_contract_filename(customer_name, material_name, timestamp):
    """生成合同文件名"""
    return f"{customer_name}_{material_name}_{timestamp}"