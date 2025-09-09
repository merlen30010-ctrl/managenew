#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.user import User
from app.models.role import Role
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

# 检查管理员账户是否存在
admin = User.query.filter_by(username='admin').first()
if not admin:
    # 创建管理员用户
    admin = User(
        username='admin',
        email='admin@example.com'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    # 获取管理员角色
    admin_role = Role.query.filter_by(name='管理员').first()
    if admin_role:
        # 分配管理员角色
        admin.roles.append(admin_role)
        db.session.commit()
        print('管理员账户已创建并分配角色')
    else:
        print('警告：管理员角色不存在，请先运行 init_db.py 初始化数据库')
else:
    # 确保现有管理员用户具有管理员角色
    admin_role = Role.query.filter_by(name='管理员').first()
    if admin_role and admin_role not in admin.roles:
        admin.roles.append(admin_role)
        db.session.commit()
        print('管理员账户已存在，已确保具有管理员角色')
    else:
        print('管理员账户已存在')