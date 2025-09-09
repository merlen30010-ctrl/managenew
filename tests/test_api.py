#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API接口测试脚本
用于验证工厂管理系统的API接口是否正常工作
"""

import os
import sys
import requests
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置Flask应用环境变量
os.environ['FLASK_APP'] = 'run.py'

from app import create_app, db
from app.models.user import User
from app.models.material import Material
from app.models.customer import Customer
from app.models.department import Department
from app.models.contract import Contract

# API基础URL
BASE_URL = 'http://localhost:5000/api'

def test_api_endpoints():
    """测试所有API端点"""
    print("开始测试API接口...")
    
    # 测试用户相关接口
    print("\n1. 测试用户相关接口")
    
    # 获取用户列表
    try:
        response = requests.get(f'{BASE_URL}/users')
        print(f"   获取用户列表: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"   用户数量: {len(users)}")
    except Exception as e:
        print(f"   获取用户列表失败: {e}")
    
    # 测试物料相关接口
    print("\n2. 测试物料相关接口")
    
    # 获取物料列表
    try:
        response = requests.get(f'{BASE_URL}/materials')
        print(f"   获取物料列表: {response.status_code}")
        if response.status_code == 200:
            materials = response.json()
            print(f"   物料数量: {len(materials)}")
    except Exception as e:
        print(f"   获取物料列表失败: {e}")
    
    # 测试客户相关接口
    print("\n3. 测试客户相关接口")
    
    # 获取客户列表
    try:
        response = requests.get(f'{BASE_URL}/customers')
        print(f"   获取客户列表: {response.status_code}")
        if response.status_code == 200:
            customers = response.json()
            print(f"   客户数量: {len(customers)}")
    except Exception as e:
        print(f"   获取客户列表失败: {e}")
    
    # 测试部门相关接口
    print("\n4. 测试部门相关接口")
    
    # 获取部门列表
    try:
        response = requests.get(f'{BASE_URL}/departments')
        print(f"   获取部门列表: {response.status_code}")
        if response.status_code == 200:
            departments = response.json()
            print(f"   部门数量: {len(departments)}")
    except Exception as e:
        print(f"   获取部门列表失败: {e}")
    
    # 测试合同相关接口
    print("\n5. 测试合同相关接口")
    
    # 获取合同列表
    try:
        response = requests.get(f'{BASE_URL}/contracts')
        print(f"   获取合同列表: {response.status_code}")
        if response.status_code == 200:
            contracts = response.json()
            print(f"   合同数量: {len(contracts)}")
    except Exception as e:
        print(f"   获取合同列表失败: {e}")
    
    print("\nAPI接口测试完成!")

def create_test_data():
    """创建测试数据"""
    print("创建测试数据...")
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        # 创建所有数据库表
        db.create_all()
        # 创建测试用户
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='testuser@example.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
            print("   创建测试用户: testuser")
        
        # 创建测试物料
        material = Material.query.filter_by(code='TEST001').first()
        if not material:
            material = Material(name='测试物料', code='TEST001', full_name='测试物料全称', purpose='其他')
            db.session.add(material)
            db.session.commit()
            print("   创建测试物料: TEST001")
        
        # 创建测试客户
        customer = Customer.query.filter_by(code='CUST001').first()
        if not customer:
            customer = Customer(name='测试客户', code='CUST001', full_name='测试客户全称', 
                              customer_type='其他', phone='12345678901', address='测试地址')
            db.session.add(customer)
            db.session.commit()
            print("   创建测试客户: CUST001")
        
        # 创建测试部门
        department = Department.query.filter_by(name='测试部门').first()
        if not department:
            department = Department(name='测试部门', short_name='测试部', full_name='测试部门全称', level=1)
            db.session.add(department)
            db.session.commit()
            print("   创建测试部门: 测试部门")
        
        print("测试数据创建完成!")

def test_create_user():
    """测试创建用户接口"""
    print("\n测试创建用户接口...")
    
    # 准备测试数据
    user_data = {
        "username": "api_test_user",

        "name": "API测试用户",
        "phone": "13800138000",
        "password": "test123"
    }
    
    # 发送POST请求
    try:
        response = requests.post(f'{BASE_URL}/users', json=user_data)
        print(f"   创建用户响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            user = response.json()
            print(f"   创建用户成功: {user['username']}")
            return user['id']
        else:
            print(f"   创建用户失败: {response.text}")
            return None
    except Exception as e:
        print(f"   创建用户请求失败: {e}")
        return None

def api_test_get_user(user_id):
    """测试获取用户接口"""
    if not user_id:
        return
        
    print("\n测试获取用户接口...")
    
    # 发送GET请求
    try:
        response = requests.get(f'{BASE_URL}/users/{user_id}')
        print(f"   获取用户响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"   获取用户成功: {user['username']}")
        else:
            print(f"   获取用户失败: {response.text}")
    except Exception as e:
        print(f"   获取用户请求失败: {e}")

def api_test_update_user(user_id):
    """测试更新用户接口"""
    if not user_id:
        return
        
    print("\n测试更新用户接口...")
    
    # 准备更新数据
    update_data = {
        "name": "API测试用户-更新",
        "phone": "13900139000"
    }
    
    # 发送PUT请求
    try:
        response = requests.put(f'{BASE_URL}/users/{user_id}', json=update_data)
        print(f"   更新用户响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"   更新用户成功: {user['name']}")
        else:
            print(f"   更新用户失败: {response.text}")
    except Exception as e:
        print(f"   更新用户请求失败: {e}")

def api_test_delete_user(user_id):
    """测试删除用户接口"""
    if not user_id:
        return
        
    print("\n测试删除用户接口...")
    
    # 发送DELETE请求
    try:
        response = requests.delete(f'{BASE_URL}/users/{user_id}')
        print(f"   删除用户响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   删除用户成功: {result['message']}")
        else:
            print(f"   删除用户失败: {response.text}")
    except Exception as e:
        print(f"   删除用户请求失败: {e}")

if __name__ == '__main__':
    # 首先创建测试数据
    create_test_data()
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试用户CRUD操作
    user_id = test_create_user()
    api_test_get_user(user_id)
    api_test_update_user(user_id)
    api_test_delete_user(user_id)
    
    print("\n所有测试完成!")