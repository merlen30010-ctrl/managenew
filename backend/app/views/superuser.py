from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from functools import wraps

superuser_view_bp = Blueprint('superuser_view', __name__)

def superuser_required(f):
    """超级管理员权限装饰器（视图用）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_superuser:
            flash('需要超级管理员权限才能访问此页面', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@superuser_view_bp.route('/management')
@login_required
@superuser_required
def management():
    """超级管理员管理页面"""
    return render_template('superuser_management.html')

@superuser_view_bp.route('/status')
@login_required
def status():
    """查看当前用户的超级管理员状态"""
    user_info = {
        'id': current_user.id,
        'username': current_user.username,
        'is_superuser': current_user.is_superuser,
        'is_active': current_user.is_active,
        'roles': [role.name for role in current_user.roles],
        'permission_count': len(current_user.get_all_permissions())
    }
    
    return render_template('superuser_status.html', user_info=user_info)