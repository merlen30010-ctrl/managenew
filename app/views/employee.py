from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.employee import Employee
from app.models.user import User
from app.models.department import Department
from app.api.decorators import admin_required

employee_view_bp = Blueprint('employee', __name__)

@employee_view_bp.route('/')
@login_required
@admin_required
def list_employees():
    """员工列表页面"""
    try:
        # 获取所有部门用于筛选
        departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
        
        return render_template('employee/list.html', 
                             departments=departments)
    except Exception as e:
        flash(f'加载页面失败: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@employee_view_bp.route('/profile')
@login_required
def my_profile():
    """个人档案页面"""
    try:
        # 获取当前用户的员工信息
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        
        if not employee:
            flash('您还没有员工档案信息', 'warning')
            return redirect(url_for('main.index'))
        
        return render_template('employee/profile.html', employee=employee)
    except Exception as e:
        flash(f'加载个人档案失败: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@employee_view_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """员工统计页面"""
    try:
        return render_template('employee/statistics.html')
    except Exception as e:
        flash(f'加载统计页面失败: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@employee_view_bp.route('/documents')
@login_required
@admin_required
def documents():
    """员工证件管理页面"""
    try:
        return render_template('employee/documents.html')
    except Exception as e:
        flash(f'加载证件管理页面失败: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@employee_view_bp.route('/rewards-punishments')
@login_required
@admin_required
def rewards_punishments():
    """员工奖惩管理页面"""
    try:
        return render_template('employee/rewards_punishments.html')
    except Exception as e:
        flash(f'加载奖惩管理页面失败: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@employee_view_bp.route('/promote/<int:employee_id>')
@login_required
@admin_required
def promote_employee(employee_id):
    """员工转正页面"""
    try:
        # 获取员工信息
        employee = Employee.query.get_or_404(employee_id)
        
        # 检查员工状态
        if employee.employment_status != '储备':
            flash('只有储备状态的员工才能转正', 'warning')
            return redirect(url_for('employee.list_employees'))
        
        # 获取所有部门
        departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
        
        return render_template('employee/promote.html', 
                             employee=employee, 
                             departments=departments)
    except Exception as e:
        flash(f'加载转正页面失败: {str(e)}', 'error')
        return redirect(url_for('employee.list_employees'))