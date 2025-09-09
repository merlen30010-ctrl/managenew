#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试超级管理员按钮功能
"""

import requests
import json

def test_superuser_api():
    """测试超级管理员API端点"""
    base_url = 'http://127.0.0.1:5000'
    
    # 测试会话
    session = requests.Session()
    
    print("=== 测试超级管理员API端点 ===")
    
    # 1. 测试获取超级管理员列表
    print("\n1. 测试获取超级管理员列表...")
    try:
        response = session.get(f'{base_url}/api/superuser/list')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取用户列表
    print("\n2. 测试获取用户列表...")
    try:
        response = session.get(f'{base_url}/api/users')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"用户数量: {len(data.get('data', []))}")
            print(f"前3个用户: {json.dumps(data.get('data', [])[:3], indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试超级管理员状态页面
    print("\n3. 测试超级管理员状态页面...")
    try:
        response = session.get(f'{base_url}/superuser/status')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("页面加载成功")
        else:
            print(f"页面加载失败: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试超级管理员管理页面
    print("\n4. 测试超级管理员管理页面...")
    try:
        response = session.get(f'{base_url}/superuser/management')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("页面加载成功")
            # 检查页面内容是否包含关键元素
            content = response.text
            if 'addSuperuserModal' in content:
                print("✓ 找到添加超级管理员模态框")
            if 'data-bs-toggle="modal"' in content:
                print("✓ 找到Bootstrap 5模态框触发器")
            if 'bootstrap.Modal' in content:
                print("✓ 找到Bootstrap 5 JavaScript调用")
        else:
            print(f"页面加载失败: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == '__main__':
    test_superuser_api()