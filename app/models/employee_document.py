from app import db
from datetime import datetime

class EmployeeDocument(db.Model):
    """员工证件管理模型"""
    __tablename__ = 'employee_documents'
    
    id = db.Column(db.Integer, primary_key=True, comment='证件ID')
    employee_id = db.Column(db.String(20), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工工号')
    
    # 证件基本信息
    document_type = db.Column(db.String(50), nullable=False, comment='证件类型')
    document_name = db.Column(db.String(100), nullable=False, comment='证件名称')
    document_number = db.Column(db.String(100), comment='证件编号')
    issuing_authority = db.Column(db.String(100), comment='发证机关')
    issue_date = db.Column(db.Date, comment='发证日期')
    expiry_date = db.Column(db.Date, comment='有效期至')
    
    # 证件状态
    status = db.Column(db.String(20), default='有效', comment='证件状态')
    is_original = db.Column(db.Boolean, default=True, comment='是否原件')
    
    # 文件信息
    file_path = db.Column(db.String(500), comment='证件文件路径')
    file_name = db.Column(db.String(200), comment='原始文件名')
    file_size = db.Column(db.Integer, comment='文件大小(字节)')
    
    # 备注信息
    notes = db.Column(db.Text, comment='备注')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    employee = db.relationship('Employee', backref='documents')
    
    def __repr__(self):
        return f'<EmployeeDocument {self.document_name}({self.employee_id})>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'document_type': self.document_type,
            'document_name': self.document_name,
            'document_number': self.document_number,
            'issuing_authority': self.issuing_authority,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'is_original': self.is_original,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @property
    def is_expired(self):
        """检查证件是否过期"""
        if self.expiry_date:
            return datetime.now().date() > self.expiry_date
        return False
    
    @property
    def days_to_expiry(self):
        """距离过期天数"""
        if self.expiry_date:
            delta = self.expiry_date - datetime.now().date()
            return delta.days
        return None

class DocumentType(db.Model):
    """证件类型配置模型"""
    __tablename__ = 'document_types'
    
    id = db.Column(db.Integer, primary_key=True, comment='类型ID')
    type_code = db.Column(db.String(50), unique=True, nullable=False, comment='类型代码')
    type_name = db.Column(db.String(100), nullable=False, comment='类型名称')
    category = db.Column(db.String(50), comment='证件分类')
    is_required = db.Column(db.Boolean, default=False, comment='是否必需')
    has_expiry = db.Column(db.Boolean, default=True, comment='是否有有效期')
    reminder_days = db.Column(db.Integer, default=30, comment='到期提醒天数')
    description = db.Column(db.Text, comment='描述')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<DocumentType {self.type_name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'type_code': self.type_code,
            'type_name': self.type_name,
            'category': self.category,
            'is_required': self.is_required,
            'has_expiry': self.has_expiry,
            'reminder_days': self.reminder_days,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }