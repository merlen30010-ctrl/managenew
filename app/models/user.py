from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)  # 超级管理员标识
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """检查用户是否具有特定权限（混合模式）"""
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return True
        
        # 普通用户通过角色权限检查
        for role in self.roles:
            if role.has_permission(permission):
                return True
        return False
    
    def has_role(self, role_name):
        """检查用户是否具有特定角色"""
        return role_name in [role.name for role in self.roles]
    
    def has_permission_name(self, permission_name):
        """根据权限名称检查用户是否具有特定权限"""
        from app.models.permission import Permission
        permission = Permission.query.filter_by(name=permission_name).first()
        if permission:
            return self.has_permission(permission)
        return False
    

    
    def get_all_permissions(self):
        """获取用户的所有权限"""
        from app.models.permission import Permission, RolePermission
        
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return Permission.query.all()
        
        # 普通用户通过角色获取权限
        permissions = set()
        for role in self.roles:
            # 通过RolePermission中间表获取权限
            role_perms = RolePermission.query.filter_by(role_id=role.id).all()
            for rp in role_perms:
                permission = Permission.query.get(rp.permission_id)
                if permission:
                    permissions.add(permission)
        return list(permissions)
    
    def set_superuser(self, is_superuser=True):
        """设置/取消超级管理员状态"""
        self.is_superuser = is_superuser
        db.session.commit()
        
    def is_super_admin(self):
        """检查是否为超级管理员（别名方法）"""
        return self.is_superuser
        
    @staticmethod
    def get_superusers():
        """获取所有超级管理员"""
        return User.query.filter_by(is_superuser=True).all()
    
    def __repr__(self):
        return f'<User {self.username}>'