import os
import logging
from datetime import datetime
from flask import current_app
from flask_login import current_user
from app import db
from app.models.attachment import Attachment

logger = logging.getLogger(__name__)

def create_upload_directory(folder_name):
    """
    创建上传目录
    """
    upload_dir = os.path.join(
        current_app.config.get('UPLOAD_FOLDER', 'uploads'), 
        folder_name, 
        datetime.now().strftime('%Y%m')
    )
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def generate_filename(original_name, folder_name):
    """
    生成文件存储名
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    name, ext = os.path.splitext(original_name)
    return f"{folder_name}_{timestamp}_{name}{ext}"

def save_uploaded_file(file, folder_name, related_type='vehicle', related_id=0):
    """
    保存上传的文件并创建附件记录
    
    Args:
        file: 上传的文件对象
        folder_name: 文件夹名称
        related_type: 关联类型
        related_id: 关联ID
    
    Returns:
        Attachment: 创建的附件记录，失败时返回None
    """
    try:
        if not file or not file.filename:
            return None
            
        # 验证文件类型
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            logger.error(f"不支持的文件类型: {file_ext}")
            return None
            
        # 验证文件大小 (最大10MB)
        max_file_size = 10 * 1024 * 1024
        if hasattr(file, 'content_length') and file.content_length > max_file_size:
            logger.error("文件大小超过限制")
            return None
            
        # 创建上传目录
        upload_dir = create_upload_directory(folder_name)
        
        # 生成存储文件名
        stored_name = generate_filename(file.filename, folder_name)
        file_path = os.path.join(upload_dir, stored_name)
        
        # 保存文件
        file.save(file_path)
        
        # 检查文件是否保存成功
        if not os.path.exists(file_path):
            logger.error(f"文件保存失败: {file_path}")
            return None
            
        # 创建附件记录
        attachment = Attachment(
            related_type=related_type,
            related_id=related_id,
            file_path=file_path,
            original_name=file.filename,
            stored_name=stored_name,
            file_type=file_ext,
            file_size=os.path.getsize(file_path),
            created_by=getattr(current_user, 'id', None)
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        logger.info(f"文件上传成功: {file_path}")
        return attachment
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        db.session.rollback()
        return None