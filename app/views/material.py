from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.material import Material

material_bp = Blueprint('material', __name__)

@material_bp.route('/')
@login_required
def list_materials():
    materials = Material.query.all()
    return render_template('materials/list.html', materials=materials)

@material_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_material():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        full_name = request.form.get('full_name')
        purpose = request.form.get('purpose')
        
        # 检查物料代码是否已存在
        if Material.query.filter_by(code=code).first():
            flash('物料代码已存在')
            return redirect(url_for('material.create_material'))
        
        # 创建新物料
        material = Material(name=name, code=code, full_name=full_name, purpose=purpose)
        db.session.add(material)
        db.session.commit()
        
        flash('物料创建成功')
        return redirect(url_for('material.list_materials'))
        
    return render_template('materials/create.html')

@material_bp.route('/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)
    
    if request.method == 'POST':
        material.name = request.form.get('name')
        material.code = request.form.get('code')
        material.full_name = request.form.get('full_name')
        material.purpose = request.form.get('purpose')
        
        db.session.commit()
        flash('物料信息更新成功')
        return redirect(url_for('material.list_materials'))
        
    return render_template('materials/edit.html', material=material)

@material_bp.route('/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    flash('物料删除成功')
    return redirect(url_for('material.list_materials'))