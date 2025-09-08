# -*- coding: utf-8 -*-
"""
会话超时管理器
提供会话超时检测和自动清理功能
"""

import threading
import time
import datetime
from typing import Dict, Set
from flask import current_app
from .jwt_utils import JWTManager


class SessionManager:
    """会话管理器 - 管理用户活跃会话
    
    注意：当前实现中混合了会话管理和JWT黑名单清理功能
    TODO: 未来应将JWT黑名单管理分离到独立的BlacklistManager中
    """
    
    def __init__(self):
        self._cleanup_thread = None
        self._stop_cleanup = False
        self._active_sessions = {}  # 存储活跃会话信息
        self._lock = threading.Lock()
    
    def start_cleanup_thread(self):
        """启动清理线程"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._stop_cleanup = False
            self._cleanup_thread = threading.Thread(target=self._cleanup_expired_tokens, daemon=True)
            self._cleanup_thread.start()
    
    def stop_cleanup_thread(self):
        """停止清理线程"""
        self._stop_cleanup = True
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
    
    def _cleanup_expired_tokens(self):
        """清理过期token的后台线程
        
        注意：此方法同时处理会话清理和JWT黑名单清理
        TODO: 应将JWT黑名单清理分离到独立的服务中
        """
        while not self._stop_cleanup:
            try:
                self._remove_expired_sessions()  # 清理过期会话
                # 注意：黑名单清理已移至BlacklistManager，此处专注于会话管理
                # 每5分钟清理一次
                time.sleep(300)
            except Exception as e:
                # 记录错误但不停止线程
                print(f"Token cleanup error: {e}")
                time.sleep(60)  # 出错时等待1分钟再重试
    
    def _remove_expired_sessions(self):
        """移除过期的会话"""
        with self._lock:
            current_time = datetime.datetime.utcnow()
            expired_tokens = []
            
            # 检查活跃会话，移除过期的
            for token, session in list(self._active_sessions.items()):
                if session['expires_at'] <= current_time:
                    expired_tokens.append(token)
            
            # 移除过期会话
            for token in expired_tokens:
                self._active_sessions.pop(token, None)
            
            if expired_tokens:
                print(f"Cleaned up {len(expired_tokens)} expired sessions")
    
    def _remove_expired_tokens(self):
        """专注于会话清理，不再处理黑名单清理
        
        注意：黑名单清理已移至BlacklistManager的自动清理机制
        """
        # 此方法现在专注于会话管理，黑名单清理由BlacklistManager负责
        pass
    
    def register_session(self, user_id: int, token: str, expires_at: datetime.datetime):
        """注册活跃会话"""
        with self._lock:
            self._active_sessions[token] = {
                'user_id': user_id,
                'expires_at': expires_at,
                'last_activity': datetime.datetime.utcnow()
            }
    
    def update_session_activity(self, token: str):
        """更新会话活动时间"""
        with self._lock:
            if token in self._active_sessions:
                self._active_sessions[token]['last_activity'] = datetime.datetime.utcnow()
    
    def remove_session(self, token: str):
        """移除会话"""
        with self._lock:
            self._active_sessions.pop(token, None)
    
    def get_active_sessions_count(self, user_id: int = None) -> int:
        """获取活跃会话数量"""
        with self._lock:
            if user_id is None:
                return len(self._active_sessions)
            
            count = 0
            for session in self._active_sessions.values():
                if session['user_id'] == user_id:
                    count += 1
            return count
    
    def get_user_sessions(self, user_id: int) -> list:
        """获取用户的所有活跃会话"""
        with self._lock:
            sessions = []
            current_time = datetime.datetime.utcnow()
            
            for token, session in self._active_sessions.items():
                if session['user_id'] == user_id:
                    # 检查会话是否过期
                    if session['expires_at'] > current_time:
                        sessions.append({
                            'token': token[:20] + '...',  # 只显示部分token
                            'expires_at': session['expires_at'],
                            'last_activity': session['last_activity']
                        })
            
            return sessions
    
    def revoke_user_sessions(self, user_id: int, exclude_token: str = None) -> int:
        """撤销用户的所有会话（除了指定的token）"""
        with self._lock:
            revoked_count = 0
            tokens_to_revoke = []
            
            for token, session in self._active_sessions.items():
                if session['user_id'] == user_id and token != exclude_token:
                    tokens_to_revoke.append(token)
            
            for token in tokens_to_revoke:
                JWTManager.revoke_token(token)
                self._active_sessions.pop(token, None)
                revoked_count += 1
            
            return revoked_count
    
    def check_session_timeout(self, token: str, timeout_minutes: int = 30) -> bool:
        """检查会话是否超时"""
        with self._lock:
            session = self._active_sessions.get(token)
            if not session:
                return True  # 会话不存在，视为超时
            
            current_time = datetime.datetime.utcnow()
            last_activity = session['last_activity']
            timeout_delta = datetime.timedelta(minutes=timeout_minutes)
            
            return current_time - last_activity > timeout_delta
    
    def get_session_info(self, token: str) -> dict:
        """获取会话信息"""
        with self._lock:
            session = self._active_sessions.get(token)
            if not session:
                return None
            
            current_time = datetime.datetime.utcnow()
            return {
                'user_id': session['user_id'],
                'expires_at': session['expires_at'],
                'last_activity': session['last_activity'],
                'is_expired': session['expires_at'] <= current_time,
                'time_until_expiry': (session['expires_at'] - current_time).total_seconds() if session['expires_at'] > current_time else 0
            }


# 全局会话管理器实例
session_manager = SessionManager()


def init_session_manager(app):
    """初始化会话管理器"""
    with app.app_context():
        session_manager.start_cleanup_thread()
        app.logger.info("Session manager initialized and cleanup thread started")


def cleanup_session_manager():
    """清理会话管理器"""
    session_manager.stop_cleanup_thread()