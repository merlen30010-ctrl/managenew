from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models.permission import Permission

def permission_required(permission_name):
    """视图权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录')
                return redirect(url_for('auth.login'))
            
            # 检查用户是否具有指定权限
            permission = Permission.query.filter_by(name=permission_name).first()
            if not permission or not current_user.has_permission(permission):
                flash('您没有权限访问此页面')
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """管理员权限检查装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录')
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为管理员
        if not current_user.is_admin:
            flash('您没有管理员权限访问此页面')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function