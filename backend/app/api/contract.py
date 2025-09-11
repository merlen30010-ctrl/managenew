from flask import Blueprint, jsonify, request, g
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
        'status': contract.status,
        'is_tax_inclusive': contract.is_tax_inclusive,
        'is_invoice_received': contract.is_invoice_received
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
        'status': contract.status,
        'is_tax_inclusive': contract.is_tax_inclusive,
        'is_invoice_received': contract.is_invoice_received,
        'operation_logs': contract.operation_logs_list
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
        status=data.get('status', '草稿'),
        is_tax_inclusive=bool(data.get('is_tax_inclusive', False)),
        is_invoice_received=bool(data.get('is_invoice_received', False))
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
    # 先flush拿到ID
    db.session.flush()
    # 写入创建日志
    actor_id = getattr(getattr(g, 'current_user', None), 'id', None)
    contract.append_log('create', actor_id=actor_id, details={
        'contract_id': contract.id,
        'contract_number': contract.contract_number,
        'status': contract.status,
        'is_tax_inclusive': contract.is_tax_inclusive,
        'is_invoice_received': contract.is_invoice_received
    })
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
        'status': contract.status,
        'is_tax_inclusive': contract.is_tax_inclusive,
        'is_invoice_received': contract.is_invoice_received
    }), 201

@api_contract_bp.route('/contracts/<int:contract_id>', methods=['PUT'])
@api_login_required
@permission_required('contract_update')
def update_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400

    user = getattr(g, 'current_user', None)
    is_super = bool(getattr(user, 'is_superuser', False))

    # 合同归档后对非超级管理员只读
    if contract.status == '合同归档' and not is_super:
        return jsonify({'error': '合同已归档，只有超级管理员可以编辑'}), 403

    changed_fields = {}
    
    # 更新合同信息
    if 'contract_type' in data and data['contract_type'] != contract.contract_type:
        old = contract.contract_type
        contract.contract_type = data['contract_type']
        changed_fields['contract_type'] = {'from': old, 'to': data['contract_type']}
    
    if 'contract_number' in data and data['contract_number'] != contract.contract_number:
        # 检查合同编号是否已存在
        existing_contract = Contract.query.filter_by(contract_number=data['contract_number']).first()
        if existing_contract and existing_contract.id != contract_id:
            return jsonify({'error': '合同编号已存在'}), 400
        old = contract.contract_number
        contract.contract_number = data['contract_number']
        changed_fields['contract_number'] = {'from': old, 'to': data['contract_number']}
    
    if 'customer_id' in data and data['customer_id'] != contract.customer_id:
        changed_fields['customer_id'] = {'from': contract.customer_id, 'to': data['customer_id']}
        contract.customer_id = data['customer_id']
    
    if 'material_id' in data and data['material_id'] != contract.material_id:
        changed_fields['material_id'] = {'from': contract.material_id, 'to': data['material_id']}
        contract.material_id = data['material_id']
    
    if 'factory_id' in data and data['factory_id'] != contract.factory_id:
        changed_fields['factory_id'] = {'from': contract.factory_id, 'to': data['factory_id']}
        contract.factory_id = data['factory_id']
    
    if 'responsible_id' in data and data['responsible_id'] != contract.responsible_id:
        changed_fields['responsible_id'] = {'from': contract.responsible_id, 'to': data['responsible_id']}
        contract.responsible_id = data['responsible_id']
    
    if 'tax_rate' in data and data['tax_rate'] != contract.tax_rate:
        changed_fields['tax_rate'] = {'from': contract.tax_rate, 'to': data['tax_rate']}
        contract.tax_rate = data['tax_rate']
    
    if 'pricing_method' in data and data['pricing_method'] != contract.pricing_method:
        changed_fields['pricing_method'] = {'from': contract.pricing_method, 'to': data['pricing_method']}
        contract.pricing_method = data['pricing_method']
    
    if 'coefficient' in data and data['coefficient'] != contract.coefficient:
        changed_fields['coefficient'] = {'from': contract.coefficient, 'to': data['coefficient']}
        contract.coefficient = data['coefficient']

    # 布尔字段写入限制：非超管禁止修改
    if 'is_tax_inclusive' in data:
        new_val = bool(data['is_tax_inclusive'])
        if new_val != contract.is_tax_inclusive and not is_super:
            return jsonify({'error': '是否含税字段禁止修改（仅超级管理员可修改）'}), 403
        if new_val != contract.is_tax_inclusive:
            changed_fields['is_tax_inclusive'] = {'from': contract.is_tax_inclusive, 'to': new_val}
            contract.is_tax_inclusive = new_val

    if 'is_invoice_received' in data:
        new_val = bool(data['is_invoice_received'])
        if new_val != contract.is_invoice_received and not is_super:
            return jsonify({'error': '是否收到发票字段禁止修改（仅超级管理员可修改）'}), 403
        if new_val != contract.is_invoice_received:
            changed_fields['is_invoice_received'] = {'from': contract.is_invoice_received, 'to': new_val}
            contract.is_invoice_received = new_val

    # 处理日期字段
    if 'sign_date' in data:
        if data['sign_date']:
            try:
                new_date = datetime.strptime(data['sign_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '签订日期格式不正确，应为YYYY-MM-DD'}), 400
            if contract.sign_date != new_date:
                changed_fields['sign_date'] = {'from': contract.sign_date.isoformat() if contract.sign_date else None, 'to': new_date.isoformat()}
                contract.sign_date = new_date
        else:
            if contract.sign_date is not None:
                changed_fields['sign_date'] = {'from': contract.sign_date.isoformat(), 'to': None}
            contract.sign_date = None
    
    if 'expiry_date' in data:
        if data['expiry_date']:
            try:
                new_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '到期日期格式不正确，应为YYYY-MM-DD'}), 400
            if contract.expiry_date != new_date:
                changed_fields['expiry_date'] = {'from': contract.expiry_date.isoformat() if contract.expiry_date else None, 'to': new_date.isoformat()}
                contract.expiry_date = new_date
        else:
            if contract.expiry_date is not None:
                changed_fields['expiry_date'] = {'from': contract.expiry_date.isoformat(), 'to': None}
            contract.expiry_date = None

    # 状态变更与归档限制
    if 'status' in data and data['status'] != contract.status:
        new_status = data['status']
        if new_status == '合同归档' or contract.status == '合同归档':
            if not is_super:
                return jsonify({'error': '归档/取消归档操作仅限超级管理员'}), 403
        old_status = contract.status
        contract.status = new_status
        # 单独记录状态变更日志
        actor_id = getattr(user, 'id', None)
        contract.append_log('status_change', actor_id=actor_id, details={'from': old_status, 'to': new_status})
        # 不把status纳入一般字段变更日志
        if 'status' in changed_fields:
            changed_fields.pop('status')

    # 写入字段更新日志（如果有其它字段变更）
    if changed_fields:
        actor_id = getattr(user, 'id', None)
        contract.append_log('update', actor_id=actor_id, details={'changes': changed_fields})
    
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
        'status': contract.status,
        'is_tax_inclusive': contract.is_tax_inclusive,
        'is_invoice_received': contract.is_invoice_received
    })

@api_contract_bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
@api_login_required
@permission_required('contract_delete')
def delete_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    user = getattr(g, 'current_user', None)
    is_super = bool(getattr(user, 'is_superuser', False))
    if contract.status == '合同归档' and not is_super:
        return jsonify({'error': '合同已归档，只有超级管理员可以删除合同'}), 403
    db.session.delete(contract)
    db.session.commit()
    return jsonify({'message': '合同删除成功'})