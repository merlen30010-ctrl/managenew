# -*- coding: utf-8 -*-
"""
JWT相关功能的测试用例
"""

import unittest
import datetime
import time
import json
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.utils.jwt_utils import JWTManager
from app.utils.session_manager import SessionManager
from app.utils.blacklist_manager import BlacklistManager


class JWTTestCase(unittest.TestCase):
    """JWT功能测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.app.config['JWT_EXPIRATION_DELTA'] = 3600  # 1小时
        self.app.config['JWT_REFRESH_WINDOW'] = 300  # 5分钟
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # 删除已存在的测试用户
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        # 创建测试用户
        self.test_user = User(
            username='testuser'
        )
        self.test_user.set_password('testpassword')
        db.session.add(self.test_user)
        db.session.commit()
        
        self.client = self.app.test_client()
    
    def tearDown(self):
        """测试后的清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_generate_token(self):
        """测试token生成"""
        token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username
        )
        
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
    
    def test_verify_valid_token(self):
        """测试验证有效token"""
        token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username
        )
        
        payload = JWTManager.verify_token(token)
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.test_user.id)
        self.assertEqual(payload['username'], self.test_user.username)
        self.assertIn('exp', payload)
        self.assertIn('iat', payload)
        self.assertIn('jti', payload)
    
    def test_verify_invalid_token(self):
        """测试验证无效token"""
        invalid_token = 'invalid.token.here'
        payload = JWTManager.verify_token(invalid_token)
        self.assertIsNone(payload)
    
    def test_verify_expired_token(self):
        """测试验证过期token"""
        # 生成一个立即过期的token
        token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username,
            expires_in=1  # 1秒后过期
        )
        
        # 等待token过期
        time.sleep(2)
        
        payload = JWTManager.verify_token(token)
        self.assertIsNone(payload)
    
    def test_revoke_token(self):
        """测试撤销token"""
        token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username
        )
        
        # 验证token有效
        payload = JWTManager.verify_token(token)
        self.assertIsNotNone(payload)
        
        # 撤销token
        result = JWTManager.revoke_token(token)
        self.assertTrue(result)
        
        # 验证token已被撤销
        payload = JWTManager.verify_token(token)
        self.assertIsNone(payload)
    
    def test_refresh_token(self):
        """测试刷新token"""
        # 生成一个接近过期的token
        original_token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username,
            expires_in=200  # 200秒后过期，在刷新窗口内（默认300秒）
        )
        
        # 刷新token
        new_token = JWTManager.refresh_token(original_token)
        
        self.assertIsNotNone(new_token)
        self.assertNotEqual(original_token, new_token)
        
        # 验证新token有效
        payload = JWTManager.verify_token(new_token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.test_user.id)
    
    def test_refresh_token_outside_window(self):
        """测试在刷新窗口外刷新token"""
        # 生成一个不在刷新窗口内的token
        token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username,
            expires_in=3600  # 1小时后过期，不在刷新窗口内
        )
        
        # 尝试刷新token
        new_token = JWTManager.refresh_token(token)
        
        # 应该返回None，因为不在刷新窗口内
        self.assertIsNone(new_token)
    
    def test_decode_token(self):
        """测试解码token"""
        token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username
        )
        
        payload = JWTManager.decode_token(token)
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.test_user.id)
        self.assertEqual(payload['username'], self.test_user.username)
    
    def test_api_login_with_jwt(self):
        """测试API登录并获取JWT token"""
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('token', data['data'])
        
        # 验证返回的token
        token = data['data']['token']
        payload = JWTManager.verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.test_user.id)
    
    def test_api_access_with_jwt(self):
        """测试使用JWT token访问API"""
        # 先登录获取token
        login_response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        token = json.loads(login_response.data)['data']['token']
        
        # 使用token访问受保护的API
        response = self.client.get('/api/users/me', headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['username'], 'testuser')
    
    def test_api_access_without_token(self):
        """测试不带token访问API"""
        response = self.client.get('/api/users/me')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data.get('success', True))
    
    def test_api_access_with_invalid_token(self):
        """测试使用无效token访问API"""
        response = self.client.get('/api/users/me', headers={
            'Authorization': 'Bearer invalid.token.here'
        })
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data.get('success', True))
    
    def test_api_logout_with_jwt(self):
        """测试使用JWT token登出"""
        # 先登录获取token
        login_response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        token = json.loads(login_response.data)['data']['token']
        
        # 登出
        logout_response = self.client.post('/api/logout', headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(logout_response.status_code, 200)
        
        # 验证token已被撤销
        response = self.client.get('/api/users/me', headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_api(self):
        """测试刷新token API"""
        # 生成一个接近过期的token
        token = JWTManager.generate_token(
            user_id=self.test_user.id,
            username=self.test_user.username,
            expires_in=250  # 在刷新窗口内（默认300秒）
        )
        
        # 调用刷新API
        response = self.client.post('/api/refresh-token', headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('token', data['data'])
        
        # 验证新token有效
        new_token = data['data']['token']
        payload = JWTManager.verify_token(new_token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.test_user.id)


class SessionManagerTestCase(unittest.TestCase):
    """会话管理器测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SESSION_TIMEOUT'] = 3600
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        self.session_manager = SessionManager()
        self.test_user_id = 1
        self.test_token = 'test.jwt.token'
        self.expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    def test_register_session(self):
        """测试注册会话"""
        self.session_manager.register_session(
            self.test_user_id,
            self.test_token,
            self.expires_at
        )
        
        session_info = self.session_manager.get_session_info(self.test_token)
        self.assertIsNotNone(session_info)
        self.assertEqual(session_info['user_id'], self.test_user_id)
    
    def test_update_session_activity(self):
        """测试更新会话活动时间"""
        self.session_manager.register_session(
            self.test_user_id,
            self.test_token,
            self.expires_at
        )
        
        original_activity = self.session_manager.get_session_info(self.test_token)['last_activity']
        
        # 等待一秒后更新活动时间
        time.sleep(1)
        self.session_manager.update_session_activity(self.test_token)
        
        new_activity = self.session_manager.get_session_info(self.test_token)['last_activity']
        self.assertGreater(new_activity, original_activity)
    
    def test_check_session_timeout(self):
        """测试会话超时检查"""
        self.session_manager.register_session(
            self.test_user_id,
            self.test_token,
            self.expires_at
        )
        
        # 正常情况下不应该超时
        is_timeout = self.session_manager.check_session_timeout(self.test_token, 30)
        self.assertFalse(is_timeout)
        
        # 检查不存在的会话
        is_timeout = self.session_manager.check_session_timeout('nonexistent', 30)
        self.assertTrue(is_timeout)
    
    def tearDown(self):
        """测试后的清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class BlacklistManagerTestCase(unittest.TestCase):
    """黑名单管理器测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # 删除已存在的测试用户
        existing_user = User.query.filter_by(username='blacklistuser').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        # 使用临时文件进行测试
        import tempfile
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        self.blacklist_manager = BlacklistManager(self.temp_file.name)
        self.test_jti = 'test-jti-123'
        self.test_user_id = 1
    
    def tearDown(self):
        """测试后的清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        import os
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_add_token_to_blacklist(self):
        """测试添加token到黑名单"""
        self.blacklist_manager.add_token(
            jti=self.test_jti,
            reason='test_revocation',
            user_id=self.test_user_id
        )
        
        self.assertTrue(self.blacklist_manager.is_blacklisted(self.test_jti))
        self.assertEqual(self.blacklist_manager.get_blacklist_count(), 1)
    
    def test_remove_token_from_blacklist(self):
        """测试从黑名单移除token"""
        self.blacklist_manager.add_token(self.test_jti)
        self.assertTrue(self.blacklist_manager.is_blacklisted(self.test_jti))
        
        result = self.blacklist_manager.remove_token(self.test_jti)
        self.assertTrue(result)
        self.assertFalse(self.blacklist_manager.is_blacklisted(self.test_jti))
    
    def test_get_blacklist_info(self):
        """测试获取黑名单信息"""
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        
        self.blacklist_manager.add_token(
            jti=self.test_jti,
            reason='test_reason',
            expires_at=expires_at,
            user_id=self.test_user_id
        )
        
        info = self.blacklist_manager.get_blacklist_info(self.test_jti)
        self.assertIsNotNone(info)
        self.assertEqual(info['reason'], 'test_reason')
        self.assertEqual(info['user_id'], self.test_user_id)
    
    def test_get_user_blacklisted_tokens(self):
        """测试获取用户的黑名单token"""
        self.blacklist_manager.add_token(
            jti=self.test_jti,
            user_id=self.test_user_id
        )
        
        user_tokens = self.blacklist_manager.get_user_blacklisted_tokens(self.test_user_id)
        self.assertEqual(len(user_tokens), 1)
        self.assertEqual(user_tokens[0]['jti'], self.test_jti)


if __name__ == '__main__':
    unittest.main()