from app import db
from datetime import datetime

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    module = db.Column(db.String(50))  # 模块名称
    action = db.Column(db.String(50))  # 操作类型 (create, read, update, delete)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    role = db.relationship('Role', backref='role_permissions')
    permission = db.relationship('Permission', backref='role_permissions')
    
    def __repr__(self):
        return f'<RolePermission role_id={self.role_id} permission_id={self.permission_id}>'