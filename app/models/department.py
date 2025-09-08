from app import db

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 部门名称
    short_name = db.Column(db.String(50))  # 部门简称
    full_name = db.Column(db.String(200))  # 部门全称
    level = db.Column(db.Integer, default=1)  # 级别：1为分厂，2为部门
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'))  # 父级部门ID
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # 自关联关系
    parent = db.relationship('Department', remote_side=[id], backref='children')
    # 负责人（多人）
    managers = db.relationship('User', secondary='department_managers', backref='managed_departments')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class DepartmentManager(db.Model):
    __tablename__ = 'department_managers'
    
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())