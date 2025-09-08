from flask import current_app
from app.utils.cache_service import cache_service

def setup_cache_invalidation_hooks():
    """简化的缓存管理（小系统适用）"""
    # 对于小系统，使用简单的手动缓存清理
    # 或者设置较短的缓存时间来避免复杂的自动失效机制
    current_app.logger.info("缓存服务已启用，使用简化的缓存管理策略")
    
    # 提供手动清理缓存的方法
    def clear_cache_manually():
        """手动清理所有缓存"""
        if cache_service.enabled:
            cache_service.clear_all()
            current_app.logger.info("手动清理缓存完成")
    
    # 将清理方法添加到应用上下文
    current_app.clear_cache = clear_cache_manually