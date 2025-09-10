from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('用户名或密码错误')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if not username or not password:
            flash('用户名和密码都是必填的')
            return redirect(url_for('auth.register'))
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('auth.register'))
        
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
        
        flash('注册成功')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')