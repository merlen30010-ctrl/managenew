#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
化验数据API接口测试脚本
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_assay_api():
    """测试化验数据API接口"""
    from app import create_app, db
    from app.models.user import User
    from app.models.department import Department
    from app.models.role import Role
    from app.models.permission import Permission
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        # 创建所有数据库表
        db.create_all()
        # 创建测试分厂
        factory = Department.query.filter_by(name='API测试分厂').first()
        if not factory:
            factory = Department(name='API测试分厂', level=1)
            db.session.add(factory)
            db.session.commit()
            print("创建API测试分厂成功")
        
        # 创建测试角色和权限
        test_role = Role.query.filter_by(name='测试角色').first()
        if not test_role:
            test_role = Role(name='测试角色', description='用于API测试的角色')
            db.session.add(test_role)
            db.session.commit()
            print("创建测试角色成功")
        
        # 为测试角色分配化验数据权限
        permissions = [
            'assay_data_read',
            'assay_data_create',
            'assay_data_update',
            'assay_data_delete'
        ]
        
        for perm_name in permissions:
            permission = Permission.query.filter_by(name=perm_name).first()
            if permission and not test_role.has_permission(permission):
                test_role.add_permission(permission)
        
        db.session.commit()
        
        # 创建测试用户并分配角色
        test_user = User.query.filter_by(username='apitestuser').first()
        if not test_user:
            test_user = User(username='apitestuser')
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            print("创建API测试用户成功")
        
        # 为测试用户分配角色
        if test_role not in test_user.roles:
            test_user.roles.append(test_role)
            db.session.commit()
            print("为测试用户分配角色成功")
        
        print("化验数据API接口测试准备完成")
        print("您可以使用以下命令测试API接口:")
        print("1. 启动Flask应用: python run.py")
        print("2. 使用curl或Postman测试以下端点:")
        print("   - GET /api/assay-data (获取化验数据列表)")
        print("   - POST /api/assay-data (创建化验数据)")
        print("   - GET /api/assay-data/<id> (获取单个化验数据)")
        print("   - PUT /api/assay-data/<id> (更新化验数据)")
        print("   - DELETE /api/assay-data/<id> (删除化验数据)")

if __name__ == '__main__':
    test_assay_api()