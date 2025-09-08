from functools import wraps
from flask import jsonify, request, g, current_app
from flask_login import current_user
from app.models.permission import Permission
from app.models.user import User
from app.utils.jwt_utils import JWTManager
from app.utils.session_manager import session_manager

def api_login_required(f):
    """API身份验证装饰器 - 支持JWT token和session验证"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 首先检查JWT token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = JWTManager.verify_token(token)
            
            if payload:
                # JWT验证成功，设置当前用户
                user_id = payload.get('user_id')
                user = User.query.get(user_id)
                if user:
                    # 检查会话超时
                    timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
                    if session_manager.check_session_timeout(token, timeout_minutes):
                        # 会话超时，撤销token
                        JWTManager.revoke_token(token)
                        return jsonify({
                            'success': False,
                            'message': '会话超时',
                            'error_code': 'SESSION_TIMEOUT'
                        }), 401
                    
                    # 更新会话活动时间
                    session_manager.update_session_activity(token)
                    
                    g.current_user = user
                    g.auth_method = 'jwt'
                    g.current_token = token
                    return f(*args, **kwargs)
            
            # JWT验证失败
            return jsonify({
                'success': False,
                'message': 'Token无效或已过期',
                'error_code': 'INVALID_TOKEN'
            }), 401
        
        # 如果没有JWT token，检查session登录
        if current_user.is_authenticated:
            g.current_user = current_user
            g.auth_method = 'session'
            return f(*args, **kwargs)
        
        # 都没有，返回未授权
        return jsonify({
            'success': False,
            'message': '需要登录才能访问此资源',
            'error_code': 'UNAUTHORIZED'
        }), 401
    return decorated_function

def permission_required(permission_name):
    """API权限检查装饰器 - 支持JWT token和session验证"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 首先进行身份验证
            auth_header = request.headers.get('Authorization')
            user = None
            
            if auth_header and auth_header.startswith('Bearer '):
                # JWT验证
                token = auth_header.split(' ')[1]
                payload = JWTManager.verify_token(token)
                
                if payload:
                    user_id = payload.get('user_id')
                    user = User.query.get(user_id)
                
                if not user:
                    return jsonify({
                        'success': False,
                        'message': 'Token无效或已过期',
                        'error_code': 'INVALID_TOKEN'
                    }), 401
            elif current_user.is_authenticated:
                # Session验证
                user = current_user
            else:
                return jsonify({
                    'success': False,
                    'message': '需要登录才能访问此资源',
                    'error_code': 'UNAUTHORIZED'
                }), 401
            
            # 检查用户是否具有指定权限
            permission = Permission.query.filter_by(name=permission_name).first()
            if not permission or not user.has_permission(permission):
                return jsonify({
                    'success': False,
                    'message': f'缺少权限: {permission_name}',
                    'error_code': 'INSUFFICIENT_PERMISSIONS'
                }), 403
            
            # 设置当前用户到g对象
            g.current_user = user
            g.auth_method = 'jwt' if auth_header else 'session'
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator