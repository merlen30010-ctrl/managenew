from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.utils.query_monitor import query_monitor
from app.views.decorators import permission_required

query_monitor_bp = Blueprint('query_monitor', __name__)

@query_monitor_bp.route('/')
@login_required
@permission_required('system_monitor')
def dashboard():
    """查询监控仪表板"""
    return render_template('query_monitor/dashboard.html')

@query_monitor_bp.route('/api/stats')
@login_required
@permission_required('system_monitor')
def get_stats():
    """获取查询统计信息"""
    limit = request.args.get('limit', 20, type=int)
    stats = query_monitor.get_query_stats(limit)
    return jsonify({
        'success': True,
        'data': stats
    })

@query_monitor_bp.route('/api/slow-queries')
@login_required
@permission_required('system_monitor')
def get_slow_queries():
    """获取慢查询列表"""
    limit = request.args.get('limit', 50, type=int)
    slow_queries = query_monitor.get_slow_queries(limit)
    
    # 格式化时间戳
    for query in slow_queries:
        query['timestamp'] = query['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'success': True,
        'data': slow_queries
    })

@query_monitor_bp.route('/api/recent-queries')
@login_required
@permission_required('system_monitor')
def get_recent_queries():
    """获取最近查询列表"""
    limit = request.args.get('limit', 100, type=int)
    recent_queries = query_monitor.get_recent_queries(limit)
    
    # 格式化时间戳
    for query in recent_queries:
        query['timestamp'] = query['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'success': True,
        'data': recent_queries
    })

@query_monitor_bp.route('/api/performance-report')
@login_required
@permission_required('system_monitor')
def get_performance_report():
    """获取性能报告"""
    report = query_monitor.generate_performance_report()
    return jsonify({
        'success': True,
        'data': report
    })

@query_monitor_bp.route('/api/clear-stats', methods=['POST'])
@login_required
@permission_required('system_monitor')
def clear_stats():
    """清除统计数据"""
    query_monitor.clear_stats()
    return jsonify({
        'success': True,
        'message': '统计数据已清除'
    })