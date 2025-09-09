from flask import Blueprint, jsonify, request, send_file
from app import db
from app.models.assay_data import AssayData
from app.models.attachment import Attachment
from datetime import datetime
import os
import logging
from flask_login import current_user
from app.api.decorators import api_login_required, permission_required

# 创建化验数据API蓝图
api_assay_data_bp = Blueprint('api_assay_data', __name__, url_prefix='/api')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 化验数据相关API
@api_assay_data_bp.route('/assay-data', methods=['GET'])
@api_login_required
@permission_required('assay_data_read')
def get_assay_data_list():
    """获取化验数据列表"""
    # 根据用户权限获取数据
    if current_user.has_permission_name('assay_data_read_all'):
        # 管理员可以看到所有数据
        assay_data_list = AssayData.query.all()
    else:
        # 其他用户只能看到自己分厂的数据
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        assay_data_list = AssayData.query.filter(AssayData.factory_id.in_(factory_ids)).all()
    
    return jsonify([{
        'id': data.id,
        'sample_name': data.sample_name,
        'factory_id': data.factory_id,
        'water_content': data.water_content,
        'zinc_content': data.zinc_content,
        'lead_content': data.lead_content,
        'chlorine_content': data.chlorine_content,
        'fluorine_content': data.fluorine_content,
        'iron_content': data.iron_content,
        'silicon_content': data.silicon_content,
        'sulfur_content': data.sulfur_content,
        'high_heat': data.high_heat,
        'low_heat': data.low_heat,
        'silver_content': data.silver_content,
        'recovery_rate': data.recovery_rate,
        'remarks': data.remarks,
        'created_by': data.created_by,
        'created_at': data.created_at.isoformat() if data.created_at else None,
        'updated_at': data.updated_at.isoformat() if data.updated_at else None
    } for data in assay_data_list])

@api_assay_data_bp.route('/assay-data/<int:data_id>', methods=['GET'])
@api_login_required
@permission_required('assay_data_read')
def get_assay_data(data_id):
    """获取单个化验数据"""
    assay_data = AssayData.query.get_or_404(data_id)
    
    # 检查权限
    if not current_user.has_permission_name('assay_data_update_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if assay_data.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限查看此化验数据'}), 403
    
    return jsonify({
        'id': assay_data.id,
        'sample_name': assay_data.sample_name,
        'factory_id': assay_data.factory_id,
        'water_content': assay_data.water_content,
        'zinc_content': assay_data.zinc_content,
        'lead_content': assay_data.lead_content,
        'chlorine_content': assay_data.chlorine_content,
        'fluorine_content': assay_data.fluorine_content,
        'iron_content': assay_data.iron_content,
        'silicon_content': assay_data.silicon_content,
        'sulfur_content': assay_data.sulfur_content,
        'high_heat': assay_data.high_heat,
        'low_heat': assay_data.low_heat,
        'silver_content': assay_data.silver_content,
        'recovery_rate': assay_data.recovery_rate,
        'remarks': assay_data.remarks,
        'created_by': assay_data.created_by,
        'created_at': assay_data.created_at.isoformat() if assay_data.created_at else None,
        'updated_at': assay_data.updated_at.isoformat() if assay_data.updated_at else None
    })

@api_assay_data_bp.route('/assay-data', methods=['POST'])
@api_login_required
@permission_required('assay_data_create')
def create_assay_data():
    """创建化验数据"""
    data = request.get_json()
    
    if not data or not data.get('sample_name') or not data.get('factory_id'):
        return jsonify({'error': '样品名称和分厂是必填字段'}), 400
    
    # 检查权限
    if not current_user.has_permission_name('assay_data_read_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if int(data['factory_id']) not in factory_ids:
            return jsonify({'error': '您没有权限在此分厂创建化验数据'}), 403
    
    # 创建化验数据记录
    assay_data = AssayData(
        sample_name=data['sample_name'],
        factory_id=data['factory_id'],
        created_by=current_user.id
    )
    
    # 设置各项指标值
    assay_data.water_content = float(data.get('water_content', 0) or 0)
    assay_data.zinc_content = float(data.get('zinc_content', 0) or 0)
    assay_data.lead_content = float(data.get('lead_content', 0) or 0)
    assay_data.chlorine_content = float(data.get('chlorine_content', 0) or 0)
    assay_data.fluorine_content = float(data.get('fluorine_content', 0) or 0)
    assay_data.iron_content = float(data.get('iron_content', 0) or 0)
    assay_data.silicon_content = float(data.get('silicon_content', 0) or 0)
    assay_data.sulfur_content = float(data.get('sulfur_content', 0) or 0)
    assay_data.high_heat = float(data.get('high_heat', 0) or 0)
    assay_data.low_heat = float(data.get('low_heat', 0) or 0)
    assay_data.silver_content = float(data.get('silver_content', 0) or 0)
    assay_data.recovery_rate = float(data.get('recovery_rate', 0) or 0)
    assay_data.remarks = data.get('remarks', '')
    
    db.session.add(assay_data)
    db.session.commit()
    
    return jsonify({
        'id': assay_data.id,
        'sample_name': assay_data.sample_name,
        'factory_id': assay_data.factory_id,
        'water_content': assay_data.water_content,
        'zinc_content': assay_data.zinc_content,
        'lead_content': assay_data.lead_content,
        'chlorine_content': assay_data.chlorine_content,
        'fluorine_content': assay_data.fluorine_content,
        'iron_content': assay_data.iron_content,
        'silicon_content': assay_data.silicon_content,
        'sulfur_content': assay_data.sulfur_content,
        'high_heat': assay_data.high_heat,
        'low_heat': assay_data.low_heat,
        'silver_content': assay_data.silver_content,
        'recovery_rate': assay_data.recovery_rate,
        'remarks': assay_data.remarks,
        'created_by': assay_data.created_by,
        'created_at': assay_data.created_at.isoformat() if assay_data.created_at else None,
        'updated_at': assay_data.updated_at.isoformat() if assay_data.updated_at else None
    }), 201

@api_assay_data_bp.route('/assay-data/<int:data_id>', methods=['PUT'])
@api_login_required
@permission_required('assay_data_update')
def update_assay_data(data_id):
    """更新化验数据"""
    assay_data = AssayData.query.get_or_404(data_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 检查权限
    if not current_user.has_permission_name('assay_data_delete_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if assay_data.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限更新此化验数据'}), 403
    
    # 更新化验数据信息
    if 'sample_name' in data:
        assay_data.sample_name = data['sample_name']
    
    if 'factory_id' in data:
        # 检查权限
        if not current_user.has_permission_name('assay_data_create_all'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if int(data['factory_id']) not in factory_ids:
                return jsonify({'error': '您没有权限将数据转移到此分厂'}), 403
        assay_data.factory_id = data['factory_id']
    
    # 更新各项指标值
    if 'water_content' in data:
        assay_data.water_content = float(data['water_content'] or 0)
    if 'zinc_content' in data:
        assay_data.zinc_content = float(data['zinc_content'] or 0)
    if 'lead_content' in data:
        assay_data.lead_content = float(data['lead_content'] or 0)
    if 'chlorine_content' in data:
        assay_data.chlorine_content = float(data['chlorine_content'] or 0)
    if 'fluorine_content' in data:
        assay_data.fluorine_content = float(data['fluorine_content'] or 0)
    if 'iron_content' in data:
        assay_data.iron_content = float(data['iron_content'] or 0)
    if 'silicon_content' in data:
        assay_data.silicon_content = float(data['silicon_content'] or 0)
    if 'sulfur_content' in data:
        assay_data.sulfur_content = float(data['sulfur_content'] or 0)
    if 'high_heat' in data:
        assay_data.high_heat = float(data['high_heat'] or 0)
    if 'low_heat' in data:
        assay_data.low_heat = float(data['low_heat'] or 0)
    if 'silver_content' in data:
        assay_data.silver_content = float(data['silver_content'] or 0)
    if 'recovery_rate' in data:
        assay_data.recovery_rate = float(data['recovery_rate'] or 0)
    if 'remarks' in data:
        assay_data.remarks = data['remarks']
    
    db.session.commit()
    
    return jsonify({
        'id': assay_data.id,
        'sample_name': assay_data.sample_name,
        'factory_id': assay_data.factory_id,
        'water_content': assay_data.water_content,
        'zinc_content': assay_data.zinc_content,
        'lead_content': assay_data.lead_content,
        'chlorine_content': assay_data.chlorine_content,
        'fluorine_content': assay_data.fluorine_content,
        'iron_content': assay_data.iron_content,
        'silicon_content': assay_data.silicon_content,
        'sulfur_content': assay_data.sulfur_content,
        'high_heat': assay_data.high_heat,
        'low_heat': assay_data.low_heat,
        'silver_content': assay_data.silver_content,
        'recovery_rate': assay_data.recovery_rate,
        'remarks': assay_data.remarks,
        'created_by': assay_data.created_by,
        'created_at': assay_data.created_at.isoformat() if assay_data.created_at else None,
        'updated_at': assay_data.updated_at.isoformat() if assay_data.updated_at else None
    })

@api_assay_data_bp.route('/assay-data/<int:data_id>', methods=['DELETE'])
@api_login_required
@permission_required('assay_data_delete')
def delete_assay_data(data_id):
    """删除化验数据"""
    assay_data = AssayData.query.get_or_404(data_id)
    
    # 检查权限
    if not current_user.has_permission_name('assay_data_delete_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if assay_data.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限删除此化验数据'}), 403
    
    db.session.delete(assay_data)
    db.session.commit()
    return jsonify({'message': '化验数据删除成功'})

# 通用附件相关API
@api_assay_data_bp.route('/attachments', methods=['POST'])
@api_login_required
@permission_required('attachment_create')
def upload_attachment():
    """
    上传附件
    """
    try:
        file = request.files.get('file')
        related_type = request.form.get('related_type')
        related_id = request.form.get('related_id')
        naming_rule = request.form.get('naming_rule', 'default')  # 命名规则参数
        
        if not file or not file.filename:
            return jsonify({'error': '请选择要上传的文件'}), 400
            
        if not related_type or not related_id:
            return jsonify({'error': '缺少关联对象信息'}), 400
            
        # 创建上传目录
        from app.views.attachment import create_upload_directory, generate_filename
        upload_dir = create_upload_directory(related_type)
        
        # 生成存储文件名
        stored_name = generate_filename(file.filename, related_type, related_id, naming_rule)
        file_path = os.path.join(upload_dir, stored_name)
        
        # 保存文件
        file.save(file_path)
        
        # 检查文件是否保存成功
        if not os.path.exists(file_path):
            logger.error(f"文件保存失败: {file_path}")
            return jsonify({'error': '文件保存失败'}), 500
            
        # 创建附件记录
        attachment = Attachment(
            related_type=related_type,
            related_id=int(related_id),
            file_path=file_path,
            original_name=file.filename,
            stored_name=stored_name,
            file_type=os.path.splitext(file.filename)[1].lower(),
            file_size=os.path.getsize(file_path),
            created_by=getattr(current_user, 'id', None)
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'id': attachment.id,
            'related_type': attachment.related_type,
            'related_id': attachment.related_id,
            'file_path': attachment.file_path,
            'original_name': attachment.original_name,
            'file_type': attachment.file_type,
            'file_size': attachment.file_size,
            'created_at': attachment.created_at.isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"上传附件时发生错误: {str(e)}")
        return jsonify({'error': f'上传附件时发生错误: {str(e)}'}), 500

@api_assay_data_bp.route('/attachments/<int:attachment_id>/download')
@api_login_required
@permission_required('attachment_read')
def download_attachment(attachment_id):
    """
    下载附件
    """
    try:
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证文件记录
        if not attachment.file_path:
            logger.error(f"附件记录中缺少文件路径: {attachment_id}")
            return jsonify({'error': '文件路径信息不完整'}), 400
            
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(attachment.file_path)
        logger.info(f"尝试下载文件: {file_path}")
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 验证路径安全性（防止路径遍历攻击）
            if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                logger.error(f"文件路径不安全: {file_path}")
                return jsonify({'error': '文件路径不安全'}), 400
                
            # 使用os.path.basename获取文件名，确保跨平台兼容性
            filename = os.path.basename(file_path)
            logger.info(f"文件存在，准备下载: {filename}")
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            logger.error(f"文件不存在: {file_path}")
            return jsonify({'error': f'文件不存在: {attachment.original_name}'}), 404
            
    except Exception as e:
        logger.error(f"下载文件时发生错误: {str(e)}")
        return jsonify({'error': f'下载文件时发生错误: {str(e)}'}), 500

@api_assay_data_bp.route('/attachments/<int:attachment_id>/preview')
@api_login_required
@permission_required('attachment_read')
def preview_attachment(attachment_id):
    """
    预览附件
    """
    try:
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证文件记录
        if not attachment.file_path:
            logger.error(f"附件记录中缺少文件路径: {attachment_id}")
            return jsonify({'error': '文件路径信息不完整'}), 400
            
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(attachment.file_path)
        logger.info(f"尝试预览文件: {file_path}")
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 验证路径安全性（防止路径遍历攻击）
            if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                logger.error(f"文件路径不安全: {file_path}")
                return jsonify({'error': '文件路径不安全'}), 400
                
            # 获取文件扩展名（使用os.path.splitext确保兼容性）
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 根据文件类型设置MIME类型
            mime_types = {
                '.pdf': 'application/pdf',
                '.txt': 'text/plain',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }
            
            # 如果是支持预览的文件类型，直接显示
            if file_ext in mime_types:
                logger.info(f"预览文件类型: {file_ext}")
                return send_file(file_path, as_attachment=False, mimetype=mime_types[file_ext])
            else:
                logger.warning(f"不支持预览的文件类型: {file_ext}")
                return jsonify({'error': '该文件类型不支持预览'}), 400
        else:
            logger.error(f"文件不存在: {file_path}")
            return jsonify({'error': f'文件不存在: {attachment.original_name}'}), 404
            
    except Exception as e:
        logger.error(f"预览文件时发生错误: {str(e)}")
        return jsonify({'error': f'预览文件时发生错误: {str(e)}'}), 500

@api_assay_data_bp.route('/attachments/<int:attachment_id>', methods=['DELETE'])
@api_login_required
@permission_required('attachment_delete')
def delete_attachment(attachment_id):
    """
    删除附件
    """
    try:
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证文件记录
        if not attachment.file_path:
            logger.error(f"附件记录中缺少文件路径: {attachment_id}")
            return jsonify({'error': '文件路径信息不完整'}), 400
            
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(attachment.file_path)
        logger.info(f"尝试删除文件: {file_path}")
        
        # 删除文件系统中的文件
        if os.path.exists(file_path):
            try:
                # 验证路径安全性
                if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                    logger.error(f"文件路径不安全: {file_path}")
                    return jsonify({'error': '文件路径不安全'}), 400
                    
                os.remove(file_path)
                logger.info(f"文件删除成功: {file_path}")
            except PermissionError:
                logger.error(f"没有权限删除文件: {file_path}")
                return jsonify({'error': f'没有权限删除文件: {attachment.original_name}'}), 403
            except Exception as e:
                logger.error(f"文件删除失败: {str(e)}")
                return jsonify({'error': f'文件删除失败: {str(e)}'}), 500
        else:
            logger.warning(f"文件不存在，跳过删除: {file_path}")
        
        db.session.delete(attachment)
        db.session.commit()
        logger.info("数据库记录删除成功")
        return jsonify({'message': '附件删除成功'}), 200
        
    except Exception as e:
        logger.error(f"删除附件时发生错误: {str(e)}")
        return jsonify({'error': f'删除附件时发生错误: {str(e)}'}), 500

@api_assay_data_bp.route('/attachments/<related_type>/<int:related_id>', methods=['GET'])
@api_login_required
@permission_required('attachment_read')
def list_attachments(related_type, related_id):
    """
    获取指定对象的附件列表
    """
    try:
        attachments = Attachment.query.filter_by(
            related_type=related_type,
            related_id=related_id
        ).all()
        
        return jsonify({
            'attachments': [{
                'id': attachment.id,
                'related_type': attachment.related_type,
                'related_id': attachment.related_id,
                'file_path': attachment.file_path,
                'original_name': attachment.original_name,
                'file_type': attachment.file_type,
                'file_size': attachment.file_size,
                'created_at': attachment.created_at.isoformat()
            } for attachment in attachments]
        }), 200
        
    except Exception as e:
        logger.error(f"获取附件列表时发生错误: {str(e)}")
        return jsonify({'error': f'获取附件列表时发生错误: {str(e)}'}), 500

# 化验数据附件相关API
@api_assay_data_bp.route('/assay-attachments', methods=['POST'])
@api_login_required
@permission_required('attachment_create')
def upload_assay_attachment():
    """
    上传化验数据附件
    """
    try:
        file = request.files.get('file')
        assay_data_id = request.form.get('assay_data_id')
        
        if not file or not file.filename:
            return jsonify({'error': '请选择要上传的文件'}), 400
            
        if not assay_data_id:
            return jsonify({'error': '缺少化验数据ID'}), 400
            
        # 验证化验数据是否存在
        assay_data = AssayData.query.get(assay_data_id)
        if not assay_data:
            return jsonify({'error': '化验数据不存在'}), 404
            
        # 检查文件类型（只允许图片）
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': '只允许上传图片文件（jpg, jpeg, png, gif）'}), 400
            
        from flask import current_app
        
        # 创建上传目录
        upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'assay', assay_data.sample_name, datetime.now().strftime('%Y%m%d'))
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成存储文件名
        name, ext = os.path.splitext(file.filename)
        stored_name = f"{assay_data.sample_name}{ext}"
        
        # 检查是否已存在同名文件，如果存在则添加后缀
        counter = 1
        final_name = stored_name
        while os.path.exists(os.path.join(upload_dir, final_name)):
            final_name = f"{assay_data.sample_name}-{counter}{ext}"
            counter += 1
        
        file_path = os.path.join(upload_dir, final_name)
        
        # 保存文件
        file.save(file_path)
        
        # 检查文件是否保存成功
        if not os.path.exists(file_path):
            logger.error(f"文件保存失败: {file_path}")
            return jsonify({'error': '文件保存失败'}), 500
            
        # 创建附件记录
        attachment = Attachment(
            related_type='assay_data',
            related_id=int(assay_data_id),
            file_path=file_path,
            original_name=file.filename,
            stored_name=final_name,
            file_type=file_ext,
            file_size=os.path.getsize(file_path),
            created_by=current_user.id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'id': attachment.id,
            'related_type': attachment.related_type,
            'related_id': attachment.related_id,
            'file_path': attachment.file_path,
            'original_name': attachment.original_name,
            'file_type': attachment.file_type,
            'file_size': attachment.file_size,
            'created_at': attachment.created_at.isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"上传化验数据附件时发生错误: {str(e)}")
        return jsonify({'error': f'上传附件时发生错误: {str(e)}'}), 500

@api_assay_data_bp.route('/assay-attachments/<int:attachment_id>/preview')
@api_login_required
@permission_required('attachment_read')
def preview_assay_attachment(attachment_id):
    """
    预览化验数据附件
    """
    try:
        from flask import current_app
        
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证附件类型
        if attachment.related_type != 'assay_data':
            return jsonify({'error': '附件类型不正确'}), 400
            
        # 验证化验数据权限
        assay_data = AssayData.query.get(attachment.related_id)
        if not assay_data:
            return jsonify({'error': '关联的化验数据不存在'}), 404
            
        # 检查用户权限
        if not current_user.has_permission_name('assay_data_read_all'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if assay_data.factory_id not in factory_ids:
                return jsonify({'error': '您没有权限查看此附件'}), 403
        
        # 验证文件记录
        if not attachment.file_path:
            logger.error(f"附件记录中缺少文件路径: {attachment_id}")
            return jsonify({'error': '文件路径信息不完整'}), 400
            
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(attachment.file_path)
        logger.info(f"尝试预览文件: {file_path}")
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 验证路径安全性（防止路径遍历攻击）
            if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                logger.error(f"文件路径不安全: {file_path}")
                return jsonify({'error': '文件路径不安全'}), 400
                
            # 获取文件扩展名（使用os.path.splitext确保兼容性）
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 根据文件类型设置MIME类型
            mime_types = {
                '.pdf': 'application/pdf',
                '.txt': 'text/plain',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }
            
            # 如果是支持预览的文件类型，直接显示
            if file_ext in mime_types:
                logger.info(f"预览文件类型: {file_ext}")
                return send_file(file_path, as_attachment=False, mimetype=mime_types[file_ext])
            else:
                logger.warning(f"不支持预览的文件类型: {file_ext}")
                return jsonify({'error': '该文件类型不支持预览'}), 400
        else:
            logger.error(f"文件不存在: {file_path}")
            return jsonify({'error': f'文件不存在: {attachment.original_name}'}), 404
            
    except Exception as e:
        logger.error(f"预览化验数据附件时发生错误: {str(e)}")
        return jsonify({'error': f'预览附件时发生错误: {str(e)}'}), 500

@api_assay_data_bp.route('/assay-attachments/<int:attachment_id>', methods=['DELETE'])
@api_login_required
@permission_required('attachment_delete')
def delete_assay_attachment(attachment_id):
    """
    删除化验数据附件
    """
    try:
        from flask import current_app
        
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证附件类型
        if attachment.related_type != 'assay_data':
            return jsonify({'error': '附件类型不正确'}), 400
            
        # 验证化验数据权限
        assay_data = AssayData.query.get(attachment.related_id)
        if not assay_data:
            return jsonify({'error': '关联的化验数据不存在'}), 404
            
        # 检查用户权限
        if not current_user.has_permission_name('assay_data_update_all'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if assay_data.factory_id not in factory_ids:
                return jsonify({'error': '您没有权限删除此附件'}), 403
        
        # 验证文件记录
        if not attachment.file_path:
            logger.error(f"附件记录中缺少文件路径: {attachment_id}")
            return jsonify({'error': '文件路径信息不完整'}), 400
            
        # 使用os.path.abspath获取绝对路径
        file_path = os.path.abspath(attachment.file_path)
        logger.info(f"尝试删除文件: {file_path}")
        
        # 删除文件系统中的文件
        if os.path.exists(file_path):
            try:
                # 验证路径安全性
                if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                    logger.error(f"文件路径不安全: {file_path}")
                    return jsonify({'error': '文件路径不安全'}), 400
                    
                os.remove(file_path)
                logger.info(f"文件删除成功: {file_path}")
            except PermissionError:
                logger.error(f"没有权限删除文件: {file_path}")
                return jsonify({'error': f'没有权限删除文件: {attachment.original_name}'}), 403
            except Exception as e:
                logger.error(f"文件删除失败: {str(e)}")
                return jsonify({'error': f'文件删除失败: {str(e)}'}), 500
        else:
            logger.warning(f"文件不存在，跳过删除: {file_path}")
        
        db.session.delete(attachment)
        db.session.commit()
        logger.info("数据库记录删除成功")
        return jsonify({'message': '附件删除成功'}), 200
        
    except Exception as e:
        logger.error(f"删除化验数据附件时发生错误: {str(e)}")
        return jsonify({'error': f'删除附件时发生错误: {str(e)}'}), 500

@api_assay_data_bp.route('/assay-attachments/assay-data/<int:assay_data_id>', methods=['GET'])
@api_login_required
@permission_required('attachment_read')
def list_assay_attachments(assay_data_id):
    """
    获取指定化验数据的附件列表
    """
    try:
        # 验证化验数据是否存在
        assay_data = AssayData.query.get_or_404(assay_data_id)
        
        # 检查用户权限
        if not current_user.has_permission_name('assay_data_update_all'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if assay_data.factory_id not in factory_ids:
                return jsonify({'error': '您没有权限查看此化验数据的附件'}), 403
        
        attachments = Attachment.query.filter_by(
            related_type='assay_data',
            related_id=assay_data_id
        ).all()
        
        return jsonify({
            'attachments': [{
                'id': attachment.id,
                'related_type': attachment.related_type,
                'related_id': attachment.related_id,
                'file_path': attachment.file_path,
                'original_name': attachment.original_name,
                'file_type': attachment.file_type,
                'file_size': attachment.file_size,
                'created_at': attachment.created_at.isoformat()
            } for attachment in attachments]
        }), 200
        
    except Exception as e:
        logger.error(f"获取化验数据附件列表时发生错误: {str(e)}")
        return jsonify({'error': f'获取附件列表时发生错误: {str(e)}'}), 500