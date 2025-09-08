from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.models.notification import Notification
from app.models.user import User
from app.api.decorators import api_login_required, permission_required
from datetime import datetime

notification_bp = Blueprint('notification_api', __name__)

@notification_bp.route('/notifications', methods=['GET'])
@api_login_required
@permission_required('notification_read')
def get_notifications():
    """获取当前用户的通知列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        is_read = request.args.get('is_read', type=bool)
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
            
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': [{
                    'id': n.id,
                    'title': n.title,
                    'content': n.content,
                    'is_read': n.is_read,
                    'created_at': n.created_at.isoformat(),
                    'read_at': n.read_at.isoformat() if n.read_at else None
                } for n in notifications.items],
                'pagination': {
                    'page': notifications.page,
                    'pages': notifications.pages,
                    'per_page': notifications.per_page,
                    'total': notifications.total
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/notifications', methods=['POST'])
@api_login_required
@permission_required('notification_create')
def create_notification():
    """创建通知"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
            
        title = data.get('title')
        content = data.get('content')
        user_ids = data.get('user_ids', [])
        
        if not title:
            return jsonify({'success': False, 'message': '标题不能为空'}), 400
            
        if not user_ids:
            return jsonify({'success': False, 'message': '接收用户不能为空'}), 400
            
        # 验证用户ID是否存在
        users = User.query.filter(User.id.in_(user_ids)).all()
        if len(users) != len(user_ids):
            return jsonify({'success': False, 'message': '部分用户ID不存在'}), 400
            
        # 批量创建通知
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                title=title,
                content=content,
                user_id=user_id
            )
            notifications.append(notification)
            db.session.add(notification)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功创建 {len(notifications)} 条通知',
            'data': {
                'count': len(notifications)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@api_login_required
@permission_required('notification_read')
def mark_notification_read(notification_id):
    """标记通知为已读"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': '通知不存在'}), 404
            
        if notification.is_read:
            return jsonify({'success': False, 'message': '通知已经是已读状态'}), 400
            
        notification.is_read = True
        notification.read_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '通知已标记为已读',
            'data': {
                'id': notification.id,
                'is_read': notification.is_read,
                'read_at': notification.read_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/notifications/mark-all-read', methods=['PUT'])
@api_login_required
@permission_required('notification_read')
def mark_all_notifications_read():
    """标记所有通知为已读"""
    try:
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        count = 0
        for notification in unread_notifications:
            notification.is_read = True
            notification.read_at = datetime.now()
            count += 1
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功标记 {count} 条通知为已读',
            'data': {
                'count': count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@api_login_required
@permission_required('notification_delete')
def delete_notification(notification_id):
    """删除通知"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': '通知不存在'}), 404
            
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '通知删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/admin/notifications', methods=['GET'])
@api_login_required
@permission_required('notification_manage')
def get_all_notifications():
    """管理员获取所有通知"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        
        query = Notification.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
            
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': [{
                    'id': n.id,
                    'title': n.title,
                    'content': n.content,
                    'user_id': n.user_id,
                    'username': n.user.username if n.user else None,
                    'is_read': n.is_read,
                    'created_at': n.created_at.isoformat(),
                    'read_at': n.read_at.isoformat() if n.read_at else None
                } for n in notifications.items],
                'pagination': {
                    'page': notifications.page,
                    'pages': notifications.pages,
                    'per_page': notifications.per_page,
                    'total': notifications.total
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/admin/notifications', methods=['POST'])
@api_login_required
@permission_required('notification_create')
def admin_create_notification():
    """管理员创建通知"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
            
        title = data.get('title')
        content = data.get('content')
        user_ids = data.get('user_ids', [])
        send_to_all = data.get('send_to_all', False)
        
        if not title:
            return jsonify({'success': False, 'message': '标题不能为空'}), 400
            
        # 如果是发送给所有用户
        if send_to_all:
            users = User.query.filter_by(is_active=True).all()
            user_ids = [user.id for user in users]
        
        if not user_ids:
            return jsonify({'success': False, 'message': '接收用户不能为空'}), 400
            
        # 验证用户ID是否存在
        users = User.query.filter(User.id.in_(user_ids)).all()
        if len(users) != len(user_ids):
            return jsonify({'success': False, 'message': '部分用户ID不存在'}), 400
            
        # 批量创建通知
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                title=title,
                content=content,
                user_id=user_id
            )
            notifications.append(notification)
            db.session.add(notification)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功创建 {len(notifications)} 条通知',
            'data': {
                'id': notifications[0].id if notifications else None,
                'count': len(notifications)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/admin/notifications/broadcast', methods=['POST'])
@api_login_required
@permission_required('notification_create')
def broadcast_notification():
    """广播通知给所有用户"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
            
        title = data.get('title')
        content = data.get('content')
        
        if not title:
            return jsonify({'success': False, 'message': '标题不能为空'}), 400
            
        # 获取所有用户
        users = User.query.filter_by(is_active=True).all()
        
        if not users:
            return jsonify({'success': False, 'message': '没有找到活跃用户'}), 400
            
        # 批量创建通知
        notifications = []
        for user in users:
            notification = Notification(
                title=title,
                content=content,
                user_id=user.id
            )
            notifications.append(notification)
            db.session.add(notification)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功向 {len(notifications)} 个用户发送广播通知',
            'data': {
                'count': len(notifications)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@notification_bp.route('/notifications/unread-count', methods=['GET'])
@api_login_required
@permission_required('notification_read')
def get_unread_count():
    """获取未读通知数量"""
    try:
        count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'unread_count': count
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500