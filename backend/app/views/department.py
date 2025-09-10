from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.department import Department
from app.models.user import User
from app.views.decorators import permission_required

department_bp = Blueprint('department', __name__)

@department_bp.route('/')
@login_required
@permission_required('department_read')
def list_departments():
    # 获取所有顶级部门（分厂）
    factories = Department.query.filter_by(level=1).all()
    return render_template('departments/list.html', factories=factories)

@department_bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('department_create')
def create_department():
    if request.method == 'POST':
        name = request.form.get('name')
        short_name = request.form.get('short_name')
        full_name = request.form.get('full_name')
        level = int(request.form.get('level'))
        parent_id = request.form.get('parent_id')
        phone = request.form.get('phone')
        
        # 创建新部门
        department = Department(name=name, short_name=short_name, full_name=full_name, 
                              level=level, phone=phone)
        
        if parent_id and parent_id != '0':
            department.parent_id = int(parent_id)
        
        db.session.add(department)
        db.session.commit()
        
        flash('部门创建成功')
        return redirect(url_for('department.list_departments'))
    
    # 获取所有分厂用于选择父级部门
    factories = Department.query.filter_by(level=1).all()
    return render_template('departments/create.html', factories=factories)

@department_bp.route('/<int:department_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('department_update')
def edit_department(department_id):
    department = Department.query.get_or_404(department_id)
    
    if request.method == 'POST':
        department.name = request.form.get('name')
        department.short_name = request.form.get('short_name')
        department.full_name = request.form.get('full_name')
        department.level = int(request.form.get('level'))
        parent_id = request.form.get('parent_id')
        department.phone = request.form.get('phone')
        
        if parent_id and parent_id != '0':
            department.parent_id = int(parent_id)
        else:
            department.parent_id = None
        
        db.session.commit()
        flash('部门信息更新成功')
        return redirect(url_for('department.list_departments'))
    
    # 获取所有分厂用于选择父级部门
    factories = Department.query.filter_by(level=1).all()
    return render_template('departments/edit.html', department=department, factories=factories)

@department_bp.route('/<int:department_id>/delete', methods=['POST'])
@login_required
@permission_required('department_delete')
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    flash('部门删除成功')
    return redirect(url_for('department.list_departments'))

@department_bp.route('/<int:department_id>/managers', methods=['GET', 'POST'])
@login_required
@permission_required('department_update')
def manage_managers(department_id):
    department = Department.query.get_or_404(department_id)
    
    if request.method == 'POST':
        # 获取选中的管理员用户ID
        manager_ids = request.form.getlist('managers')
        
        # 清除现有的管理员关联
        department.managers.clear()
        
        # 添加新的管理员
        for user_id in manager_ids:
            user = User.query.get(int(user_id))
            if user:
                department.managers.append(user)
        
        db.session.commit()
        flash('部门管理员设置成功')
        return redirect(url_for('department.list_departments'))
    
    # 获取所有用户用于选择管理员
    users = User.query.all()
    return render_template('departments/managers.html', department=department, users=users)