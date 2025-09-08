from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification
from app.models.user import User
from app.views.decorators import permission_required
from datetime import datetime

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications')
@login_required
def user_list():
    """用户查看自己的通知列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('notifications/user_list.html', notifications=notifications, unread_count=unread_count)

@notification_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    """标记通知为已读"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        flash('通知不存在', 'error')
        return redirect(url_for('notification.user_list'))
        
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now()
        db.session.commit()
        flash('通知已标记为已读', 'success')
    
    return redirect(url_for('notification.user_list'))

@notification_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """标记所有通知为已读"""
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
    flash(f'成功标记 {count} 条通知为已读', 'success')
    
    return redirect(url_for('notification.user_list'))

@notification_bp.route('/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_user_notification(notification_id):
    """用户删除自己的通知"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        flash('通知不存在', 'error')
        return redirect(url_for('notification.user_list'))
        
    db.session.delete(notification)
    db.session.commit()
    flash('通知删除成功', 'success')
    
    return redirect(url_for('notification.user_list'))

@notification_bp.route('/admin/notifications')
@login_required
@permission_required('notification_manage')
def admin_list_notifications():
    """管理员查看所有通知"""
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id', type=int)
    per_page = 20
    
    query = Notification.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
        
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = User.query.filter_by(is_active=True).all()
    
    return render_template('notifications/admin_list.html', 
                         notifications=notifications, 
                         users=users,
                         selected_user_id=user_id)

@notification_bp.route('/admin/notifications/create', methods=['GET', 'POST'])
@login_required
@permission_required('notification_create')
def admin_create_notification():
    """管理员创建通知"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        user_ids = request.form.getlist('user_ids')
        send_to_all = request.form.get('send_to_all') == 'on'
        
        if not title:
            flash('标题不能为空', 'error')
            return redirect(url_for('notification.admin_create_notification'))
            
        if send_to_all:
            # 发送给所有活跃用户
            users = User.query.filter_by(is_active=True).all()
            user_ids = [user.id for user in users]
        elif not user_ids:
            flash('请选择接收用户', 'error')
            return redirect(url_for('notification.admin_create_notification'))
        else:
            user_ids = [int(uid) for uid in user_ids]
            
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
        
        flash(f'成功创建 {len(notifications)} 条通知', 'success')
        return redirect(url_for('notification.admin_list_notifications'))
        
    users = User.query.filter_by(is_active=True).all()
    return render_template('notifications/admin_create.html', users=users)

@notification_bp.route('/admin/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
@permission_required('notification_delete')
def admin_delete_notification(notification_id):
    """管理员删除通知"""
    notification = Notification.query.get_or_404(notification_id)
    
    db.session.delete(notification)
    db.session.commit()
    
    flash('通知删除成功', 'success')
    return redirect(url_for('notification.admin_list_notifications'))

@notification_bp.route('/notifications/unread-count')
@login_required
def get_unread_count():
    """获取未读通知数量（AJAX接口）"""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'unread_count': count})