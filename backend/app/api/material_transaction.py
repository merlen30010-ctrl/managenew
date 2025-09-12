from flask import Blueprint, jsonify, request, send_file
from app import db
from app.models.material_transaction import MaterialTransaction
from app.models.attachment import Attachment
from datetime import datetime
from app.api.decorators import api_login_required, permission_required

# 创建物料交易API蓝图
api_material_transaction_bp = Blueprint('api_material_transaction', __name__, url_prefix='/api')

# 导入文件处理相关模块
import os
import logging
from werkzeug.utils import secure_filename
from flask import current_app
from flask_login import current_user

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建上传目录函数
def create_upload_directory(related_type):
    """
    创建上传目录
    """
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), related_type, datetime.now().strftime('%Y%m'))
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

# 生成文件名函数
def generate_filename(original_name, related_type, related_id):
    """
    生成文件存储名
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    name, ext = os.path.splitext(original_name)
    return f"{related_type}_{related_id}_{timestamp}{ext}"

@api_material_transaction_bp.route('/material-transactions', methods=['GET'])
@api_login_required
@permission_required('material_transaction_read')
def get_material_transactions():
    """获取物料进出厂记录列表"""
    # 根据用户权限获取数据
    from flask_login import current_user
    if current_user.has_permission('material_transaction_read_all'):
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
        'status': transaction.status,
        'editable': transaction.editable,
        'driver_name': transaction.driver_name,
        'driver_phone': transaction.driver_phone,
        'driver_id_card': transaction.driver_id_card,
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
    if not current_user.has_permission('material_transaction_read_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限查看此记录'}), 403
            
    # 获取关联的附件列表
    attachments = Attachment.query.filter_by(
        related_type='material_transaction',
        related_id=transaction_id
    ).all()
    
    attachment_list = [{
        'id': attachment.id,
        'file_path': attachment.file_path,
        'original_name': attachment.original_name,
        'file_type': attachment.file_type,
        'file_size': attachment.file_size,
        'description': attachment.description,
        'created_at': attachment.created_at.isoformat() if attachment.created_at else None
    } for attachment in attachments]
    
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
        'editable': transaction.editable,
        'driver_name': transaction.driver_name,
        'driver_phone': transaction.driver_phone,
        'driver_id_card': transaction.driver_id_card,
        'loading_time': transaction.loading_time.isoformat() if transaction.loading_time else None,
        'arrival_time': transaction.arrival_time.isoformat() if transaction.arrival_time else None,
        'storage_time': transaction.storage_time.isoformat() if transaction.storage_time else None,
        'usage_time': transaction.usage_time.isoformat() if transaction.usage_time else None,
        'created_by': transaction.created_by,
        'loading_by': transaction.loading_by,
        'arrival_by': transaction.arrival_by,
        'storage_by': transaction.storage_by,
        'usage_by': transaction.usage_by,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'attachments': attachment_list,
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
    if not current_user.has_permission('material_transaction_update_all'):
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
        remarks=data.get('remarks', ''),
        status='loading',  # 默认状态为装车
        loading_time=datetime.now(),  # 设置装车时间
        loading_by=current_user.id,  # 设置装车操作人
        created_by=current_user.id,  # 设置创建人
        # 司机信息
        driver_name=data.get('driver_name', ''),
        driver_phone=data.get('driver_phone', ''),
        driver_id_card=data.get('driver_id_card', '')
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
        'status': transaction.status,
        'driver_name': transaction.driver_name,
        'driver_phone': transaction.driver_phone,
        'driver_id_card': transaction.driver_id_card,
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
    
    # 检查记录是否可编辑
    if not transaction.editable:
        return jsonify({'error': '此记录当前状态不可编辑'}), 403
    
    # 检查权限
    if not current_user.has_permission('material_transaction_update_all'):
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
        if not current_user.has_permission('material_transaction_create_all'):
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
    if not current_user.has_permission('material_transaction_update_all'):
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
    
    if not data or 'status' not in data:
        return jsonify({'error': '没有提供状态数据'}), 400
    
    new_status = data['status']
    
    # 验证状态值
    valid_statuses = ['loading', 'arrived', 'stored', 'used']
    if new_status not in valid_statuses:
        return jsonify({'error': f'无效的状态值，有效值为: {", ".join(valid_statuses)}'}), 400
    
    # 检查权限
    if not current_user.has_permission('material_transaction_status_manage_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限更新此记录的状态'}), 403
    
    # 定义有效的状态转换
    valid_transitions = {
        'loading': ['arrived'],
        'arrived': ['stored'],
        'stored': ['used'],
        'used': []
    }
    
    # 验证状态转换是否有效
    if new_status not in valid_transitions.get(transaction.status, []):
        return jsonify({'error': f'无法从 {transaction.status} 状态转换为 {new_status} 状态'}), 400
    
    # 更新状态和相关字段
    transaction.status = new_status
    
    # 根据新状态更新时间和操作人员字段
    if new_status == 'arrived':
        transaction.arrival_time = datetime.now()
        transaction.arrival_by = current_user.id
    elif new_status == 'stored':
        transaction.storage_time = datetime.now()
        transaction.storage_by = current_user.id
    elif new_status == 'used':
        transaction.usage_time = datetime.now()
        transaction.usage_by = current_user.id
        transaction.editable = False  # 使用后不可编辑
    
    # 更新司机信息（如果提供）
    if 'driver_name' in data:
        transaction.driver_name = data['driver_name']
    if 'driver_phone' in data:
        transaction.driver_phone = data['driver_phone']
    if 'driver_id_card' in data:
        transaction.driver_id_card = data['driver_id_card']
    
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
        'editable': transaction.editable,
        'driver_name': transaction.driver_name,
        'driver_phone': transaction.driver_phone,
        'driver_id_card': transaction.driver_id_card,
        'loading_time': transaction.loading_time.isoformat() if transaction.loading_time else None,
        'arrival_time': transaction.arrival_time.isoformat() if transaction.arrival_time else None,
        'storage_time': transaction.storage_time.isoformat() if transaction.storage_time else None,
        'usage_time': transaction.usage_time.isoformat() if transaction.usage_time else None,
        'created_by': transaction.created_by,
        'loading_by': transaction.loading_by,
        'arrival_by': transaction.arrival_by,
        'storage_by': transaction.storage_by,
        'usage_by': transaction.usage_by,
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
    if not current_user.has_permission('material_transaction_status_manage_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限分配此记录的操作人员'}), 403
    
    # 分配操作人员
    if 'loading_by' in data:
        transaction.loading_by = data['loading_by']
    
    if 'arrival_by' in data:
        transaction.arrival_by = data['arrival_by']
    
    if 'storage_by' in data:
        transaction.storage_by = data['storage_by']
    
    if 'usage_by' in data:
        transaction.usage_by = data['usage_by']
    
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
        'editable': transaction.editable,
        'driver_name': transaction.driver_name,
        'driver_phone': transaction.driver_phone,
        'driver_id_card': transaction.driver_id_card,
        'loading_time': transaction.loading_time.isoformat() if transaction.loading_time else None,
        'arrival_time': transaction.arrival_time.isoformat() if transaction.arrival_time else None,
        'storage_time': transaction.storage_time.isoformat() if transaction.storage_time else None,
        'usage_time': transaction.usage_time.isoformat() if transaction.usage_time else None,
        'created_by': transaction.created_by,
        'loading_by': transaction.loading_by,
        'arrival_by': transaction.arrival_by,
        'storage_by': transaction.storage_by,
        'usage_by': transaction.usage_by,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
    })

@api_material_transaction_bp.route('/material-transactions/<int:transaction_id>/attachments', methods=['POST'])
@api_login_required
@permission_required('material_transaction_update')
def upload_material_transaction_attachment(transaction_id):
    """上传物料进出厂记录附件"""
    from flask_login import current_user
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    
    # 检查权限
    if not current_user.has_permission('material_transaction_update_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限为此记录上传附件'}), 403
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 获取文件描述
    description = request.form.get('description', '')
    
    # 创建上传目录
    upload_dir = create_upload_directory('material_transaction')
    
    # 安全处理文件名并生成存储文件名
    original_name = secure_filename(file.filename)
    filename = generate_filename(original_name, 'material_transaction', transaction_id)
    
    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # 获取文件类型和大小
    file_type = os.path.splitext(original_name)[1].lstrip('.')
    file_size = os.path.getsize(file_path)
    
    # 创建附件记录
    attachment = Attachment(
        related_type='material_transaction',
        related_id=transaction_id,
        file_path=os.path.join('material_transaction', datetime.now().strftime('%Y%m'), filename),
        original_name=original_name,
        file_type=file_type,
        file_size=file_size,
        description=description,
        created_by=current_user.id
    )
    
    db.session.add(attachment)
    db.session.commit()
    
    return jsonify({
        'id': attachment.id,
        'file_path': attachment.file_path,
        'original_name': attachment.original_name,
        'file_type': attachment.file_type,
        'file_size': attachment.file_size,
        'description': attachment.description,
        'created_at': attachment.created_at.isoformat() if attachment.created_at else None
    }), 201

@api_material_transaction_bp.route('/attachments/<int:attachment_id>', methods=['DELETE'])
@api_login_required
@permission_required('material_transaction_update')
def delete_attachment(attachment_id):
    """删除附件"""
    from flask_login import current_user
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # 检查附件类型
    if attachment.related_type != 'material_transaction':
        return jsonify({'error': '无效的附件ID'}), 404
    
    # 获取关联的物料交易记录
    transaction = MaterialTransaction.query.get_or_404(attachment.related_id)
    
    # 检查权限
    if not current_user.has_permission('material_transaction_update_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限删除此附件'}), 403
    
    # 删除物理文件
    try:
        file_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), attachment.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
    
    # 删除数据库记录
    db.session.delete(attachment)
    db.session.commit()
    
    return jsonify({'message': '附件删除成功'})

@api_material_transaction_bp.route('/attachments/<int:attachment_id>/download', methods=['GET'])
@api_login_required
@permission_required('material_transaction_read')
def download_attachment(attachment_id):
    """下载附件"""
    from flask_login import current_user
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # 检查附件类型
    if attachment.related_type != 'material_transaction':
        return jsonify({'error': '无效的附件ID'}), 404
    
    # 获取关联的物料交易记录
    transaction = MaterialTransaction.query.get_or_404(attachment.related_id)
    
    # 检查权限
    if not current_user.has_permission('material_transaction_read_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限下载此附件'}), 403
    
    # 构建文件路径
    file_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), attachment.file_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    # 发送文件
    return send_file(file_path, as_attachment=True, download_name=attachment.original_name)

@api_material_transaction_bp.route('/material-transactions/batch-status', methods=['PUT'])
@api_login_required
@permission_required('material_transaction_status_manage')
def batch_update_material_transaction_status():
    """批量更新物料进出厂记录状态"""
    from flask_login import current_user
    data = request.get_json()
    
    if not data or 'ids' not in data or 'status' not in data:
        return jsonify({'error': '缺少必要参数'}), 400
        
    transaction_ids = data['ids']
    new_status = data['status']
    
    # 验证状态值
    valid_statuses = ['loading', 'arrived', 'stored', 'used']
    if new_status not in valid_statuses:
        return jsonify({'error': f'无效的状态值，有效值为: {", ".join(valid_statuses)}'}), 400
    
    # 定义有效的状态转换
    valid_transitions = {
        'loading': ['arrived'],
        'arrived': ['stored'],
        'stored': ['used'],
        'used': []
    }
    
    # 获取所有需要更新的记录
    transactions = MaterialTransaction.query.filter(MaterialTransaction.id.in_(transaction_ids)).all()
    
    # 检查权限
    if not current_user.has_permission('material_transaction_status_manage_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        for transaction in transactions:
            if transaction.factory_id not in factory_ids:
                return jsonify({'error': '您没有权限更新某些记录的状态'}), 403
    
    updated_ids = []
    errors = []
    
    for transaction in transactions:
        # 验证状态转换是否有效
        if new_status not in valid_transitions.get(transaction.status, []):
            errors.append({
                'id': transaction.id,
                'error': f'无法从 {transaction.status} 状态转换为 {new_status} 状态'
            })
            continue
        
        # 更新状态和相关字段
        transaction.status = new_status
        
        # 根据新状态更新时间和操作人员字段
        if new_status == 'arrived':
            transaction.arrival_time = datetime.now()
            transaction.arrival_by = current_user.id
        elif new_status == 'stored':
            transaction.storage_time = datetime.now()
            transaction.storage_by = current_user.id
        elif new_status == 'used':
            transaction.usage_time = datetime.now()
            transaction.usage_by = current_user.id
            transaction.editable = False  # 使用后不可编辑
        
        updated_ids.append(transaction.id)
    
    # 提交更改
    if updated_ids:
        db.session.commit()
    
    return jsonify({
        'updated': updated_ids,
        'errors': errors
    })