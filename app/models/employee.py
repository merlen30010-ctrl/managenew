from app import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    # 使用user_id作为主键，建立一对一关系
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, comment='用户ID')
    
    # 员工基本信息
    employee_id = db.Column(db.String(20), unique=True, index=True, comment='员工工号')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), comment='部门ID')
    job_title = db.Column(db.String(50), comment='职位')
    hire_date = db.Column(db.Date, comment='入职日期')
    work_years = db.Column(db.Integer, comment='工龄')
    
    # 基本信息
    name = db.Column(db.String(64), comment='姓名')
    gender = db.Column(db.String(10), comment='性别')
    birth_date = db.Column(db.Date, comment='出生日期')
    id_card = db.Column(db.String(18), unique=True, comment='身份证号')
    native_place = db.Column(db.String(100), comment='籍贯')
    nationality = db.Column(db.String(50), comment='民族')
    education = db.Column(db.String(50), comment='学历')
    marital_status = db.Column(db.String(20), comment='婚姻状况')
    phone = db.Column(db.String(20), comment='联系电话')
    address = db.Column(db.String(200), comment='居住地址')
    avatar_path = db.Column(db.String(200), comment='照片路径')
    employment_status = db.Column(db.String(20), default='在职', comment='在职状态')
    
    # 联系信息
    emergency_contact = db.Column(db.String(50), comment='紧急联系人')
    emergency_phone = db.Column(db.String(20), comment='紧急联系电话')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('employee', uselist=False))
    department = db.relationship('Department', backref='employees')
    
    def __repr__(self):
        return f'<Employee {self.employee_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'department_id': self.department_id,
            'job_title': self.job_title,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'work_years': self.work_years,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'id_card': self.id_card,
            'native_place': self.native_place,
            'nationality': self.nationality,
            'education': self.education,
            'marital_status': self.marital_status,
            'phone': self.phone,
            'address': self.address,
            'avatar_path': self.avatar_path,
            'employment_status': self.employment_status,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }