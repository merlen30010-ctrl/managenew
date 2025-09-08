from flask import Blueprint, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.role import Role
from app.models.notification import Notification, ExamResult
from app.utils.validators import validate_password
from app.views.decorators import permission_required
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/notifications')
@login_required
def notifications():
    """查看个人通知"""
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications/list.html', notifications=user_notifications)

@main_bp.route('/exam-results')
@login_required
def exam_results():
    """查看在线考试成绩"""
    user_exam_results = ExamResult.query.filter_by(user_id=current_user.id).order_by(ExamResult.exam_date.desc()).all()
    return render_template('exam_results/list.html', exam_results=user_exam_results)

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证当前密码
        if not current_user.check_password(current_password):
            flash('当前密码错误')
            return redirect(url_for('main.change_password'))
        
        # 验证新密码
        if not validate_password(new_password):
            flash('新密码不符合要求，至少6位且包含字母和数字')
            return redirect(url_for('main.change_password'))
        
        # 确认密码一致性
        if new_password != confirm_password:
            flash('新密码和确认密码不一致')
            return redirect(url_for('main.change_password'))
        
        # 更新密码
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('密码修改成功')
        return redirect(url_for('main.profile'))
    
    return render_template('change_password.html')

# 用户管理功能
@main_bp.route('/users')
@login_required
@permission_required('user_read')
def users():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@main_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@permission_required('user_create')
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('main.create_user'))
            
        if User.query.filter_by(email=email).first():
            flash('邮箱已存在')
            return redirect(url_for('main.create_user'))
        
        # 创建新用户
        user = User(username=username, email=email, name=name, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('用户创建成功')
        return redirect(url_for('main.users'))
        
    return render_template('users/create.html')

@main_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('user_update')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        # name和phone字段已移至Employee表，此处不再处理
        
        # 如果提供了新密码，则更新密码
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        db.session.commit()
        flash('用户信息更新成功')
        return redirect(url_for('main.users'))
        
    return render_template('users/edit.html', user=user)

@main_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@permission_required('user_delete')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('用户删除成功')
    return redirect(url_for('main.users'))

# 角色管理功能
@main_bp.route('/roles')
@login_required
def roles():
    roles = Role.query.all()
    return render_template('roles/list.html', roles=roles)

@main_bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
def create_role():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # 检查角色是否已存在
        if Role.query.filter_by(name=name).first():
            flash('角色名称已存在')
            return redirect(url_for('main.create_role'))
        
        # 创建新角色
        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        
        flash('角色创建成功')
        return redirect(url_for('main.roles'))
        
    return render_template('roles/create.html')

@main_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        role.name = request.form.get('name')
        role.description = request.form.get('description')
        
        db.session.commit()
        flash('角色信息更新成功')
        return redirect(url_for('main.roles'))
        
    return render_template('roles/edit.html', role=role)

@main_bp.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash('角色删除成功')
    return redirect(url_for('main.roles'))