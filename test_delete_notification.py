#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知删除功能测试程序
测试用户删除通知的功能是否正常工作
"""

import requests
import json
from datetime import datetime

class NotificationDeleteTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        
    def login(self, username, password):
        """登录"""
        # 先获取登录页面以获取CSRF token等
        self.session.get(f'{self.base_url}/auth/login')
        
        login_data = {
            'username': username,
            'password': password
        }
        
        response = self.session.post(f'{self.base_url}/auth/login', data=login_data, allow_redirects=False)
        return response.status_code in [200, 302]  # 成功登录
    
    def test_admin_login(self):
        """测试管理员登录"""
        print("=== 测试管理员登录 ===")
        if self.login('admin', 'admin123'):
            print("✓ admin 登录成功")
            return True
        else:
            print("✗ admin 登录失败")
            return False
    
    def create_test_notification(self):
        """创建测试通知"""
        print("\n=== 创建测试通知 ===")
        
        data = {
            'title': '删除测试通知',
            'content': '这是一条用于测试删除功能的通知',
            'user_ids': [1],  # 发送给admin用户
            'send_to_all': False
        }
        
        response = self.session.post(
            f'{self.base_url}/api/admin/notifications',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            result = response.json()
            notification_id = result.get('data', {}).get('id')
            print(f"✓ 测试通知创建成功，ID: {notification_id}")
            return notification_id
        else:
            print(f"✗ 测试通知创建失败: {response.status_code}")
            return None
    
    def test_delete_notification_api(self, notification_id):
        """测试API删除通知"""
        print(f"\n=== 测试API删除通知 {notification_id} ===")
        
        response = self.session.delete(f'{self.base_url}/api/notifications/{notification_id}')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ API删除通知成功: {result.get('message')}")
            return True
        else:
            print(f"✗ API删除通知失败: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    error = response.json()
                    print(f"错误信息: {error.get('message')}")
                except:
                    pass
            return False
    
    def test_delete_notification_web(self, notification_id):
        """测试Web界面删除通知"""
        print(f"\n=== 测试Web界面删除通知 {notification_id} ===")
        
        response = self.session.post(f'{self.base_url}/notification/notifications/{notification_id}/delete')
        
        if response.status_code in [200, 302]:  # 200或302都表示成功
            print("✓ Web界面删除通知成功")
            return True
        else:
            print(f"✗ Web界面删除通知失败: {response.status_code}")
            return False
    
    def verify_notification_deleted(self, notification_id):
        """验证通知是否已删除"""
        print(f"\n=== 验证通知 {notification_id} 是否已删除 ===")
        
        response = self.session.get(f'{self.base_url}/api/notifications')
        
        if response.status_code == 200:
            result = response.json()
            notifications = result.get('data', {}).get('notifications', [])
            
            for notification in notifications:
                if notification['id'] == notification_id:
                    print(f"✗ 通知 {notification_id} 仍然存在，删除失败")
                    return False
            
            print(f"✓ 通知 {notification_id} 已成功删除")
            return True
        else:
            print(f"✗ 获取通知列表失败: {response.status_code}")
            return False
    
    def run_delete_tests(self):
        """运行删除功能测试"""
        print("开始通知删除功能测试...")
        print("=" * 50)
        
        # 管理员登录
        if not self.test_admin_login():
            return
        
        # 测试API删除功能
        print("\n" + "=" * 30)
        print("测试API删除功能")
        print("=" * 30)
        
        notification_id = self.create_test_notification()
        if notification_id:
            if self.test_delete_notification_api(notification_id):
                self.verify_notification_deleted(notification_id)
        
        # 测试Web界面删除功能
        print("\n" + "=" * 30)
        print("测试Web界面删除功能")
        print("=" * 30)
        
        notification_id = self.create_test_notification()
        if notification_id:
            if self.test_delete_notification_web(notification_id):
                self.verify_notification_deleted(notification_id)
        
        print("\n" + "=" * 50)
        print("通知删除功能测试完成！")
        print("\n建议手动测试:")
        print("1. 登录系统后访问通知列表")
        print("2. 点击删除按钮测试删除功能")
        print("3. 确认删除确认对话框正常显示")
        print("4. 验证删除后通知从列表中消失")

def main():
    tester = NotificationDeleteTester()
    tester.run_delete_tests()

if __name__ == '__main__':
    main()