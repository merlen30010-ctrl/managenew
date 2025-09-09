#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
from datetime import datetime

def test_application_submit():
    """测试应聘信息提交"""
    base_url = 'http://127.0.0.1:5000'
    
    # 创建会话
    session = requests.Session()
    
    try:
        # 1. 访问应聘页面获取session
        print("=== 访问应聘页面 ===")
        response = session.get(f'{base_url}/application')
        print(f"页面访问状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"页面访问失败: {response.text}")
            return False
            
        # 2. 提交应聘信息
        print("\n=== 提交应聘信息 ===")
        test_data = {
            'name': '调试测试者',
            'gender': '男',
            'birth_date': '1990-01-01',
            'id_card': '110101199001011234',
            'phone': '13800138000',
            'education': '本科',
            'native_place': '北京市',
            'nationality': '汉族',
            'marital_status': '未婚',
            'job_title': '测试工程师',
            'address': '北京市测试区',
            'emergency_contact': '紧急联系人',
            'emergency_phone': '13900139000'
        }
        
        print(f"提交数据: {test_data}")
        
        response = session.post(f'{base_url}/application/submit', data=test_data, allow_redirects=False)
        print(f"提交状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✓ 表单提交成功（重定向）")
            print(f"重定向到: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"✗ 表单提交失败")
            print(f"响应内容: {response.text[:500]}")
            
        return response.status_code == 302
        
    except Exception as e:
        print(f"测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("开始调试应聘信息提交功能...")
    print(f"测试时间: {datetime.now()}")
    
    success = test_application_submit()
    
    if success:
        print("\n🎉 测试成功！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)