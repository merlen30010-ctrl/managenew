from flask import jsonify, request
from app.api import api_bp
from app import db
from app.models.vehicle import Vehicle, VehicleUsageRecord, MaintenanceRecord, InsuranceRecord
from app.models.attachment import Attachment
from datetime import datetime
from app.api.decorators import api_login_required, permission_required
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 车辆管理API
@api_bp.route('/vehicles', methods=['GET'])
@api_login_required
@permission_required('vehicle_read')
def get_vehicles():
    """获取车辆列表"""
    vehicles = Vehicle.query.all()
    return jsonify([vehicle.to_dict() for vehicle in vehicles])

@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@api_login_required
@permission_required('vehicle_read')
def get_vehicle(vehicle_id):
    """获取单个车辆信息"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify(vehicle.to_dict())

@api_bp.route('/vehicles', methods=['POST'])
@api_login_required
@permission_required('vehicle_create')
def create_vehicle():
    """创建车辆"""
    data = request.get_json()
    
    # 检查必填字段
    if not data or not data.get('license_plate'):
        return jsonify({'error': '车牌号是必填字段'}), 400
    
    # 检查车牌号是否已存在
    if Vehicle.query.filter_by(plate_number=data['license_plate']).first():
        return jsonify({'error': '车牌号已存在'}), 400
    
    # 创建新车辆
    vehicle = Vehicle(
        plate_number=data['license_plate'],
        brand=data.get('brand', ''),
        model=data.get('model', ''),
        color=data.get('color', ''),
        purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
        status=data.get('status', '可用')
    )
    
    db.session.add(vehicle)
    db.session.commit()
    
    return jsonify(vehicle.to_dict()), 201

@api_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@api_login_required
@permission_required('vehicle_update')
def update_vehicle(vehicle_id):
    """更新车辆信息"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新车辆信息
    if 'license_plate' in data:
        # 检查车牌号是否已存在
        existing_vehicle = Vehicle.query.filter_by(plate_number=data['license_plate']).first()
        if existing_vehicle and existing_vehicle.id != vehicle_id:
            return jsonify({'error': '车牌号已存在'}), 400
        vehicle.plate_number = data['license_plate']
    
    if 'brand' in data:
        vehicle.brand = data['brand']
    
    if 'model' in data:
        vehicle.model = data['model']
    
    if 'color' in data:
        vehicle.color = data['color']
    
    if 'purchase_date' in data:
        vehicle.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data['purchase_date'] else None
    
    if 'status' in data:
        vehicle.status = data['status']
    
    # 备注字段在Vehicle模型中不存在，已移除
    
    db.session.commit()
    
    return jsonify(vehicle.to_dict())

@api_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@api_login_required
@permission_required('vehicle_delete')
def delete_vehicle(vehicle_id):
    """删除车辆"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': '车辆删除成功'})

# 车辆借还记录API
@api_bp.route('/vehicle-usage-records', methods=['GET'])
@api_login_required
@permission_required('vehicle_usage_read')
def get_usage_records():
    """获取车辆借还记录列表"""
    records = VehicleUsageRecord.query.all()
    return jsonify([record.to_dict() for record in records])

@api_bp.route('/vehicle-usage-records/<int:record_id>', methods=['GET'])
@api_login_required
@permission_required('vehicle_usage_read')
def get_usage_record(record_id):
    """获取单个车辆借还记录"""
    record = VehicleUsageRecord.query.get_or_404(record_id)
    return jsonify(record.to_dict())

@api_bp.route('/vehicle-usage-records', methods=['POST'])
@api_login_required
@permission_required('vehicle_usage_create')
def create_usage_record():
    """创建车辆借还记录"""
    from flask_login import current_user
    data = request.get_json()
    
    # 检查必填字段
    if not data or not data.get('vehicle_id'):
        return jsonify({'error': '车辆ID是必填字段'}), 400
    
    # 检查车辆是否存在
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': '车辆不存在'}), 404
    
    # 检查借车时车辆状态
    if vehicle.status != '可用':
        return jsonify({'error': '车辆当前不可用'}), 400
    
    # 创建借车记录
    record = VehicleUsageRecord(
        vehicle_id=data['vehicle_id'],
        borrower_id=getattr(current_user, 'id', None),
        borrow_time=datetime.strptime(data['borrow_time'], '%Y-%m-%d %H:%M:%S') if data.get('borrow_time') else datetime.now(),
        borrow_mileage=data.get('borrow_mileage'),
        borrow_photo_id=data.get('borrow_photo_id'),
        purpose=data.get('purpose', ''),
        remarks=data.get('remarks', '')
    )
    
    db.session.add(record)
    db.session.flush()  # 获取记录ID
    
    # 更新车辆状态为使用中
    vehicle.status = '使用中'
    
    db.session.commit()
    
    return jsonify(record.to_dict()), 201

@api_bp.route('/vehicle-usage-records/<int:record_id>', methods=['PUT'])
@api_login_required
@permission_required('vehicle_usage_update')
def update_usage_record(record_id):
    """更新车辆借还记录"""
    record = VehicleUsageRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新记录信息
    if 'borrower_id' in data:
        record.borrower_id = data['borrower_id']
    
    if 'borrow_time' in data:
        record.borrow_time = datetime.strptime(data['borrow_time'], '%Y-%m-%d %H:%M:%S') if data['borrow_time'] else None
    
    if 'return_time' in data:
        record.return_time = datetime.strptime(data['return_time'], '%Y-%m-%d %H:%M:%S') if data['return_time'] else None
    
    if 'borrow_mileage' in data:
        record.borrow_mileage = data['borrow_mileage']
    
    if 'return_mileage' in data:
        record.return_mileage = data['return_mileage']
    
    if 'purpose' in data:
        record.purpose = data['purpose']
    
    if 'remarks' in data:
        record.remarks = data['remarks']
    
    if 'borrow_photo_id' in data:
        record.borrow_photo_id = data['borrow_photo_id']
    
    if 'return_photo_id' in data:
        record.return_photo_id = data['return_photo_id']
    
    db.session.commit()
    
    return jsonify(record.to_dict())

@api_bp.route('/vehicle-usage-records/<int:record_id>', methods=['DELETE'])
@api_login_required
@permission_required('vehicle_usage_delete')
def delete_usage_record(record_id):
    """删除车辆借还记录"""
    record = VehicleUsageRecord.query.get_or_404(record_id)
    
    # 如果是借车记录且有关联的还车记录，需要先删除还车记录
    if record.usage_type == '借车' and record.return_record_id:
        return_record = VehicleUsageRecord.query.get(record.return_record_id)
        if return_record:
            db.session.delete(return_record)
    
    # 更新车辆状态
    vehicle = record.vehicle
    if record.usage_type == '借车':
        vehicle.status = '可用'
    
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '车辆借还记录删除成功'})

# 保养记录API
@api_bp.route('/maintenance-records', methods=['GET'])
@api_login_required
@permission_required('vehicle_maintenance_read')
def get_maintenance_records():
    """获取保养记录列表"""
    records = MaintenanceRecord.query.all()
    return jsonify([record.to_dict() for record in records])

@api_bp.route('/maintenance-records/<int:record_id>', methods=['GET'])
@api_login_required
@permission_required('vehicle_maintenance_read')
def get_maintenance_record(record_id):
    """获取单个保养记录"""
    record = MaintenanceRecord.query.get_or_404(record_id)
    return jsonify(record.to_dict())

@api_bp.route('/maintenance-records', methods=['POST'])
@api_login_required
@permission_required('vehicle_maintenance_create')
def create_maintenance_record():
    """创建保养记录"""
    data = request.get_json()
    
    # 检查必填字段
    if not data or not data.get('vehicle_id') or not data.get('maintenance_date'):
        return jsonify({'error': '车辆ID和保养日期是必填字段'}), 400
    
    # 检查车辆是否存在
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': '车辆不存在'}), 404
    
    # 创建保养记录
    record = MaintenanceRecord(
        vehicle_id=data['vehicle_id'],
        maintenance_date=datetime.strptime(data['maintenance_date'], '%Y-%m-%d').date(),
        maintenance_type=data.get('maintenance_type', ''),
        cost=data.get('cost', 0),
        service_provider=data.get('service_provider', ''),
        next_maintenance_date=datetime.strptime(data['next_maintenance_date'], '%Y-%m-%d').date() if data.get('next_maintenance_date') else None,
        remarks=data.get('remarks', '')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify(record.to_dict()), 201

@api_bp.route('/maintenance-records/<int:record_id>', methods=['PUT'])
@api_login_required
@permission_required('vehicle_maintenance_update')
def update_maintenance_record(record_id):
    """更新保养记录"""
    record = MaintenanceRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新保养记录信息
    if 'maintenance_date' in data:
        record.maintenance_date = datetime.strptime(data['maintenance_date'], '%Y-%m-%d').date()
    
    if 'maintenance_type' in data:
        record.maintenance_type = data['maintenance_type']
    
    if 'cost' in data:
        record.cost = data['cost']
    
    if 'service_provider' in data:
        record.service_provider = data['service_provider']
    
    if 'next_maintenance_date' in data:
        record.next_maintenance_date = datetime.strptime(data['next_maintenance_date'], '%Y-%m-%d').date() if data['next_maintenance_date'] else None
    
    if 'remarks' in data:
        record.remarks = data['remarks']
    
    db.session.commit()
    
    return jsonify(record.to_dict())

@api_bp.route('/maintenance-records/<int:record_id>', methods=['DELETE'])
@api_login_required
@permission_required('vehicle_maintenance_delete')
def delete_maintenance_record(record_id):
    """删除保养记录"""
    record = MaintenanceRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '保养记录删除成功'})

# 保险记录API
@api_bp.route('/insurance-records', methods=['GET'])
@api_login_required
@permission_required('vehicle_insurance_read')
def get_insurance_records():
    """获取保险记录列表"""
    records = InsuranceRecord.query.all()
    return jsonify([record.to_dict() for record in records])

@api_bp.route('/insurance-records/<int:record_id>', methods=['GET'])
@api_login_required
@permission_required('vehicle_insurance_read')
def get_insurance_record(record_id):
    """获取单个保险记录"""
    record = InsuranceRecord.query.get_or_404(record_id)
    return jsonify(record.to_dict())

@api_bp.route('/insurance-records', methods=['POST'])
@api_login_required
@permission_required('vehicle_insurance_create')
def create_insurance_record():
    """创建保险记录"""
    data = request.get_json()
    
    # 检查必填字段
    if not data or not data.get('vehicle_id') or not data.get('insurance_company') or not data.get('start_date') or not data.get('end_date'):
        return jsonify({'error': '车辆ID、保险公司、开始日期和结束日期是必填字段'}), 400
    
    # 检查车辆是否存在
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': '车辆不存在'}), 404
    
    # 创建保险记录
    record = InsuranceRecord(
        vehicle_id=data['vehicle_id'],
        insurance_company=data['insurance_company'],
        policy_number=data.get('policy_number', ''),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
        premium=data.get('premium', 0),
        remarks=data.get('remarks', '')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify(record.to_dict()), 201

@api_bp.route('/insurance-records/<int:record_id>', methods=['PUT'])
@api_login_required
@permission_required('vehicle_insurance_update')
def update_insurance_record(record_id):
    """更新保险记录"""
    record = InsuranceRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新保险记录信息
    if 'insurance_company' in data:
        record.insurance_company = data['insurance_company']
    
    if 'policy_number' in data:
        record.policy_number = data['policy_number']
    
    if 'start_date' in data:
        record.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    
    if 'end_date' in data:
        record.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    if 'premium' in data:
        record.premium = data['premium']
    
    if 'remarks' in data:
        record.remarks = data['remarks']
    
    db.session.commit()
    
    return jsonify(record.to_dict())

@api_bp.route('/insurance-records/<int:record_id>', methods=['DELETE'])
@api_login_required
@permission_required('vehicle_insurance_delete')
def delete_insurance_record(record_id):
    """删除保险记录"""
    record = InsuranceRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '保险记录删除成功'})