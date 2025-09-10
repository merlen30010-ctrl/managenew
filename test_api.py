#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

# Flask后端地址
BASE_URL = 'http://localhost:5000'

def test_login():
    """测试登录接口"""
    print("测试登录接口...")
    
    # 测试数据
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        # 发送登录请求
        response = requests.post(
            f'{BASE_URL}/api/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("登录成功!")
                print(f"Token: {data['data']['token']}")
                return data['data']['token']
            else:
                print(f"登录失败: {data.get('message')}")
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"请求异常: {e}")
    
    return None

def test_protected_api(token):
    """测试需要认证的API"""
    print("\n测试需要认证的API...")
    
    try:
        # 发送带token的请求
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{BASE_URL}/api/users/me',
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("认证成功!")
                print(f"用户信息: {data['data']}")
            else:
                print(f"认证失败: {data.get('message')}")
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == '__main__':
    print("Flask API测试脚本")
    print("=" * 50)
    
    # 测试登录
    token = test_login()
    
    # 如果登录成功，测试认证API
    if token:
        test_protected_api(token)
    
    print("\n测试完成!")