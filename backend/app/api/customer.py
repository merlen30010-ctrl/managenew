from flask import Blueprint, jsonify, request
from app import db
from app.models.customer import Customer
from app.api.decorators import api_login_required, permission_required

# 创建客户API蓝图
api_customer_bp = Blueprint('api_customer', __name__, url_prefix='/api')

@api_customer_bp.route('/customers', methods=['GET'])
@api_login_required
@permission_required('customer_read')
def get_customers():
    customers = Customer.query.all()
    return jsonify([{
        'id': customer.id,
        'name': customer.name,
        'code': customer.code,
        'full_name': customer.full_name,
        'customer_type': customer.customer_type,
        'phone': customer.phone,
        'address': customer.address
    } for customer in customers])

@api_customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
@api_login_required
@permission_required('customer_read')
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'code': customer.code,
        'full_name': customer.full_name,
        'customer_type': customer.customer_type,
        'phone': customer.phone,
        'address': customer.address
    })

@api_customer_bp.route('/customers', methods=['POST'])
@api_login_required
@permission_required('customer_create')
def create_customer():
    data = request.get_json()
    
    # 检查必填字段
    if not data or not data.get('name') or not data.get('code'):
        return jsonify({'error': '客户名称和代码是必填字段'}), 400
    
    # 检查客户代码是否已存在
    if Customer.query.filter_by(code=data['code']).first():
        return jsonify({'error': '客户代码已存在'}), 400
    
    # 创建新客户
    customer = Customer(
        name=data['name'],
        code=data['code'],
        full_name=data.get('full_name', ''),
        customer_type=data.get('customer_type', '其他'),
        phone=data.get('phone', ''),
        address=data.get('address', '')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'code': customer.code,
        'full_name': customer.full_name,
        'customer_type': customer.customer_type,
        'phone': customer.phone,
        'address': customer.address
    }), 201

@api_customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@api_login_required
@permission_required('customer_update')
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新客户信息
    if 'name' in data:
        customer.name = data['name']
    
    if 'code' in data:
        # 检查客户代码是否已存在
        existing_customer = Customer.query.filter_by(code=data['code']).first()
        if existing_customer and existing_customer.id != customer_id:
            return jsonify({'error': '客户代码已存在'}), 400
        customer.code = data['code']
    
    if 'full_name' in data:
        customer.full_name = data['full_name']
    
    if 'customer_type' in data:
        customer.customer_type = data['customer_type']
    
    if 'phone' in data:
        customer.phone = data['phone']
    
    if 'address' in data:
        customer.address = data['address']
    
    db.session.commit()
    
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'code': customer.code,
        'full_name': customer.full_name,
        'customer_type': customer.customer_type,
        'phone': customer.phone,
        'address': customer.address
    })

@api_customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@api_login_required
@permission_required('customer_delete')
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': '客户删除成功'})