from app import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)  # 车牌号码
    brand = db.Column(db.String(50))  # 车辆品牌
    model = db.Column(db.String(50))  # 车辆型号
    color = db.Column(db.String(20))  # 车辆颜色
    purchase_date = db.Column(db.Date)  # 购买日期
    status = db.Column(db.String(20), default='可用')  # 车辆状态：可用、已借出、维修中、报废等
    responsible_person_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 负责人ID
    insurance_expiry_date = db.Column(db.Date)  # 保险到期日期
    last_maintenance_date = db.Column(db.Date)  # 上次保养日期
    next_maintenance_mileage = db.Column(db.Float)  # 下次保养里程数
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    responsible_person = db.relationship('User', foreign_keys=[responsible_person_id])
    usage_records = db.relationship('VehicleUsageRecord', backref='vehicle', lazy=True)
    maintenance_records = db.relationship('MaintenanceRecord', backref='vehicle', lazy=True)
    insurance_records = db.relationship('InsuranceRecord', backref='vehicle', lazy=True)
    
    def __repr__(self):
        return f'<Vehicle {self.plate_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'status': self.status,
            'responsible_person_id': self.responsible_person_id,
            'responsible_person_name': self.responsible_person.name if self.responsible_person else None,
            'insurance_expiry_date': self.insurance_expiry_date.isoformat() if self.insurance_expiry_date else None,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'next_maintenance_mileage': self.next_maintenance_mileage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class VehicleUsageRecord(db.Model):
    __tablename__ = 'vehicle_usage_records'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)  # 车辆ID
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 借车人ID
    borrow_time = db.Column(db.DateTime, nullable=False)  # 借车时间
    borrow_mileage = db.Column(db.Float, nullable=True)  # 借车时里程数
    borrow_photo_id = db.Column(db.Integer, db.ForeignKey('attachments.id'), nullable=True)  # 借车照片ID
    return_time = db.Column(db.DateTime)  # 还车时间
    return_mileage = db.Column(db.Float)  # 还车时里程数
    return_photo_id = db.Column(db.Integer, db.ForeignKey('attachments.id'))  # 还车照片ID
    purpose = db.Column(db.String(200))  # 用车事由
    remarks = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    borrower = db.relationship('User', foreign_keys=[borrower_id])
    borrow_photo = db.relationship('Attachment', foreign_keys=[borrow_photo_id])
    return_photo = db.relationship('Attachment', foreign_keys=[return_photo_id])
    
    def __repr__(self):
        return f'<VehicleUsageRecord {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'vehicle_plate_number': self.vehicle.plate_number if self.vehicle else None,
            'borrower_id': self.borrower_id,
            'borrower_name': self.borrower.name if self.borrower else None,
            'borrow_time': self.borrow_time.isoformat() if self.borrow_time else None,
            'borrow_mileage': self.borrow_mileage,
            'borrow_photo_id': self.borrow_photo_id,
            'borrow_photo_url': self.borrow_photo.file_path if self.borrow_photo else None,
            'return_time': self.return_time.isoformat() if self.return_time else None,
            'return_mileage': self.return_mileage,
            'return_photo_id': self.return_photo_id,
            'return_photo_url': self.return_photo.file_path if self.return_photo else None,
            'purpose': self.purpose,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)  # 车辆ID
    maintenance_date = db.Column(db.Date, nullable=False)  # 保养日期
    maintenance_type = db.Column(db.String(50))  # 保养类型
    cost = db.Column(db.Float)  # 费用
    service_provider = db.Column(db.String(100))  # 服务商
    next_maintenance_mileage = db.Column(db.Float)  # 下次保养里程数
    remarks = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<MaintenanceRecord {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'vehicle_plate_number': self.vehicle.plate_number if self.vehicle else None,
            'maintenance_date': self.maintenance_date.isoformat() if self.maintenance_date else None,
            'maintenance_type': self.maintenance_type,
            'cost': self.cost,
            'service_provider': self.service_provider,
            'next_maintenance_mileage': self.next_maintenance_mileage,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InsuranceRecord(db.Model):
    __tablename__ = 'insurance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)  # 车辆ID
    insurance_company = db.Column(db.String(100))  # 保险公司
    policy_number = db.Column(db.String(50))  # 保单号
    start_date = db.Column(db.Date)  # 保险开始日期
    expiry_date = db.Column(db.Date)  # 保险到期日期
    premium = db.Column(db.Float)  # 保费
    remarks = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<InsuranceRecord {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'vehicle_plate_number': self.vehicle.plate_number if self.vehicle else None,
            'insurance_company': self.insurance_company,
            'policy_number': self.policy_number,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'premium': self.premium,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }