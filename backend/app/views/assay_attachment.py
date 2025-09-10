from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models.attachment import Attachment
from app.models.assay_data import AssayData
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

assay_attachment_bp = Blueprint('assay_attachment', __name__, url_prefix='/assay-attachment')

def create_assay_upload_directory(sample_name):
    """
    创建化验数据上传目录
    :param sample_name: 样品名称
    """
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'assay', sample_name, datetime.now().strftime('%Y%m%d'))
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def generate_assay_filename(original_name, sample_name):
    """
    生成化验数据文件存储名
    :param original_name: 原始文件名
    :param sample_name: 样品名称
    """
    name, ext = os.path.splitext(original_name)
    # 检查是否已存在同名文件，如果存在则添加后缀
    stored_name = f"{sample_name}{ext}"
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'assay', sample_name, datetime.now().strftime('%Y%m%d'))
    
    counter = 1
    final_name = stored_name
    while os.path.exists(os.path.join(upload_dir, final_name)):
        final_name = f"{sample_name}-{counter}{ext}"
        counter += 1
    
    return final_name

@assay_attachment_bp.route('/upload', methods=['POST'])
@login_required
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
            
        # 创建上传目录
        upload_dir = create_assay_upload_directory(assay_data.sample_name)
        
        # 生成存储文件名
        stored_name = generate_assay_filename(file.filename, assay_data.sample_name)
        file_path = os.path.join(upload_dir, stored_name)
        
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
            stored_name=stored_name,
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

@assay_attachment_bp.route('/<int:attachment_id>/preview')
@login_required
def preview_assay_attachment(attachment_id):
    """
    预览化验数据附件
    """
    try:
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证附件类型
        if attachment.related_type != 'assay_data':
            return jsonify({'error': '附件类型不正确'}), 400
            
        # 验证化验数据权限
        assay_data = AssayData.query.get(attachment.related_id)
        if not assay_data:
            return jsonify({'error': '关联的化验数据不存在'}), 404
            
        # 检查用户权限
        if not current_user.has_permission('assay_data_delete_all'):
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

@assay_attachment_bp.route('/<int:attachment_id>', methods=['DELETE'])
@login_required
def delete_assay_attachment(attachment_id):
    """
    删除化验数据附件
    """
    try:
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证附件类型
        if attachment.related_type != 'assay_data':
            return jsonify({'error': '附件类型不正确'}), 400
            
        # 验证化验数据权限
        assay_data = AssayData.query.get(attachment.related_id)
        if not assay_data:
            return jsonify({'error': '关联的化验数据不存在'}), 404
            
        # 检查用户权限
        if not current_user.has_permission('assay_data_delete_all'):
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

@assay_attachment_bp.route('/assay-data/<int:assay_data_id>', methods=['GET'])
@login_required
def list_assay_attachments(assay_data_id):
    """
    获取指定化验数据的附件列表
    """
    try:
        # 验证化验数据是否存在
        assay_data = AssayData.query.get_or_404(assay_data_id)
        
        # 检查用户权限
        if not current_user.has_permission('assay_data_update_all'):
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
