from flask import Blueprint, jsonify, request
from app import db
from app.models.material_transaction import MaterialTransaction
from datetime import datetime
from app.api.decorators import api_login_required, permission_required

# 创建物料交易API蓝图
api_material_transaction_bp = Blueprint('api_material_transaction', __name__, url_prefix='/api')

@api_material_transaction_bp.route('/material-transactions', methods=['GET'])
@api_login_required
@permission_required('material_transaction_read')
def get_material_transactions():
    """获取物料进出厂记录列表"""
    # 根据用户权限获取数据
    from flask_login import current_user
    if current_user.has_permission_name('material_transaction_read_all'):
        # 管理员可以看到所有数据
        transactions = MaterialTransaction.query.all()
    else:
        # 其他用户只能看到自己分厂的数据
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        transactions = MaterialTransaction.query.filter(MaterialTransaction.factory_id.in_(factory_ids)).all()
    
    return jsonify([{
        'id': transaction.id,
        'date': transaction.date.isoformat() if transaction.date else None,
        'customer': transaction.customer,
        'material_name': transaction.material_name,
        'factory_id': transaction.factory_id,
        'contract_number': transaction.contract_number,
        'transaction_type': transaction.transaction_type,
        'packaging': transaction.packaging,
        'vehicle_number': transaction.vehicle_number,
        'shipped_quantity': transaction.shipped_quantity,
        'received_quantity': transaction.received_quantity,
        'water_content': transaction.water_content,
        'zinc_content': transaction.zinc_content,
        'lead_content': transaction.lead_content,
        'chlorine_content': transaction.chlorine_content,
        'fluorine_content': transaction.fluorine_content,
        'remarks': transaction.remarks,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
    } for transaction in transactions])

@api_material_transaction_bp.route('/material-transactions/<int:transaction_id>', methods=['GET'])
@api_login_required
@permission_required('material_transaction_read')
def get_material_transaction(transaction_id):
    """获取单个物料进出厂记录"""
    from flask_login import current_user
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    
    # 检查权限
    if not current_user.has_permission_name('material_transaction_read_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限查看此记录'}), 403
    
    return jsonify({
        'id': transaction.id,
        'date': transaction.date.isoformat() if transaction.date else None,
        'customer': transaction.customer,
        'material_name': transaction.material_name,
        'factory_id': transaction.factory_id,
        'contract_number': transaction.contract_number,
        'transaction_type': transaction.transaction_type,
        'packaging': transaction.packaging,
        'vehicle_number': transaction.vehicle_number,
        'shipped_quantity': transaction.shipped_quantity,
        'received_quantity': transaction.received_quantity,
        'water_content': transaction.water_content,
        'zinc_content': transaction.zinc_content,
        'lead_content': transaction.lead_content,
        'chlorine_content': transaction.chlorine_content,
        'fluorine_content': transaction.fluorine_content,
        'remarks': transaction.remarks,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
    })

@api_material_transaction_bp.route('/material-transactions', methods=['POST'])
@api_login_required
@permission_required('material_transaction_create')
def create_material_transaction():
    """创建物料进出厂记录"""
    from flask_login import current_user
    data = request.get_json()
    
    if not data or not data.get('date') or not data.get('customer') or not data.get('material_name') or not data.get('factory_id'):
        return jsonify({'error': '日期、客户、物料名称和分厂是必填字段'}), 400
    
    # 检查权限
    if not current_user.has_permission_name('material_transaction_update_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if int(data['factory_id']) not in factory_ids:
            return jsonify({'error': '您没有权限在此分厂创建记录'}), 403
    
    # 处理日期
    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式不正确，应为YYYY-MM-DD'}), 400
    
    # 创建记录
    transaction = MaterialTransaction(
        date=date_obj,
        customer=data['customer'],
        material_name=data['material_name'],
        factory_id=data['factory_id'],
        contract_number=data.get('contract_number', ''),
        transaction_type=data.get('transaction_type', ''),
        packaging=data.get('packaging', ''),
        vehicle_number=data.get('vehicle_number', ''),
        shipped_quantity=float(data.get('shipped_quantity', 0) or 0),
        received_quantity=float(data.get('received_quantity', 0) or 0),
        water_content=float(data.get('water_content', 0) or 0) if data.get('water_content') is not None else None,
        zinc_content=float(data.get('zinc_content', 0) or 0) if data.get('zinc_content') is not None else None,
        lead_content=float(data.get('lead_content', 0) or 0) if data.get('lead_content') is not None else None,
        chlorine_content=float(data.get('chlorine_content', 0) or 0) if data.get('chlorine_content') is not None else None,
        fluorine_content=float(data.get('fluorine_content', 0) or 0) if data.get('fluorine_content') is not None else None,
        remarks=data.get('remarks', '')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'id': transaction.id,
        'date': transaction.date.isoformat() if transaction.date else None,
        'customer': transaction.customer,
        'material_name': transaction.material_name,
        'factory_id': transaction.factory_id,
        'contract_number': transaction.contract_number,
        'transaction_type': transaction.transaction_type,
        'packaging': transaction.packaging,
        'vehicle_number': transaction.vehicle_number,
        'shipped_quantity': transaction.shipped_quantity,
        'received_quantity': transaction.received_quantity,
        'water_content': transaction.water_content,
        'zinc_content': transaction.zinc_content,
        'lead_content': transaction.lead_content,
        'chlorine_content': transaction.chlorine_content,
        'fluorine_content': transaction.fluorine_content,
        'remarks': transaction.remarks,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
    }), 201

@api_material_transaction_bp.route('/material-transactions/<int:transaction_id>', methods=['PUT'])
@api_login_required
@permission_required('material_transaction_update')
def update_material_transaction(transaction_id):
    """更新物料进出厂记录"""
    from flask_login import current_user
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 检查权限
    if not current_user.has_permission_name('material_transaction_update_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限更新此记录'}), 403
    
    # 更新记录信息
    if 'date' in data:
        try:
            transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式不正确，应为YYYY-MM-DD'}), 400
    
    if 'customer' in data:
        transaction.customer = data['customer']
    
    if 'material_name' in data:
        transaction.material_name = data['material_name']
    
    if 'factory_id' in data:
        # 检查权限
        if not current_user.has_permission_name('material_transaction_create_all'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if int(data['factory_id']) not in factory_ids:
                return jsonify({'error': '您没有权限将记录转移到此分厂'}), 403
        transaction.factory_id = data['factory_id']
    
    if 'contract_number' in data:
        transaction.contract_number = data['contract_number']
    
    if 'transaction_type' in data:
        transaction.transaction_type = data['transaction_type']
    
    if 'packaging' in data:
        transaction.packaging = data['packaging']
    
    if 'vehicle_number' in data:
        transaction.vehicle_number = data['vehicle_number']
    
    if 'shipped_quantity' in data:
        transaction.shipped_quantity = float(data['shipped_quantity'] or 0)
    
    if 'received_quantity' in data:
        transaction.received_quantity = float(data['received_quantity'] or 0)
    
    if 'water_content' in data:
        transaction.water_content = float(data['water_content'] or 0) if data['water_content'] is not None else None
    
    if 'zinc_content' in data:
        transaction.zinc_content = float(data['zinc_content'] or 0) if data['zinc_content'] is not None else None
    
    if 'lead_content' in data:
        transaction.lead_content = float(data['lead_content'] or 0) if data['lead_content'] is not None else None
    
    if 'chlorine_content' in data:
        transaction.chlorine_content = float(data['chlorine_content'] or 0) if data['chlorine_content'] is not None else None
    
    if 'fluorine_content' in data:
        transaction.fluorine_content = float(data['fluorine_content'] or 0) if data['fluorine_content'] is not None else None
    
    if 'remarks' in data:
        transaction.remarks = data['remarks']
    
    db.session.commit()
    
    return jsonify({
        'id': transaction.id,
        'date': transaction.date.isoformat() if transaction.date else None,
        'customer': transaction.customer,
        'material_name': transaction.material_name,
        'factory_id': transaction.factory_id,
        'contract_number': transaction.contract_number,
        'transaction_type': transaction.transaction_type,
        'packaging': transaction.packaging,
        'vehicle_number': transaction.vehicle_number,
        'shipped_quantity': transaction.shipped_quantity,
        'received_quantity': transaction.received_quantity,
        'water_content': transaction.water_content,
        'zinc_content': transaction.zinc_content,
        'lead_content': transaction.lead_content,
        'chlorine_content': transaction.chlorine_content,
        'fluorine_content': transaction.fluorine_content,
        'remarks': transaction.remarks,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
    })

@api_material_transaction_bp.route('/material-transactions/<int:transaction_id>', methods=['DELETE'])
@api_login_required
@permission_required('material_transaction_delete')
def delete_material_transaction(transaction_id):
    """删除物料进出厂记录"""
    from flask_login import current_user
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    
    # 检查权限
    if not current_user.has_permission_name('material_transaction_update_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限删除此记录'}), 403
    
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': '物料进出厂记录删除成功'})

@api_material_transaction_bp.route('/material-transactions/<int:transaction_id>/status', methods=['PUT'])
@api_login_required
@permission_required('material_transaction_status_manage')
def update_material_transaction_status(transaction_id):
    """更新物料进出厂记录状态"""
    from flask_login import current_user
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    data = request.get_json()
    
    # 检查权限
    if not current_user.has_permission_name('material_transaction_delete_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限更新此记录状态'}), 403
    
    # 更新状态字段
    if 'status' in data:
        transaction.status = data['status']
    
    if 'weighing_completed' in data:
        transaction.weighing_completed = data['weighing_completed']
    
    if 'assaying_completed' in data:
        transaction.assaying_completed = data['assaying_completed']
    
    if 'completed_by' in data:
        transaction.completed_by = data['completed_by']
    
    db.session.commit()
    
    return jsonify({
        'id': transaction.id,
        'date': transaction.date.isoformat() if transaction.date else None,
        'customer': transaction.customer,
        'material_name': transaction.material_name,
        'factory_id': transaction.factory_id,
        'contract_number': transaction.contract_number,
        'transaction_type': transaction.transaction_type,
        'packaging': transaction.packaging,
        'vehicle_number': transaction.vehicle_number,
        'shipped_quantity': transaction.shipped_quantity,
        'received_quantity': transaction.received_quantity,
        'water_content': transaction.water_content,
        'zinc_content': transaction.zinc_content,
        'lead_content': transaction.lead_content,
        'chlorine_content': transaction.chlorine_content,
        'fluorine_content': transaction.fluorine_content,
        'remarks': transaction.remarks,
        'status': transaction.status,
        'weighing_completed': transaction.weighing_completed,
        'assaying_completed': transaction.assaying_completed,
        'created_by': transaction.created_by,
        'completed_by': transaction.completed_by,
        'weighing_by': transaction.weighing_by,
        'assaying_by': transaction.assaying_by,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
    })

@api_material_transaction_bp.route('/material-transactions/<int:transaction_id>/assign', methods=['PUT'])
@api_login_required
@permission_required('material_transaction_status_manage')
def assign_material_transaction_operators(transaction_id):
    """分配物料进出厂记录操作人员"""
    from flask_login import current_user
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    data = request.get_json()
    
    # 检查权限
    if not current_user.has_permission_name('material_transaction_delete_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限分配此记录的操作人员'}), 403
    
    # 分配操作人员
    if 'weighing_by' in data:
        transaction.weighing_by = data['weighing_by']
    
    if 'assaying_by' in data:
        transaction.assaying_by = data['assaying_by']
    
    db.session.commit()
    
    return jsonify({
        'id': transaction.id,
        'date': transaction.date.isoformat() if transaction.date else None,
        'customer': transaction.customer,
        'material_name': transaction.material_name,
        'factory_id': transaction.factory_id,
        'contract_number': transaction.contract_number,
        'transaction_type': transaction.transaction_type,
        'packaging': transaction.packaging,
        'vehicle_number': transaction.vehicle_number,
        'shipped_quantity': transaction.shipped_quantity,
        'received_quantity': transaction.received_quantity,
        'water_content': transaction.water_content,
        'zinc_content': transaction.zinc_content,
        'lead_content': transaction.lead_content,
        'chlorine_content': transaction.chlorine_content,
        'fluorine_content': transaction.fluorine_content,
        'remarks': transaction.remarks,
        'status': transaction.status,
        'weighing_completed': transaction.weighing_completed,
        'assaying_completed': transaction.assaying_completed,
        'created_by': transaction.created_by,
        'completed_by': transaction.completed_by,
        'weighing_by': transaction.weighing_by,
        'assaying_by': transaction.assaying_by,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
    })