from flask import Blueprint, jsonify, request
from app import db
from app.models.contract import Contract
from app.api.decorators import api_login_required, permission_required
from datetime import datetime

# 创建合同API蓝图
api_contract_bp = Blueprint('api_contract', __name__, url_prefix='/api')

@api_contract_bp.route('/contracts', methods=['GET'])
@api_login_required
@permission_required('contract_read')
def get_contracts():
    contracts = Contract.query.all()
    return jsonify([{
        'id': contract.id,
        'contract_type': contract.contract_type,
        'contract_number': contract.contract_number,
        'customer_id': contract.customer_id,
        'material_id': contract.material_id,
        'factory_id': contract.factory_id,
        'responsible_id': contract.responsible_id,
        'sign_date': contract.sign_date.isoformat() if contract.sign_date else None,
        'expiry_date': contract.expiry_date.isoformat() if contract.expiry_date else None,
        'tax_rate': contract.tax_rate,
        'pricing_method': contract.pricing_method,
        'coefficient': contract.coefficient,
        'status': contract.status
    } for contract in contracts])

@api_contract_bp.route('/contracts/<int:contract_id>', methods=['GET'])
@api_login_required
@permission_required('contract_read')
def get_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return jsonify({
        'id': contract.id,
        'contract_type': contract.contract_type,
        'contract_number': contract.contract_number,
        'customer_id': contract.customer_id,
        'material_id': contract.material_id,
        'factory_id': contract.factory_id,
        'responsible_id': contract.responsible_id,
        'sign_date': contract.sign_date.isoformat() if contract.sign_date else None,
        'expiry_date': contract.expiry_date.isoformat() if contract.expiry_date else None,
        'tax_rate': contract.tax_rate,
        'pricing_method': contract.pricing_method,
        'coefficient': contract.coefficient,
        'status': contract.status
    })

@api_contract_bp.route('/contracts', methods=['POST'])
@api_login_required
@permission_required('contract_create')
def create_contract():
    data = request.get_json()
    
    # 检查必填字段
    if not data or not data.get('contract_type') or not data.get('contract_number'):
        return jsonify({'error': '合同类型和合同编号是必填字段'}), 400
    
    # 检查合同编号是否已存在
    if Contract.query.filter_by(contract_number=data['contract_number']).first():
        return jsonify({'error': '合同编号已存在'}), 400
    
    # 创建新合同
    contract = Contract(
        contract_type=data['contract_type'],
        contract_number=data['contract_number'],
        customer_id=data.get('customer_id'),
        material_id=data.get('material_id'),
        factory_id=data.get('factory_id'),
        responsible_id=data.get('responsible_id'),
        tax_rate=data.get('tax_rate', 0),
        pricing_method=data.get('pricing_method'),
        coefficient=data.get('coefficient'),
        status=data.get('status', '执行')
    )
    
    # 处理日期字段
    if data.get('sign_date'):
        try:
            contract.sign_date = datetime.strptime(data['sign_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '签订日期格式不正确，应为YYYY-MM-DD'}), 400
    
    if data.get('expiry_date'):
        try:
            contract.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '到期日期格式不正确，应为YYYY-MM-DD'}), 400
    
    db.session.add(contract)
    db.session.commit()
    
    return jsonify({
        'id': contract.id,
        'contract_type': contract.contract_type,
        'contract_number': contract.contract_number,
        'customer_id': contract.customer_id,
        'material_id': contract.material_id,
        'factory_id': contract.factory_id,
        'responsible_id': contract.responsible_id,
        'sign_date': contract.sign_date.isoformat() if contract.sign_date else None,
        'expiry_date': contract.expiry_date.isoformat() if contract.expiry_date else None,
        'tax_rate': contract.tax_rate,
        'pricing_method': contract.pricing_method,
        'coefficient': contract.coefficient,
        'status': contract.status
    }), 201

@api_contract_bp.route('/contracts/<int:contract_id>', methods=['PUT'])
@api_login_required
@permission_required('contract_update')
def update_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新合同信息
    if 'contract_type' in data:
        contract.contract_type = data['contract_type']
    
    if 'contract_number' in data:
        # 检查合同编号是否已存在
        existing_contract = Contract.query.filter_by(contract_number=data['contract_number']).first()
        if existing_contract and existing_contract.id != contract_id:
            return jsonify({'error': '合同编号已存在'}), 400
        contract.contract_number = data['contract_number']
    
    if 'customer_id' in data:
        contract.customer_id = data['customer_id']
    
    if 'material_id' in data:
        contract.material_id = data['material_id']
    
    if 'factory_id' in data:
        contract.factory_id = data['factory_id']
    
    if 'responsible_id' in data:
        contract.responsible_id = data['responsible_id']
    
    if 'tax_rate' in data:
        contract.tax_rate = data['tax_rate']
    
    if 'pricing_method' in data:
        contract.pricing_method = data['pricing_method']
    
    if 'coefficient' in data:
        contract.coefficient = data['coefficient']
    
    if 'status' in data:
        contract.status = data['status']
    
    # 处理日期字段
    if 'sign_date' in data:
        if data['sign_date']:
            try:
                contract.sign_date = datetime.strptime(data['sign_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '签订日期格式不正确，应为YYYY-MM-DD'}), 400
        else:
            contract.sign_date = None
    
    if 'expiry_date' in data:
        if data['expiry_date']:
            try:
                contract.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '到期日期格式不正确，应为YYYY-MM-DD'}), 400
        else:
            contract.expiry_date = None
    
    db.session.commit()
    
    return jsonify({
        'id': contract.id,
        'contract_type': contract.contract_type,
        'contract_number': contract.contract_number,
        'customer_id': contract.customer_id,
        'material_id': contract.material_id,
        'factory_id': contract.factory_id,
        'responsible_id': contract.responsible_id,
        'sign_date': contract.sign_date.isoformat() if contract.sign_date else None,
        'expiry_date': contract.expiry_date.isoformat() if contract.expiry_date else None,
        'tax_rate': contract.tax_rate,
        'pricing_method': contract.pricing_method,
        'coefficient': contract.coefficient,
        'status': contract.status
    })

@api_contract_bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
@api_login_required
@permission_required('contract_delete')
def delete_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    db.session.delete(contract)
    db.session.commit()
    return jsonify({'message': '合同删除成功'})