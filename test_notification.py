#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通知功能测试程序
测试通知的创建、读取、标记已读等功能
"""

import requests
import json
import time
from datetime import datetime

class NotificationTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        
    def login(self, username, password):
        """登录获取token"""
        login_data = {
            'username': username,
            'password': password
        }
        
        response = self.session.post(f'{self.base_url}/auth/login', data=login_data)
        if response.status_code == 200:
            print(f"✓ {username} 登录成功")
            return True
        else:
            print(f"✗ {username} 登录失败: {response.status_code}")
            return False
    
    def test_admin_login(self):
        """测试管理员登录"""
        print("\n=== 测试管理员登录 ===")
        return self.login('admin', 'admin123')
    
    def test_user_login(self):
        """测试普通用户登录"""
        print("\n=== 测试普通用户登录 ===")
        # 这里假设有一个普通用户，如果没有可以先创建
        return self.login('testuser', 'password123')
    
    def test_create_notification(self):
        """测试创建通知"""
        print("\n=== 测试创建通知 ===")
        
        # 测试数据
        notification_data = {
            'title': f'测试通知 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': '这是一条测试通知，用于验证通知功能是否正常工作。',
            'send_to_all': True
        }
        
        response = self.session.post(
            f'{self.base_url}/api/admin/notifications',
            json=notification_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ 通知创建成功: {result.get('message')}")
            return result.get('data', {}).get('id')
        else:
            print(f"✗ 通知创建失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误信息: {error_data.get('message', '未知错误')}")
            except:
                print(f"响应内容: {response.text}")
            return None
    
    def test_get_notifications(self):
        """测试获取通知列表"""
        print("\n=== 测试获取通知列表 ===")
        
        response = self.session.get(f'{self.base_url}/api/notifications')
        
        if response.status_code == 200:
            result = response.json()
            notifications = result.get('data', {}).get('notifications', [])
            print(f"✓ 获取通知列表成功，共 {len(notifications)} 条通知")
            
            for notification in notifications[:3]:  # 只显示前3条
                print(f"  - {notification['title']} ({'已读' if notification['is_read'] else '未读'})")
            
            return notifications
        else:
            print(f"✗ 获取通知列表失败: {response.status_code}")
            return []
    
    def test_get_unread_count(self):
        """测试获取未读通知数量"""
        print("\n=== 测试获取未读通知数量 ===")
        
        response = self.session.get(f'{self.base_url}/api/notifications/unread-count')
        
        if response.status_code == 200:
            result = response.json()
            count = result.get('data', {}).get('unread_count', 0)
            print(f"✓ 未读通知数量: {count}")
            return count
        else:
            print(f"✗ 获取未读通知数量失败: {response.status_code}")
            return 0
    
    def test_mark_notification_read(self, notification_id):
        """测试标记通知为已读"""
        print(f"\n=== 测试标记通知 {notification_id} 为已读 ===")
        
        response = self.session.put(f'{self.base_url}/api/notifications/{notification_id}/read')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 通知标记为已读成功: {result.get('message')}")
            return True
        else:
            print(f"✗ 标记通知为已读失败: {response.status_code}")
            return False
    
    def test_mark_all_read(self):
        """测试标记所有通知为已读"""
        print("\n=== 测试标记所有通知为已读 ===")
        
        response = self.session.put(f'{self.base_url}/api/notifications/mark-all-read')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 标记所有通知为已读成功: {result.get('message')}")
            return True
        else:
            print(f"✗ 标记所有通知为已读失败: {response.status_code}")
            return False
    
    def test_admin_get_all_notifications(self):
        """测试管理员获取所有通知"""
        print("\n=== 测试管理员获取所有通知 ===")
        
        response = self.session.get(f'{self.base_url}/api/admin/notifications')
        
        if response.status_code == 200:
            result = response.json()
            notifications = result.get('data', {}).get('notifications', [])
            pagination = result.get('data', {}).get('pagination', {})
            print(f"✓ 管理员获取所有通知成功，共 {pagination.get('total', 0)} 条通知")
            
            for notification in notifications[:3]:  # 只显示前3条
                username = notification.get('username', '未知用户')
                print(f"  - {notification['title']} (用户: {username}, {'已读' if notification['is_read'] else '未读'})")
            
            return notifications
        else:
            print(f"✗ 管理员获取所有通知失败: {response.status_code}")
            return []
    
    def test_web_interface(self):
        """测试Web界面访问"""
        print("\n=== 测试Web界面访问 ===")
        
        # 测试用户通知页面
        response = self.session.get(f'{self.base_url}/notification/notifications')
        if response.status_code == 200:
            print("✓ 用户通知页面访问成功")
        else:
            print(f"✗ 用户通知页面访问失败: {response.status_code}")
        
        # 测试管理员通知管理页面
        response = self.session.get(f'{self.base_url}/notification/admin/notifications')
        if response.status_code == 200:
            print("✓ 管理员通知管理页面访问成功")
        else:
            print(f"✗ 管理员通知管理页面访问失败: {response.status_code}")
        
        # 测试创建通知页面
        response = self.session.get(f'{self.base_url}/notification/admin/notifications/create')
        if response.status_code == 200:
            print("✓ 创建通知页面访问成功")
        else:
            print(f"✗ 创建通知页面访问失败: {response.status_code}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始通知功能测试...")
        print("=" * 50)
        
        # 管理员测试
        if not self.test_admin_login():
            print("管理员登录失败，跳过管理员相关测试")
            return
        
        # 测试创建通知
        notification_id = self.test_create_notification()
        
        # 测试管理员获取所有通知
        self.test_admin_get_all_notifications()
        
        # 测试获取通知列表
        notifications = self.test_get_notifications()
        
        # 测试获取未读通知数量
        unread_count = self.test_get_unread_count()
        
        # 测试标记单个通知为已读
        if notifications and unread_count > 0:
            unread_notification = next((n for n in notifications if not n['is_read']), None)
            if unread_notification:
                self.test_mark_notification_read(unread_notification['id'])
        
        # 再次获取未读数量
        self.test_get_unread_count()
        
        # 测试标记所有通知为已读
        if unread_count > 1:
            self.test_mark_all_read()
            self.test_get_unread_count()
        
        # 测试Web界面
        self.test_web_interface()
        
        print("\n=" * 50)
        print("通知功能测试完成！")
        print("\n建议手动测试以下功能:")
        print("1. 访问 http://localhost:5000 查看导航栏通知图标")
        print("2. 点击通知图标查看通知列表")
        print("3. 管理员登录后访问系统管理 -> 通知管理")
        print("4. 创建新通知并测试发送功能")
        print("5. 测试通知的标记已读功能")

def main():
    """主函数"""
    tester = NotificationTester()
    tester.run_all_tests()

if __name__ == '__main__':
    main()