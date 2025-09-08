import time
import logging
from datetime import datetime, timedelta
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask import current_app, g
from typing import Dict, List, Optional
import threading
from collections import defaultdict, deque

class QueryMonitor:
    """数据库查询监控服务"""
    
    def __init__(self):
        self.enabled = False
        self.slow_query_threshold = 1.0  # 慢查询阈值（秒）
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'avg_time': 0,
            'max_time': 0,
            'min_time': float('inf')
        })
        self.recent_queries = deque(maxlen=1000)  # 保留最近1000条查询
        self.lock = threading.Lock()
        
        # 设置慢查询日志
        self.slow_query_logger = logging.getLogger('slow_queries')
        self.slow_query_logger.setLevel(logging.WARNING)
        
        # 设置查询统计日志
        self.stats_logger = logging.getLogger('query_stats')
        self.stats_logger.setLevel(logging.INFO)
    
    def init_app(self, app):
        """初始化查询监控"""
        self.enabled = app.config.get('ENABLE_QUERY_MONITORING', False)
        self.slow_query_threshold = app.config.get('SLOW_QUERY_THRESHOLD', 1.0)
        
        if self.enabled:
            self._setup_logging(app)
            self._setup_sqlalchemy_events()
            app.logger.info(f"数据库查询监控已启用，慢查询阈值: {self.slow_query_threshold}秒")
        else:
            app.logger.info("数据库查询监控已禁用")
    
    def _setup_logging(self, app):
        """设置日志配置"""
        import os
        
        # 创建日志目录
        log_dir = os.path.join(app.instance_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 慢查询日志文件处理器
        slow_query_handler = logging.FileHandler(
            os.path.join(log_dir, 'slow_queries.log')
        )
        slow_query_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.slow_query_logger.addHandler(slow_query_handler)
        
        # 查询统计日志文件处理器
        stats_handler = logging.FileHandler(
            os.path.join(log_dir, 'query_stats.log')
        )
        stats_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.stats_logger.addHandler(stats_handler)
    
    def _setup_sqlalchemy_events(self):
        """设置SQLAlchemy事件监听"""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if self.enabled:
                g.query_start_time = time.time()
                g.query_statement = statement
        
        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if self.enabled and hasattr(g, 'query_start_time'):
                execution_time = time.time() - g.query_start_time
                self._record_query(statement, execution_time, parameters)
    
    def _record_query(self, statement: str, execution_time: float, parameters=None):
        """记录查询信息"""
        with self.lock:
            # 简化SQL语句用于统计
            simplified_sql = self._simplify_sql(statement)
            
            # 更新统计信息
            stats = self.query_stats[simplified_sql]
            stats['count'] += 1
            stats['total_time'] += execution_time
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['max_time'] = max(stats['max_time'], execution_time)
            stats['min_time'] = min(stats['min_time'], execution_time)
            
            # 记录查询详情
            query_info = {
                'timestamp': datetime.now(),
                'sql': statement,
                'execution_time': execution_time,
                'parameters': str(parameters) if parameters else None
            }
            self.recent_queries.append(query_info)
            
            # 记录慢查询
            if execution_time > self.slow_query_threshold:
                self._log_slow_query(query_info)
    
    def _simplify_sql(self, sql: str) -> str:
        """简化SQL语句用于统计分组"""
        # 移除参数占位符和具体值
        import re
        
        # 移除换行和多余空格
        sql = re.sub(r'\s+', ' ', sql.strip())
        
        # 替换参数占位符
        sql = re.sub(r'\?|%\([^)]+\)s|:\w+', '?', sql)
        
        # 替换具体数值
        sql = re.sub(r'\b\d+\b', '?', sql)
        
        # 替换字符串字面量
        sql = re.sub(r"'[^']*'", "'?'", sql)
        sql = re.sub(r'"[^"]*"', '"?"', sql)
        
        return sql[:200]  # 限制长度
    
    def _log_slow_query(self, query_info: Dict):
        """记录慢查询"""
        self.slow_query_logger.warning(
            f"慢查询检测 - 执行时间: {query_info['execution_time']:.3f}秒 | "
            f"SQL: {query_info['sql'][:500]}{'...' if len(query_info['sql']) > 500 else ''}"
        )
    
    def get_query_stats(self, limit: int = 20) -> List[Dict]:
        """获取查询统计信息"""
        with self.lock:
            stats_list = []
            for sql, stats in self.query_stats.items():
                stats_list.append({
                    'sql': sql,
                    'count': stats['count'],
                    'total_time': round(stats['total_time'], 3),
                    'avg_time': round(stats['avg_time'], 3),
                    'max_time': round(stats['max_time'], 3),
                    'min_time': round(stats['min_time'], 3) if stats['min_time'] != float('inf') else 0
                })
            
            # 按平均执行时间排序
            stats_list.sort(key=lambda x: x['avg_time'], reverse=True)
            return stats_list[:limit]
    
    def get_slow_queries(self, limit: int = 50) -> List[Dict]:
        """获取慢查询列表"""
        with self.lock:
            slow_queries = [
                query for query in self.recent_queries 
                if query['execution_time'] > self.slow_query_threshold
            ]
            
            # 按执行时间排序
            slow_queries.sort(key=lambda x: x['execution_time'], reverse=True)
            return slow_queries[:limit]
    
    def get_recent_queries(self, limit: int = 100) -> List[Dict]:
        """获取最近查询列表"""
        with self.lock:
            recent = list(self.recent_queries)[-limit:]
            recent.reverse()  # 最新的在前
            return recent
    
    def clear_stats(self):
        """清除统计数据"""
        with self.lock:
            self.query_stats.clear()
            self.recent_queries.clear()
            current_app.logger.info("查询监控统计数据已清除")
    
    def generate_performance_report(self) -> Dict:
        """生成性能报告"""
        with self.lock:
            total_queries = sum(stats['count'] for stats in self.query_stats.values())
            total_time = sum(stats['total_time'] for stats in self.query_stats.values())
            
            slow_query_count = len([
                query for query in self.recent_queries 
                if query['execution_time'] > self.slow_query_threshold
            ])
            
            return {
                'total_queries': total_queries,
                'total_execution_time': round(total_time, 3),
                'avg_execution_time': round(total_time / total_queries, 3) if total_queries > 0 else 0,
                'slow_query_count': slow_query_count,
                'slow_query_percentage': round(slow_query_count / total_queries * 100, 2) if total_queries > 0 else 0,
                'unique_queries': len(self.query_stats),
                'monitoring_enabled': self.enabled,
                'slow_query_threshold': self.slow_query_threshold
            }

# 创建全局查询监控实例
query_monitor = QueryMonitor()