from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.assay_data import AssayData
from app.models.department import Department
from app.models.attachment import Attachment
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

assay_data_bp = Blueprint('assay_data', __name__, url_prefix='/assay-data')

@assay_data_bp.route('/')
@login_required
def list_assay_data():
    """化验数据列表"""
    # 根据用户权限获取数据
    if current_user.has_permission_name('assay_data_read_all'):
        # 管理员可以看到所有数据
        assay_data_list = AssayData.query.all()
    else:
        # 其他用户只能看到自己分厂的数据
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        assay_data_list = AssayData.query.filter(AssayData.factory_id.in_(factory_ids)).all()
    
    return render_template('assay_data/list.html', assay_data_list=assay_data_list)

@assay_data_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_assay_data():
    """创建化验数据"""
    if request.method == 'POST':
        sample_name = request.form.get('sample_name')
        factory_id = request.form.get('factory_id')
        
        # 检查权限
        if not current_user.has_permission_name('assay_data_create_all'):
            user_factories = [dept.id for dept in current_user.managed_departments if dept.level == 1]
            if factory_id and int(factory_id) not in user_factories:
                flash('您没有权限在此分厂创建化验数据')
                return redirect(url_for('assay_data.create_assay_data'))
        
        # 创建化验数据记录
        assay_data = AssayData(
            sample_name=sample_name,
            factory_id=int(factory_id) if factory_id else 0,
            created_by=current_user.id
        )
        
        # 设置各项指标值
        assay_data.water_content = float(request.form.get('water_content', 0) or 0)
        assay_data.zinc_content = float(request.form.get('zinc_content', 0) or 0)
        assay_data.lead_content = float(request.form.get('lead_content', 0) or 0)
        assay_data.chlorine_content = float(request.form.get('chlorine_content', 0) or 0)
        assay_data.fluorine_content = float(request.form.get('fluorine_content', 0) or 0)
        assay_data.iron_content = float(request.form.get('iron_content', 0) or 0)
        assay_data.silicon_content = float(request.form.get('silicon_content', 0) or 0)
        assay_data.sulfur_content = float(request.form.get('sulfur_content', 0) or 0)
        assay_data.high_heat = float(request.form.get('high_heat', 0) or 0)
        assay_data.low_heat = float(request.form.get('low_heat', 0) or 0)
        assay_data.silver_content = float(request.form.get('silver_content', 0) or 0)
        assay_data.recovery_rate = float(request.form.get('recovery_rate', 0) or 0)
        assay_data.remarks = request.form.get('remarks', '')
        
        db.session.add(assay_data)
        db.session.flush()  # 先刷新获取ID，但不提交事务
        
        # 处理附件上传
        try:
            if 'attachment' in request.files:
                file = request.files['attachment']
                if file and file.filename:
                    # 检查文件类型（只允许图片）
                    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
                    file_ext = os.path.splitext(file.filename)[1].lower()
                    if file_ext not in allowed_extensions:
                        flash('只允许上传图片文件（jpg, jpeg, png, gif）')
                        db.session.rollback()
                        return redirect(url_for('assay_data.create_assay_data'))
                    
                    # 创建上传目录
                    from flask import current_app
                    upload_folder = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
                    upload_dir = os.path.join(str(upload_folder), 'assay', sample_name or '', datetime.now().strftime('%Y%m%d'))
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # 生成存储文件名
                    stored_name = f"{sample_name}{file_ext}"
                    
                    # 检查是否已存在同名文件，如果存在则添加后缀
                    counter = 1
                    final_name = stored_name
                    while os.path.exists(os.path.join(upload_dir, final_name)):
                        final_name = f"{sample_name}-{counter}{file_ext}"
                        counter += 1
                    
                    file_path = os.path.join(upload_dir, final_name)
                    
                    # 保存文件
                    file.save(file_path)
                    
                    # 检查文件是否保存成功
                    if os.path.exists(file_path):
                        # 创建附件记录
                        attachment = Attachment(
                            related_type='assay_data',
                            related_id=assay_data.id,
                            file_path=file_path,
                            original_name=file.filename,
                            stored_name=final_name,
                            file_type=file_ext,
                            file_size=os.path.getsize(file_path),
                            created_by=current_user.id
                        )
                        
                        db.session.add(attachment)
                    else:
                        logger.error(f"文件保存失败: {file_path}")
                        flash('文件保存失败')
                        db.session.rollback()
                        return redirect(url_for('assay_data.create_assay_data'))
        except Exception as e:
            logger.error(f"上传附件时发生错误: {str(e)}")
            flash(f'上传附件时发生错误: {str(e)}')
            db.session.rollback()
            return redirect(url_for('assay_data.create_assay_data'))
        
        db.session.commit()
        flash('化验数据创建成功')
        return redirect(url_for('assay_data.list_assay_data'))
    
    # 获取用户有权限的分厂
    if current_user.has_permission_name('assay_data_read_all'):
        factories = Department.query.filter_by(level=1).all()
    else:
        factories = current_user.managed_departments
    
    return render_template('assay_data/create.html', factories=factories)

@assay_data_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_assay_data(id):
    """编辑化验数据"""
    assay_data = AssayData.query.get_or_404(id)
    
    # 检查权限
    if not current_user.has_permission_name('assay_data_update_all'):
        user_factories = [dept.id for dept in current_user.managed_departments if dept.level == 1]
        if assay_data.factory_id not in user_factories:
            flash('您没有权限编辑此化验数据')
            return redirect(url_for('assay_data.list_assay_data'))
    
    if request.method == 'POST':
        assay_data.sample_name = request.form.get('sample_name')
        
        # 更新各项指标值
        assay_data.water_content = float(request.form.get('water_content', 0) or 0)
        assay_data.zinc_content = float(request.form.get('zinc_content', 0) or 0)
        assay_data.lead_content = float(request.form.get('lead_content', 0) or 0)
        assay_data.chlorine_content = float(request.form.get('chlorine_content', 0) or 0)
        assay_data.fluorine_content = float(request.form.get('fluorine_content', 0) or 0)
        assay_data.iron_content = float(request.form.get('iron_content', 0) or 0)
        assay_data.silicon_content = float(request.form.get('silicon_content', 0) or 0)
        assay_data.sulfur_content = float(request.form.get('sulfur_content', 0) or 0)
        assay_data.high_heat = float(request.form.get('high_heat', 0) or 0)
        assay_data.low_heat = float(request.form.get('low_heat', 0) or 0)
        assay_data.silver_content = float(request.form.get('silver_content', 0) or 0)
        assay_data.recovery_rate = float(request.form.get('recovery_rate', 0) or 0)
        assay_data.remarks = request.form.get('remarks', '')
        
        db.session.commit()
        flash('化验数据更新成功')
        return redirect(url_for('assay_data.list_assay_data'))
    
    # 获取用户有权限的分厂
    if current_user.has_permission_name('assay_data_read_all'):
        factories = Department.query.filter_by(level=1).all()
    else:
        factories = current_user.managed_departments
    
    return render_template('assay_data/edit.html', assay_data=assay_data, factories=factories)

@assay_data_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_assay_data(id):
    """删除化验数据"""
    assay_data = AssayData.query.get_or_404(id)
    
    # 检查权限
    if not current_user.has_permission_name('assay_data_delete_all'):
        user_factories = [dept.id for dept in current_user.managed_departments if dept.level == 1]
        if assay_data.factory_id not in user_factories:
            flash('您没有权限删除此化验数据')
            return redirect(url_for('assay_data.list_assay_data'))
    
    db.session.delete(assay_data)
    db.session.commit()
    flash('化验数据删除成功')
    return redirect(url_for('assay_data.list_assay_data'))