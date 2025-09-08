import redis
import json
import hashlib
from datetime import timedelta
from flask import current_app
from typing import Any, Optional, Dict, List
from functools import wraps

class CacheService:
    """Redis缓存服务"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
    
    def init_app(self, app):
        """初始化Redis连接"""
        try:
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # 测试连接
            self.redis_client.ping()
            self.enabled = True
            app.logger.info("Redis缓存服务已启用")
        except Exception as e:
            app.logger.warning(f"Redis连接失败，缓存功能已禁用: {e}")
            self.enabled = False
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.enabled:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            current_app.logger.error(f"缓存获取失败: {e}")
        return None
    
    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """设置缓存"""
        if not self.enabled:
            return False
        
        try:
            data = json.dumps(value, default=str)
            return self.redis_client.setex(key, expire, data)
        except Exception as e:
            current_app.logger.error(f"缓存设置失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            current_app.logger.error(f"缓存删除失败: {e}")
            return False
    
    def clear_all(self) -> bool:
        """清除所有缓存（仅开发环境使用）"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            current_app.logger.error(f"清除缓存失败: {e}")
            return False
    
    def cache_query_result(self, prefix: str, expire: int = 300):
        """简单查询结果缓存装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 如果缓存未启用，直接执行函数
                if not self.enabled:
                    return func(*args, **kwargs)
                
                # 生成简单缓存键
                cache_key = self._generate_key(prefix, args=args, kwargs=kwargs)
                
                # 尝试从缓存获取
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # 执行查询
                result = func(*args, **kwargs)
                
                # 缓存结果
                if result is not None:
                    self.set(cache_key, result, expire)
                
                return result
            return wrapper
        return decorator
    
# 简化的缓存服务实例
cache_service = CacheService()

# 简化的缓存超时配置
CACHE_TIMEOUT = {
    'SHORT': 60,    # 1分钟
    'MEDIUM': 300,  # 5分钟
    'LONG': 1800    # 30分钟
}