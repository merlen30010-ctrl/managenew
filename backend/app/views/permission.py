from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.role import Role
from app.models.permission import Permission, RolePermission
from app.views.decorators import permission_required

permission_bp = Blueprint('permission', __name__)

@permission_bp.route('/')
@login_required
@permission_required('permission_read')
def list_permissions():
    """列出所有权限"""
    permissions = Permission.query.all()
    return render_template('permissions/list.html', permissions=permissions)

@permission_bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('permission_create')
def create_permission():
    """创建权限"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        module = request.form.get('module')
        action = request.form.get('action')
        
        # 检查权限是否已存在
        if Permission.query.filter_by(name=name).first():
            flash('权限名称已存在')
            return redirect(url_for('permission.create_permission'))
        
        # 创建新权限
        permission = Permission(
            name=name,
            description=description,
            module=module,
            action=action
        )
        db.session.add(permission)
        db.session.commit()
        
        flash('权限创建成功')
        return redirect(url_for('permission.list_permissions'))
        
    return render_template('permissions/create.html')

@permission_bp.route('/<int:permission_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('permission_update')
def edit_permission(permission_id):
    """编辑权限"""
    permission = Permission.query.get_or_404(permission_id)
    
    if request.method == 'POST':
        permission.name = request.form.get('name')
        permission.description = request.form.get('description')
        permission.module = request.form.get('module')
        permission.action = request.form.get('action')
        
        db.session.commit()
        flash('权限信息更新成功')
        return redirect(url_for('permission.list_permissions'))
        
    return render_template('permissions/edit.html', permission=permission)

@permission_bp.route('/<int:permission_id>/delete', methods=['POST'])
@login_required
@permission_required('permission_delete')
def delete_permission(permission_id):
    """删除权限"""
    permission = Permission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    flash('权限删除成功')
    return redirect(url_for('permission.list_permissions'))

@permission_bp.route('/roles/<int:role_id>/permissions')
@login_required
@permission_required('role_read')
def role_permissions(role_id):
    """查看角色权限"""
    role = Role.query.get_or_404(role_id)
    permissions = Permission.query.all()
    return render_template('permissions/role_permissions.html', role=role, permissions=permissions)

@permission_bp.route('/roles/<int:role_id>/permissions/update', methods=['POST'])
@login_required
@permission_required('role_update')
def update_role_permissions(role_id):
    """更新角色权限"""
    role = Role.query.get_or_404(role_id)
    
    # 获取所有权限ID
    permission_ids = request.form.getlist('permissions')
    
    # 删除现有权限关联
    RolePermission.query.filter_by(role_id=role.id).delete()
    
    # 添加新的权限关联
    for permission_id in permission_ids:
        rp = RolePermission(role_id=role.id, permission_id=int(permission_id))
        db.session.add(rp)
    
    db.session.commit()
    flash('角色权限更新成功')
    return redirect(url_for('permission.role_permissions', role_id=role.id))