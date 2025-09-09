#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

# 检查管理员账户是否存在
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print('管理员账户已创建')
else:
    print('管理员账户已存在')