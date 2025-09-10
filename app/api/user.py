# 用户管理相关API路由
from flask import Blueprint, jsonify, request, g
from app import db
from app.models.user import User
from flask_login import current_user
from app.api.decorators import api_login_required, permission_required
import logging

# 创建用户API蓝图
api_user_bp = Blueprint('api_user', __name__, url_prefix='/api')

# 配置日志
logger = logging.getLogger(__name__)

@api_user_bp.route('/users/me', methods=['GET'])
@api_login_required
def get_current_user():
    """获取当前登录用户信息"""
    return jsonify({
        'success': True,
        'data': {
            'id': current_user.id,
            'username': current_user.username,
    
            'name': current_user.name,
            'roles': [role.name for role in current_user.roles] if hasattr(current_user, 'roles') else []
        }
    })

@api_user_bp.route('/users', methods=['GET'])
@api_login_required
@permission_required('user_read')
def get_users():
    """获取用户列表"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [{
                'id': user.id,
                'username': user.username,
    
                'name': user.name
            } for user in users]
        })
    except Exception as e:
        logger.error(f"获取用户列表时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

@api_user_bp.route('/users/<int:user_id>', methods=['GET'])
@api_login_required
@permission_required('user_read')
def get_user(user_id):
    """获取指定用户信息"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
        
                'name': user.name
            }
        })
    except Exception as e:
        logger.error(f"获取用户信息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@api_user_bp.route('/users', methods=['POST'])
@api_login_required
@permission_required('user_create')
def create_user():
    """创建新用户"""
    try:
        data = request.get_json()
        
        # 检查必填字段
        if not data or not data.get('username'):
            return jsonify({
                'success': False,
                'message': '用户名是必填字段'
            }), 400
        
        # 检查用户是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400
        
        # 创建新用户
        user = User()
        user.username = data['username']
        if data.get('name'):
            user.name = data['name']
        
        if data.get('password'):
            user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # 自动为新用户分配员工角色
        from app.models.role import Role
        employee_role = Role.query.filter_by(name='员工').first()
        if employee_role:
            user.roles.append(employee_role)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'data': {
                'id': user.id,
                'username': user.username,
    
                'name': user.name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建用户时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建用户失败: {str(e)}'
        }), 500

@api_user_bp.route('/users/<int:user_id>', methods=['PUT'])
@api_login_required
@permission_required('user_update')
def update_user(user_id):
    """更新用户信息"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '没有提供更新数据'
            }), 400
        
        # 更新用户信息
        if 'username' in data:
            # 禁止修改任何用户的用户名
            return jsonify({
                'success': False,
                'message': '用户名不允许修改'
            }), 400
        

        
        if 'name' in data:
            user.name = data['name']
        
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
    
                'name': user.name
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新用户失败: {str(e)}'
        }), 500

@api_user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@api_login_required
@permission_required('user_delete')
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 防止删除当前登录用户
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'message': '不能删除当前登录用户'
            }), 400
        
        # 防止删除admin用户
        if user.username == 'admin':
            return jsonify({
                'success': False,
                'message': '不能删除系统管理员admin用户'
            }), 400
        
        # 防止删除最后一个超级管理员
        if user.is_superuser:
            superuser_count = User.query.filter_by(is_superuser=True).count()
            if superuser_count <= 1:
                return jsonify({
                    'success': False,
                    'message': '不能删除最后一个超级管理员'
                }), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除用户时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500