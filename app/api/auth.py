# 认证相关API路由
from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from flask_login import login_user, logout_user, current_user
from app.api.decorators import api_login_required
from app.utils.jwt_utils import JWTManager
from app.utils.session_manager import session_manager
from app.utils.blacklist_manager import blacklist_manager
import logging

# 创建认证API蓝图
api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api')

# 配置日志
logger = logging.getLogger(__name__)

@api_auth_bp.route('/login', methods=['POST'])
def api_login():
    """API登录接口"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': '用户名和密码不能为空'
        }), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        
        # 生成JWT token
        token = JWTManager.generate_token(user.id, user.username)
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'name': user.name
                }
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

@api_auth_bp.route('/register', methods=['POST'])
def api_register():
    """API注册接口"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': '用户名、邮箱和密码不能为空'
        }), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'success': False,
            'message': '用户名已存在'
        }), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'success': False,
            'message': '邮箱已存在'
        }), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        name=data.get('name', data['username'])
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '注册成功',
        'data': {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name
            }
        }
    })

@api_auth_bp.route('/logout', methods=['POST'])
@api_login_required
def api_logout():
    """API登出接口"""
    try:
        # 获取当前token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # 将token加入黑名单
            JWTManager.blacklist_token(token)
        
        logout_user()
        return jsonify({
            'success': True,
            'message': '登出成功'
        })
    except Exception as e:
        logger.error(f"登出时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登出失败'
        }), 500

@api_auth_bp.route('/refresh-token', methods=['POST'])
def api_refresh_token():
    """刷新token接口"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '缺少Authorization头'}), 401
        
        old_token = auth_header.split(' ')[1]
        new_token = JWTManager.refresh_token(old_token)
        
        return jsonify({
            'success': True,
            'data': {
                'token': new_token
            }
        })
    except Exception as e:
        logger.error(f"刷新token时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 401

@api_auth_bp.route('/sessions', methods=['GET'])
@api_login_required
def get_user_sessions():
    """获取用户会话信息"""
    try:
        sessions = session_manager.get_user_sessions(current_user.id)
        return jsonify({
            'success': True,
            'data': {
                'sessions': sessions
            }
        })
    except Exception as e:
        logger.error(f"获取会话信息时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_auth_bp.route('/sessions/revoke-all', methods=['POST'])
@api_login_required
def revoke_all_sessions():
    """撤销所有会话"""
    try:
        session_manager.revoke_all_user_sessions(current_user.id)
        return jsonify({
            'success': True,
            'message': '所有会话已撤销'
        })
    except Exception as e:
        logger.error(f"撤销会话时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_auth_bp.route('/session/info', methods=['GET'])
@api_login_required
def get_session_info():
    """获取当前会话信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '缺少Authorization头'}), 401
        
        token = auth_header.split(' ')[1]
        payload = JWTManager.decode_token(token)
        
        if not payload:
            return jsonify({'error': 'Token无效'}), 401
        
        session_info = session_manager.get_session_info(payload.get('jti'))
        
        return jsonify({
            'success': True,
            'data': {
                'session_info': session_info,
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'jti': payload.get('jti'),
                'exp': payload.get('exp'),
                'iat': payload.get('iat')
            }
        })
    except Exception as e:
        logger.error(f"获取会话信息时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_auth_bp.route('/blacklist/info', methods=['GET'])
@api_login_required
def get_blacklist_info():
    """获取黑名单信息"""
    try:
        info = {
            'total_blacklisted': len(blacklist_manager._blacklist),
            'metadata_count': len(blacklist_manager._blacklist_metadata),
            'file_path': blacklist_manager.get_blacklist_path()
        }
        
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"获取黑名单信息时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_auth_bp.route('/blacklist/cleanup', methods=['POST'])
@api_login_required
def cleanup_blacklist():
    """清理过期的黑名单条目"""
    try:
        removed_count = blacklist_manager.cleanup_expired()
        
        return jsonify({
            'success': True,
            'message': f'清理完成，移除了 {removed_count} 个过期条目',
            'data': {
                'removed_count': removed_count,
                'remaining_count': len(blacklist_manager._blacklist)
            }
        })
    except Exception as e:
        logger.error(f"清理黑名单时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_auth_bp.route('/user/blacklisted-tokens', methods=['GET'])
@api_login_required
def get_user_blacklisted_tokens():
    """获取当前用户的黑名单token信息"""
    try:
        # 这里可以根据需要实现获取用户相关的黑名单token
        # 目前返回基本的黑名单统计信息
        info = {
            'total_blacklisted': len(blacklist_manager._blacklist)
        }
        
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"获取用户黑名单token时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500