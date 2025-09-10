from flask import request
from sqlalchemy import desc, asc
from sqlalchemy.orm import joinedload
from typing import Optional, Dict, Any, List, Tuple
from app import db
from app.utils.cache_service import cache_service, CACHE_TIMEOUT

class PaginationService:
    """统一分页查询服务"""
    
    def __init__(self, page_size: int = 20, max_page_size: int = 100):
        self.page_size = page_size
        self.max_page_size = max_page_size
    
    def get_pagination_params(self) -> Tuple[int, int]:
        """从请求参数中获取分页参数"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', self.page_size, type=int)
        
        # 限制每页最大数量
        per_page = min(per_page, self.max_page_size)
        
        return page, per_page
    
    def get_sort_params(self, default_sort: str = 'created_at', 
                       allowed_sorts: Optional[List[str]] = None) -> Tuple[str, str]:
        """从请求参数中获取排序参数"""
        sort_by = request.args.get('sort_by', default_sort)
        sort_order = request.args.get('sort_order', 'desc')
        
        # 验证排序字段
        if allowed_sorts and sort_by not in allowed_sorts:
            sort_by = default_sort
        
        # 验证排序方向
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        return sort_by, sort_order
    
    def apply_sorting(self, query, model_class, sort_by: str, sort_order: str):
        """应用排序到查询"""
        if hasattr(model_class, sort_by):
            sort_column = getattr(model_class, sort_by)
            if sort_order == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        return query
    
    def paginate_query(self, query, model_class, 
                      default_sort: str = 'created_at',
                      allowed_sorts: Optional[List[str]] = None,
                      eager_load: Optional[List[str]] = None,
                      use_cache: bool = False,
                      cache_timeout: Optional[int] = None) -> Dict[str, Any]:
        """执行分页查询
        
        Args:
            query: SQLAlchemy查询对象
            model_class: 模型类
            default_sort: 默认排序字段
            allowed_sorts: 允许的排序字段列表
            eager_load: 需要预加载的关联关系列表
            use_cache: 是否使用缓存
            cache_timeout: 缓存超时时间
        
        Returns:
            包含分页数据和元信息的字典
        """
        # 获取分页参数
        page, per_page = self.get_pagination_params()
        
        # 获取排序参数
        sort_by, sort_order = self.get_sort_params(default_sort, allowed_sorts)
        
        # 简化的缓存处理（可选）
        cache_key = None
        if use_cache and cache_service.enabled:
            cache_key = f"{model_class.__name__}_page_{page}_{per_page}_{sort_by}_{sort_order}"
            cached_result = cache_service.get(cache_key)
            if cached_result:
                return cached_result
        
        # 应用预加载
        if eager_load:
            for relation in eager_load:
                if hasattr(model_class, relation):
                    query = query.options(joinedload(getattr(model_class, relation)))
        
        # 应用排序
        query = self.apply_sorting(query, model_class, sort_by, sort_order)
        
        # 执行分页查询
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = {
            'items': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        # 简化的缓存设置
        if use_cache and cache_key and cache_service.enabled:
            timeout = cache_timeout or CACHE_TIMEOUT['MEDIUM']
            cache_result = result.copy()
            cache_result['items'] = [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in pagination.items]
            cache_service.set(cache_key, cache_result, timeout)
        
        return result
    
    def build_filter_query(self, base_query, model_class, filters: Dict[str, Any]):
        """构建筛选查询
        
        Args:
            base_query: 基础查询对象
            model_class: 模型类
            filters: 筛选条件字典
        
        Returns:
            应用筛选条件后的查询对象
        """
        query = base_query
        
        for field, value in filters.items():
            if value is None or value == '':
                continue
                
            if hasattr(model_class, field):
                column = getattr(model_class, field)
                
                # 根据字段类型应用不同的筛选逻辑
                if isinstance(value, str):
                    # 字符串字段使用模糊匹配
                    query = query.filter(column.contains(value))
                elif isinstance(value, (int, float)):
                    # 数值字段使用精确匹配
                    query = query.filter(column == value)
                elif isinstance(value, list):
                    # 列表值使用IN查询
                    query = query.filter(column.in_(value))
                elif isinstance(value, dict):
                    # 字典值支持范围查询
                    if 'min' in value and value['min'] is not None:
                        query = query.filter(column >= value['min'])
                    if 'max' in value and value['max'] is not None:
                        query = query.filter(column <= value['max'])
        
        return query
    
    def get_filter_params(self, allowed_filters: List[str]) -> Dict[str, Any]:
        """从请求参数中获取筛选参数"""
        filters = {}
        
        for filter_name in allowed_filters:
            value = request.args.get(filter_name)
            if value is not None and value != '':
                filters[filter_name] = value
        
        return filters

# 全局分页服务实例
pagination_service = PaginationService()