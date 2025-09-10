from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.utils.validators import validate_required_fields
from functools import wraps

superuser_bp = Blueprint('superuser_api', __name__)

def superuser_required(f):
    """超级管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superuser:
            return jsonify({'error': '需要超级管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

@superuser_bp.route('/list', methods=['GET'])
@login_required
@superuser_required
def list_superusers():
    """获取所有超级管理员列表"""
    try:
        superusers = User.get_superusers()
        return jsonify({
            'success': True,
            'data': [{
                'id': user.id,
                'username': user.username,
        
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            } for user in superusers],
            'total': len(superusers)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@superuser_bp.route('/set/<int:user_id>', methods=['POST'])
@login_required
@superuser_required
def set_superuser(user_id):
    """设置用户为超级管理员"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 检查用户是否已经是超级管理员
        if user.is_superuser:
            return jsonify({
                'success': False,
                'error': f'用户 {user.username} 已经是超级管理员'
            }), 400
        
        # 设置为超级管理员
        user.set_superuser(True)
        
        return jsonify({
            'success': True,
            'message': f'用户 {user.username} 已设置为超级管理员',
            'data': {
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@superuser_bp.route('/unset/<int:user_id>', methods=['POST'])
@login_required
@superuser_required
def unset_superuser(user_id):
    """取消用户的超级管理员权限"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 检查是否为当前用户
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'error': '不能取消自己的超级管理员权限'
            }), 400
        
        # 检查是否为最后一个超级管理员
        superuser_count = User.query.filter_by(is_superuser=True).count()
        if superuser_count <= 1:
            return jsonify({
                'success': False,
                'error': '至少需要保留一个超级管理员'
            }), 400
        
        # 检查用户是否是超级管理员
        if not user.is_superuser:
            return jsonify({
                'success': False,
                'error': f'用户 {user.username} 不是超级管理员'
            }), 400
        
        # 取消超级管理员权限
        user.set_superuser(False)
        
        return jsonify({
            'success': True,
            'message': f'用户 {user.username} 的超级管理员权限已取消',
            'data': {
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@superuser_bp.route('/status/<int:user_id>', methods=['GET'])
@login_required
@superuser_required
def check_superuser_status(user_id):
    """检查用户的超级管理员状态"""
    try:
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'roles': [role.name for role in user.roles],
                'permission_count': len(user.get_all_permissions())
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@superuser_bp.route('/current', methods=['GET'])
@login_required
def current_superuser_status():
    """获取当前用户的超级管理员状态"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'id': current_user.id,
                'username': current_user.username,
                'is_superuser': current_user.is_superuser,
                'is_active': current_user.is_active,
                'roles': [role.name for role in current_user.roles]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500