from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models.attachment import Attachment
from app.models.customer import Customer
from app.models.material import Material
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

attachment_bp = Blueprint('attachment', __name__, url_prefix='/attachment')

def create_upload_directory(related_type):
    """
    创建上传目录
    """
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), related_type, datetime.now().strftime('%Y%m'))
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def generate_filename(original_name, related_type, related_id, naming_rule='default'):
    """
    生成文件存储名
    :param original_name: 原始文件名
    :param related_type: 关联对象类型
    :param related_id: 关联对象ID
    :param naming_rule: 命名规则 ('default' 或 'contract')
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    if naming_rule == 'contract' and related_type == 'contract':
        # 合同模块使用原有命名规则：客户名+物料名+时间戳+扩展名
        try:
            from app.models.contract import Contract
            contract = Contract.query.get(related_id)
            if contract:
                customer = Customer.query.get(contract.customer_id)
                material = Material.query.get(contract.material_id)
                if customer and material:
                    return f"{customer.name}_{material.name}_{timestamp}{os.path.splitext(original_name)[1]}"
        except Exception as e:
            logger.warning(f"使用合同命名规则时出错: {e}")
    
    # 默认命名规则：对象类型_对象ID_时间戳_原始文件名
    name, ext = os.path.splitext(original_name)
    return f"{related_type}_{related_id}_{timestamp}{ext}"

@attachment_bp.route('/', methods=['POST'])
@login_required
def upload_attachment():
    """
    上传附件
    """
    try:
        file = request.files.get('file')
        related_type = request.form.get('related_type')
        related_id = request.form.get('related_id')
        description = request.form.get('description')
        naming_rule = request.form.get('naming_rule', 'default')  # 命名规则参数
        
        if not file or not file.filename:
            return jsonify({'error': '请选择要上传的文件'}), 400
            
        if not related_type or not related_id:
            return jsonify({'error': '缺少关联对象信息'}), 400
            
        if not description:
            return jsonify({'error': '请填写附件说明'}), 400
            
        # 创建上传目录
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
            description=description,
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
            'description': attachment.description,
            'created_at': attachment.created_at.isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"上传附件时发生错误: {str(e)}")
        return jsonify({'error': f'上传附件时发生错误: {str(e)}'}), 500

@attachment_bp.route('/<int:attachment_id>/download')
@login_required
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

@attachment_bp.route('/<int:attachment_id>/preview')
@login_required
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

@attachment_bp.route('/<int:attachment_id>', methods=['DELETE'])
@login_required
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

@attachment_bp.route('/<related_type>/<int:related_id>', methods=['GET'])
@login_required
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
                'description': attachment.description,
                'created_at': attachment.created_at.isoformat()
            } for attachment in attachments]
        }), 200
        
    except Exception as e:
        logger.error(f"获取附件列表时发生错误: {str(e)}")
        return jsonify({'error': f'获取附件列表时发生错误: {str(e)}'}), 500
