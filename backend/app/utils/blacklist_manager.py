# -*- coding: utf-8 -*-
"""
Token黑名单管理器
提供token黑名单的持久化存储和管理功能
"""

import json
import os
import threading
import datetime
from typing import Set, Dict
from flask import current_app


class BlacklistManager:
    """Token黑名单管理器"""
    
    def __init__(self, blacklist_file: str = None):
        self._blacklist_file = blacklist_file or 'token_blacklist.json'
        self._blacklist: Set[str] = set()
        self._blacklist_metadata: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._load_blacklist()
    
    def _get_blacklist_path(self) -> str:
        """获取黑名单文件的完整路径"""
        try:
            # 尝试使用Flask应用的实例路径
            instance_path = current_app.instance_path
            return os.path.join(instance_path, self._blacklist_file)
        except RuntimeError:
            # 如果不在应用上下文中，使用当前目录
            return os.path.join(os.getcwd(), 'instance', self._blacklist_file)
    
    def _load_blacklist(self):
        """从文件加载黑名单"""
        blacklist_path = self._get_blacklist_path()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(blacklist_path), exist_ok=True)
            
            if os.path.exists(blacklist_path):
                with open(blacklist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._blacklist = set(data.get('blacklist', []))
                    self._blacklist_metadata = data.get('metadata', {})
                    
                    # 清理过期的黑名单项
                    self._cleanup_expired_entries()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load blacklist from {blacklist_path}: {e}")
            self._blacklist = set()
            self._blacklist_metadata = {}
    
    def _save_blacklist(self):
        """保存黑名单到文件"""
        blacklist_path = self._get_blacklist_path()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(blacklist_path), exist_ok=True)
            
            data = {
                'blacklist': list(self._blacklist),
                'metadata': self._blacklist_metadata,
                'last_updated': datetime.datetime.utcnow().isoformat()
            }
            
            # 写入临时文件，然后重命名（原子操作）
            temp_path = blacklist_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            os.replace(temp_path, blacklist_path)
        except IOError as e:
            print(f"Warning: Failed to save blacklist to {blacklist_path}: {e}")
    
    def _cleanup_expired_entries(self):
        """清理过期的黑名单条目"""
        current_time = datetime.datetime.utcnow()
        expired_jtis = []
        
        for jti in list(self._blacklist):
            metadata = self._blacklist_metadata.get(jti, {})
            expires_at_str = metadata.get('expires_at')
            
            if expires_at_str:
                try:
                    expires_at = datetime.datetime.fromisoformat(expires_at_str)
                    # 如果token已过期超过24小时，从黑名单中移除
                    if current_time - expires_at > datetime.timedelta(hours=24):
                        expired_jtis.append(jti)
                except ValueError:
                    # 如果时间格式不正确，也移除
                    expired_jtis.append(jti)
            else:
                # 如果没有过期时间信息，检查添加时间
                added_at_str = metadata.get('added_at')
                if added_at_str:
                    try:
                        added_at = datetime.datetime.fromisoformat(added_at_str)
                        # 如果添加时间超过7天，移除
                        if current_time - added_at > datetime.timedelta(days=7):
                            expired_jtis.append(jti)
                    except ValueError:
                        expired_jtis.append(jti)
        
        # 移除过期条目
        for jti in expired_jtis:
            self._blacklist.discard(jti)
            self._blacklist_metadata.pop(jti, None)
        
        if expired_jtis:
            print(f"Cleaned up {len(expired_jtis)} expired blacklist entries")
    
    def add_token(self, jti: str, reason: str = None, expires_at: datetime.datetime = None, user_id: int = None):
        """添加token到黑名单"""
        with self._lock:
            self._blacklist.add(jti)
            
            # 记录元数据
            metadata = {
                'added_at': datetime.datetime.utcnow().isoformat(),
                'reason': reason or 'manual_revocation'
            }
            
            if expires_at:
                metadata['expires_at'] = expires_at.isoformat()
            
            if user_id:
                metadata['user_id'] = user_id
            
            self._blacklist_metadata[jti] = metadata
            
            # 保存到文件
            self._save_blacklist()
    
    def remove_token(self, jti: str) -> bool:
        """从黑名单中移除token"""
        with self._lock:
            if jti in self._blacklist:
                self._blacklist.remove(jti)
                self._blacklist_metadata.pop(jti, None)
                self._save_blacklist()
                return True
            return False
    
    def add_to_blacklist(self, jti: str, expires_at: datetime.datetime = None) -> None:
        """添加token到黑名单"""
        with self._lock:
            if jti not in self._blacklist:
                self._blacklist.add(jti)
                self._blacklist_metadata[jti] = {
                    'added_at': datetime.datetime.utcnow().isoformat(),
                    'expires_at': expires_at.isoformat() if expires_at else None
                }
                self._save_blacklist()
    
    def remove_from_blacklist(self, jti: str) -> None:
        """从黑名单中移除token"""
        with self._lock:
            if jti in self._blacklist:
                self._blacklist.remove(jti)
                if jti in self._blacklist_metadata:
                    del self._blacklist_metadata[jti]
                self._save_blacklist()
    
    def is_blacklisted(self, jti: str) -> bool:
        """检查token是否在黑名单中"""
        with self._lock:
            return jti in self._blacklist
    
    def get_blacklist_info(self, jti: str) -> dict:
        """获取黑名单条目的详细信息"""
        with self._lock:
            if jti in self._blacklist:
                return self._blacklist_metadata.get(jti, {})
            return None
    
    def get_blacklist_count(self) -> int:
        """获取黑名单条目数量"""
        with self._lock:
            return len(self._blacklist)
    
    def get_user_blacklisted_tokens(self, user_id: int) -> list:
        """获取指定用户的黑名单token"""
        with self._lock:
            user_tokens = []
            for jti, metadata in self._blacklist_metadata.items():
                if metadata.get('user_id') == user_id and jti in self._blacklist:
                    user_tokens.append({
                        'jti': jti,
                        'added_at': metadata.get('added_at'),
                        'reason': metadata.get('reason'),
                        'expires_at': metadata.get('expires_at')
                    })
            return user_tokens
    
    def cleanup_expired(self) -> int:
        """手动清理过期条目，返回清理的数量"""
        with self._lock:
            initial_count = len(self._blacklist)
            self._cleanup_expired_entries()
            cleaned_count = initial_count - len(self._blacklist)
            
            if cleaned_count > 0:
                self._save_blacklist()
            
            return cleaned_count
    
    def clear_all(self):
        """清空所有黑名单（谨慎使用）"""
        with self._lock:
            self._blacklist.clear()
            self._blacklist_metadata.clear()
            self._save_blacklist()
    
    def export_blacklist(self) -> dict:
        """导出黑名单数据"""
        with self._lock:
            return {
                'blacklist': list(self._blacklist),
                'metadata': self._blacklist_metadata.copy(),
                'exported_at': datetime.datetime.utcnow().isoformat(),
                'total_count': len(self._blacklist)
            }
    
    def import_blacklist(self, data: dict, merge: bool = True):
        """导入黑名单数据"""
        with self._lock:
            if not merge:
                self._blacklist.clear()
                self._blacklist_metadata.clear()
            
            imported_blacklist = set(data.get('blacklist', []))
            imported_metadata = data.get('metadata', {})
            
            self._blacklist.update(imported_blacklist)
            self._blacklist_metadata.update(imported_metadata)
            
            # 清理过期条目
            self._cleanup_expired_entries()
            
            # 保存到文件
            self._save_blacklist()


# 全局黑名单管理器实例
blacklist_manager = BlacklistManager()


def init_blacklist_manager(app):
    """初始化黑名单管理器"""
    with app.app_context():
        # 设置黑名单文件路径
        blacklist_file = app.config.get('JWT_BLACKLIST_FILE', 'token_blacklist.json')
        global blacklist_manager
        blacklist_manager = BlacklistManager(blacklist_file)
        app.logger.info(f"Blacklist manager initialized with {blacklist_manager.get_blacklist_count()} entries")


def cleanup_blacklist_manager():
    """清理黑名单管理器"""
    try:
        cleaned_count = blacklist_manager.cleanup_expired()
        print(f"Blacklist cleanup completed, removed {cleaned_count} expired entries")
    except Exception as e:
        print(f"Blacklist cleanup error: {e}")