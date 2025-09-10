from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # 关联用户
    users = db.relationship('User', secondary='user_roles', backref='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def has_permission(self, permission):
        """检查角色是否具有特定权限"""
        # 使用字符串查询避免循环导入
        from sqlalchemy import text
        
        # 如果传入的是字符串，先查找对应的权限ID
        if isinstance(permission, str):
            permission_result = db.session.execute(
                text("SELECT id FROM permissions WHERE name = :permission_name"),
                {'permission_name': permission}
            ).first()
            if not permission_result:
                return False
            permission_id = permission_result[0]
        else:
            # 如果传入的是Permission对象
            permission_id = permission.id
            
        result = db.session.execute(
            text("SELECT 1 FROM role_permissions WHERE role_id = :role_id AND permission_id = :permission_id"),
            {'role_id': self.id, 'permission_id': permission_id}
        ).first()
        return result is not None
    
    def add_permission(self, permission):
        """为角色添加权限"""
        if not self.has_permission(permission):
            # 使用原生SQL避免循环导入
            from sqlalchemy import text
            
            # 如果传入的是字符串，先查找对应的权限ID
            if isinstance(permission, str):
                permission_result = db.session.execute(
                    text("SELECT id FROM permissions WHERE name = :permission_name"),
                    {'permission_name': permission}
                ).first()
                if not permission_result:
                    return
                permission_id = permission_result[0]
            else:
                # 如果传入的是Permission对象
                permission_id = permission.id
                
            db.session.execute(
                text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)"),
                {'role_id': self.id, 'permission_id': permission_id}
            )
    
    def remove_permission(self, permission):
        """为角色移除权限"""
        # 使用原生SQL避免循环导入
        from sqlalchemy import text
        
        # 如果传入的是字符串，先查找对应的权限ID
        if isinstance(permission, str):
            permission_result = db.session.execute(
                text("SELECT id FROM permissions WHERE name = :permission_name"),
                {'permission_name': permission}
            ).first()
            if not permission_result:
                return
            permission_id = permission_result[0]
        else:
            # 如果传入的是Permission对象
            permission_id = permission.id
            
        db.session.execute(
            text("DELETE FROM role_permissions WHERE role_id = :role_id AND permission_id = :permission_id"),
            {'role_id': self.id, 'permission_id': permission_id}
        )

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())