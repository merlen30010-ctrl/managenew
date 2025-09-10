from flask import Blueprint, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.role import Role
from app.models.employee import Employee
from app.models.notification import Notification, ExamResult
from app.utils.validators import validate_password
from app.views.decorators import permission_required
from app.utils.anti_spam import anti_spam_required, record_submission_attempt, anti_spam
import os
from datetime import datetime

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
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('notifications/list.html', notifications=user_notifications, unread_count=unread_count)

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
    superuser_count = User.query.filter_by(is_superuser=True).count()
    return render_template('users/list.html', users=users, superuser_count=superuser_count)

@main_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@permission_required('user_create')
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('main.create_user'))
        
        # 创建新用户
        user = User(username=username, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # 自动为新用户分配员工角色
        from app.models.role import Role
        employee_role = Role.query.filter_by(name='员工').first()
        if employee_role:
            user.roles.append(employee_role)
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
        # 更新姓名
        name = request.form.get('name')
        if name:
            user.name = name
        
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
    """删除用户"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 防止删除当前登录用户
        if user.id == current_user.id:
            flash('不能删除当前登录用户', 'error')
            return redirect(url_for('main.users'))
        
        # 防止删除admin用户
        if user.username == 'admin':
            flash('不能删除系统管理员admin用户', 'error')
            return redirect(url_for('main.users'))
        
        # 防止删除最后一个超级管理员
        if user.is_superuser:
            superuser_count = User.query.filter_by(is_superuser=True).count()
            if superuser_count <= 1:
                flash('不能删除最后一个超级管理员', 'error')
                return redirect(url_for('main.users'))
        
        db.session.delete(user)
        db.session.commit()
        flash('用户删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除用户失败: {str(e)}', 'error')
    
    return redirect(url_for('main.users'))

# 角色管理功能
@main_bp.route('/roles')
@login_required
@permission_required('role_read')
def roles():
    roles = Role.query.all()
    return render_template('roles/list.html', roles=roles)

@main_bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
@permission_required('role_create')
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

# 应聘相关路由（公开访问）
@main_bp.route('/application')
def application():
    """应聘信息填写页面（公开访问）"""
    return render_template('application.html')

@main_bp.route('/application/submit', methods=['POST'])
@anti_spam_required
def submit_application():
    """处理应聘信息提交"""
    ip = anti_spam.get_client_ip()
    
    try:
        # 获取表单数据
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        birth_date_str = request.form.get('birth_date', '').strip()
        id_card = request.form.get('id_card', '').strip()
        phone = request.form.get('phone', '').strip()
        education = request.form.get('education', '').strip()
        native_place = request.form.get('native_place', '').strip()
        nationality = request.form.get('nationality', '').strip()
        marital_status = request.form.get('marital_status', '').strip()
        job_title = request.form.get('job_title', '').strip()
        address = request.form.get('address', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        emergency_phone = request.form.get('emergency_phone', '').strip()
        
        # 验证必填字段
        if not all([name, gender, birth_date_str, id_card, phone, education]):
            flash('请填写所有必填项目', 'error')
            return redirect(url_for('main.application'))
        
        # 检查身份证号是否已存在
        existing_employee = Employee.query.filter_by(id_card=id_card).first()
        if existing_employee:
            flash('该身份证号已存在，请检查后重新填写', 'error')
            return redirect(url_for('main.application'))
        
        # 转换日期格式
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('出生日期格式不正确', 'error')
            return redirect(url_for('main.application'))
        
        # 创建员工记录
        try:
            employee = Employee(
                user_id=None,  # 应聘阶段不关联用户
                employee_id=None,  # 应聘阶段不分配工号
                department_id=None,  # 应聘阶段不分配部门
                job_title=job_title if job_title else None,
                hire_date=None,  # 应聘阶段不设置入职日期
                work_years=None,
                name=name,
                gender=gender,
                birth_date=birth_date,
                id_card=id_card,
                native_place=native_place if native_place else None,
                nationality=nationality if nationality else None,
                education=education,
                marital_status=marital_status if marital_status else None,
                phone=phone,
                address=address if address else None,
                avatar_path=None,
                employment_status='储备',  # 默认为储备状态
                emergency_contact=emergency_contact if emergency_contact else None,
                emergency_phone=emergency_phone if emergency_phone else None
            )
            
            db.session.add(employee)
            db.session.commit()
            current_app.logger.info(f'员工记录创建成功: {name}, ID: {employee.id}')
        except Exception as create_error:
            db.session.rollback()
            current_app.logger.error(f'创建员工记录失败: {str(create_error)}')
            raise create_error
        
        # 记录成功提交
        record_submission_attempt(ip, request.form.to_dict())
        
        flash('应聘信息提交成功！我们会尽快与您联系。', 'success')
        return redirect(url_for('main.application'))
        
    except Exception as e:
        db.session.rollback()
        # 即使失败也记录提交尝试（防止恶意重试）
        record_submission_attempt(ip, request.form.to_dict())
        current_app.logger.error(f'应聘信息提交失败: {str(e)}')
        flash('提交失败，请稍后重试', 'error')
        return redirect(url_for('main.application'))
        
    return render_template('roles/create.html')

@main_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('role_update')
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
@permission_required('role_delete')
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash('角色删除成功')
    return redirect(url_for('main.roles'))

@main_bp.route('/robots.txt')
def robots_txt():
    """提供robots.txt文件，禁止搜索引擎抓取"""
    return send_from_directory(current_app.root_path + '/../', 'robots.txt', mimetype='text/plain')