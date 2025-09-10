# -*- coding: utf-8 -*-
"""
JWT工具类
提供JWT token的生成、验证和解码功能
"""

import jwt
import datetime
from typing import Dict, Optional, Any
from flask import current_app


class JWTManager:
    """JWT管理器"""
    
    @classmethod
    def _get_blacklist_manager(cls):
        """获取黑名单管理器实例"""
        try:
            from .blacklist_manager import blacklist_manager
            return blacklist_manager
        except ImportError:
            return None
    
    @staticmethod
    def generate_token(user_id: int, username: str, expires_in: int = None) -> str:
        """
        生成JWT token
        
        Args:
            user_id: 用户ID
            username: 用户名
            expires_in: 过期时间（秒），默认使用配置中的值
            
        Returns:
            JWT token字符串
        """
        if expires_in is None:
            expires_in = current_app.config.get('JWT_EXPIRATION_DELTA', 3600)  # 默认1小时
            
        import uuid
        now = datetime.datetime.utcnow()
        exp_time = now + datetime.timedelta(seconds=expires_in)
        payload = {
            'user_id': user_id,
            'username': username,
            'iat': int(now.timestamp()),  # 签发时间，使用UTC时间戳
            'exp': int(exp_time.timestamp()),  # 过期时间，使用UTC时间戳
            'jti': f"{user_id}_{int(now.timestamp())}_{uuid.uuid4().hex[:8]}"  # JWT ID，用于黑名单
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY', current_app.config['SECRET_KEY'])
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        
        # 注册会话到会话管理器
        try:
            from .session_manager import session_manager
            expires_at = now + datetime.timedelta(seconds=expires_in)
            session_manager.register_session(user_id, token, expires_at)
        except ImportError:
            pass  # 如果会话管理器不可用，继续正常流程
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT token
        
        Args:
            token: JWT token字符串
            
        Returns:
            解码后的payload，验证失败返回None
        """
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY', current_app.config['SECRET_KEY'])
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            # 先不验证过期时间进行解码
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=[algorithm],
                options={"verify_exp": False}
            )
            
            # 手动检查过期时间
            exp = payload.get('exp')
            if exp:
                import datetime
                current_time = datetime.datetime.utcnow().timestamp()
                if current_time > exp:
                    return None
            
            # 检查token是否在黑名单中
            jti = payload.get('jti')
            if jti:
                blacklist_manager = JWTManager._get_blacklist_manager()
                if blacklist_manager and blacklist_manager.is_blacklisted(jti):
                    return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            # Token已过期
            return None
        except jwt.InvalidTokenError:
            # Token无效
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        解码JWT token（不验证过期时间）
        
        Args:
            token: JWT token字符串
            
        Returns:
            解码后的payload，解码失败返回None
        """
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY', current_app.config['SECRET_KEY'])
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            # 不验证过期时间
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=[algorithm],
                options={"verify_exp": False}
            )
            
            return payload
            
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def refresh_token(token: str) -> Optional[str]:
        """
        刷新JWT token
        
        Args:
            token: 原JWT token字符串
            
        Returns:
            新的JWT token，刷新失败返回None
        """
        payload = JWTManager.decode_token(token)
        if not payload:
            return None
            
        # 检查token是否在黑名单中
        jti = payload.get('jti')
        if jti:
            blacklist_manager = JWTManager._get_blacklist_manager()
            if blacklist_manager and blacklist_manager.is_blacklisted(jti):
                return None
            
        # 检查token是否在刷新窗口期内
        exp = payload.get('exp')
        if exp:
            exp_time = datetime.datetime.fromtimestamp(exp)
            refresh_window = current_app.config.get('JWT_REFRESH_WINDOW', 300)  # 默认5分钟
            current_time = datetime.datetime.utcnow()
            
            # 只有在token即将过期（剩余时间小于刷新窗口）或已过期但在窗口期内时才允许刷新
            time_until_expiry = (exp_time - current_time).total_seconds()
            time_since_expiry = (current_time - exp_time).total_seconds()
            
            # 如果token还有很长时间才过期（超过刷新窗口），不允许刷新
            if time_until_expiry > refresh_window:
                return None
            # 如果token过期时间超过刷新窗口，也不允许刷新
            if time_since_expiry > refresh_window:
                return None
        
        # 将旧token加入黑名单
        if jti:
            blacklist_manager = JWTManager._get_blacklist_manager()
            if blacklist_manager:
                # 获取token的过期时间
                expires_at = None
                exp_timestamp = payload.get('exp')
                if exp_timestamp:
                    expires_at = datetime.datetime.fromtimestamp(exp_timestamp)
                
                blacklist_manager.add_to_blacklist(jti, expires_at=expires_at)
            
        # 生成新token
        user_id = payload.get('user_id')
        username = payload.get('username')
        
        if user_id and username:
            return JWTManager.generate_token(user_id, username)
            
        return None
    
    @staticmethod
    def revoke_token(token: str) -> bool:
        """
        撤销JWT token（加入黑名单）
        
        Args:
            token: JWT token字符串
            
        Returns:
            撤销是否成功
        """
        return JWTManager.blacklist_token(token)
    
    @staticmethod
    def blacklist_token(token: str) -> bool:
        """
        将token加入黑名单
        
        Args:
            token: JWT token字符串
            
        Returns:
            操作是否成功
        """
        blacklist_manager = JWTManager._get_blacklist_manager()
        if blacklist_manager:
            try:
                # 解码token获取jti和过期时间
                payload = jwt.decode(token, options={"verify_signature": False})
                jti = payload.get('jti')
                exp = payload.get('exp')
                if jti:
                    expires_at = datetime.datetime.fromtimestamp(exp) if exp else None
                    blacklist_manager.add_to_blacklist(jti, expires_at=expires_at)
                    
                    # 从会话管理器中移除会话
                    try:
                        from .session_manager import session_manager
                        session_manager.remove_session(token)
                    except ImportError:
                        pass
                    
                    return True
            except jwt.InvalidTokenError:
                pass
        return False
    
    @staticmethod
    def is_token_revoked(token: str) -> bool:
        """
        检查token是否已被撤销
        
        Args:
            token: JWT token字符串
            
        Returns:
            token是否已被撤销
        """
        payload = JWTManager.decode_token(token)
        if not payload:
            return True
            
        jti = payload.get('jti')
        if jti:
            blacklist_manager = JWTManager._get_blacklist_manager()
            if blacklist_manager:
                return blacklist_manager.is_blacklisted(jti)
        return False
    
    @staticmethod
    def get_token_info(token: str) -> Optional[Dict[str, Any]]:
        """
        获取token信息
        
        Args:
            token: JWT token字符串
            
        Returns:
            token信息字典
        """
        payload = JWTManager.decode_token(token)
        if not payload:
            return None
            
        exp = payload.get('exp')
        iat = payload.get('iat')
        
        info = {
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'jti': payload.get('jti'),
            'issued_at': datetime.datetime.fromtimestamp(iat) if iat else None,
            'expires_at': datetime.datetime.fromtimestamp(exp) if exp else None,
            'is_expired': datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(exp) if exp else False,
            'is_revoked': JWTManager.is_token_revoked(token)
        }
        
        return info
    
    @staticmethod
    def clear_blacklist():
        """
        清空黑名单（主要用于测试）
        """
        blacklist_manager = JWTManager._get_blacklist_manager()
        if blacklist_manager:
            blacklist_manager.clear_all()