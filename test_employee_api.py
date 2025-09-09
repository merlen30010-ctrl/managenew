#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from requests.sessions import Session

def test_employee_api():
    """测试员工API接口"""
    base_url = 'http://127.0.0.1:5000'
    
    # 创建会话
    session = Session()
    
    try:
        # 1. 先获取登录页面（获取CSRF token等）
        print("1. 获取登录页面...")
        login_page = session.get(f'{base_url}/auth/login')
        print(f"登录页面状态码: {login_page.status_code}")
        
        # 2. 登录（使用管理员账户）
        print("\n2. 尝试登录...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f'{base_url}/auth/login', data=login_data)
        print(f"登录响应状态码: {login_response.status_code}")
        
        # 检查是否登录成功（通过重定向判断）
        if login_response.status_code == 302 or '仪表板' in login_response.text:
            print("登录成功！")
        else:
            print("登录可能失败，继续尝试API调用...")
        
        # 3. 调用员工API
        print("\n3. 调用员工API...")
        api_response = session.get(f'{base_url}/api/employees')
        print(f"API响应状态码: {api_response.status_code}")
        
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print("\nAPI响应数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                if data.get('success'):
                    employees = data.get('data', {}).get('items', [])
                    print(f"\n找到 {len(employees)} 个员工:")
                    for emp in employees:
                        print(f"- {emp.get('name', 'N/A')} ({emp.get('employee_id', 'N/A')}) - {emp.get('employment_status', 'N/A')}")
                else:
                    print(f"API返回错误: {data.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                print("API响应不是有效的JSON格式")
                print(f"响应内容前500字符: {api_response.text[:500]}")
        else:
            print(f"API调用失败，状态码: {api_response.status_code}")
            print(f"响应内容前500字符: {api_response.text[:500]}")
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == '__main__':
    test_employee_api()