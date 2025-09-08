from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models.attachment import Attachment
from app.models.article import Article
from app.views.decorators import permission_required
from app.api.decorators import api_login_required
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

article_attachment_bp = Blueprint('article_attachment', __name__, url_prefix='/api/article-attachments')

def create_upload_directory():
    """
    创建文章附件上传目录
    """
    upload_dir = os.path.join(
        current_app.config.get('UPLOAD_FOLDER', 'uploads'), 
        'articles', 
        datetime.now().strftime('%Y%m')
    )
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def generate_filename(original_name, article_id):
    """
    生成文章附件存储文件名
    :param original_name: 原始文件名
    :param article_id: 文章ID
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    name, ext = os.path.splitext(original_name)
    return f"article_{article_id}_{timestamp}_{name}{ext}"

@article_attachment_bp.route('/upload', methods=['POST'])
@api_login_required
@permission_required('article_create')
def upload_article_attachment():
    """
    上传文章附件
    """
    try:
        file = request.files.get('file')
        article_id = request.form.get('article_id')
        module = request.form.get('module', 'article')  # 兼容前端模板中的module参数
        
        if not file or not file.filename:
            return jsonify({
                'success': False,
                'message': '请选择要上传的文件'
            }), 400
            
        # 如果没有提供article_id，创建临时记录
        if not article_id:
            article_id = 0  # 临时文章ID，后续保存文章时会更新
            
        # 验证文件类型和大小
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
            {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', 
             '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.zip', '.rar', '.7z'})
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'message': f'不支持的文件类型: {file_ext}'
            }), 400
            
        max_file_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
        if hasattr(file, 'content_length') and file.content_length > max_file_size:
            return jsonify({
                'success': False,
                'message': '文件大小超过限制'
            }), 400
        
        # 创建上传目录
        upload_dir = create_upload_directory()
        
        # 生成存储文件名
        stored_name = generate_filename(file.filename, article_id)
        file_path = os.path.join(upload_dir, stored_name)
        
        # 保存文件
        file.save(file_path)
        
        # 检查文件是否保存成功
        if not os.path.exists(file_path):
            logger.error(f"文件保存失败: {file_path}")
            return jsonify({
                'success': False,
                'message': '文件保存失败'
            }), 500
            
        # 创建附件记录
        attachment = Attachment(
            related_type='article',
            related_id=int(article_id) if article_id else 0,
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
            'success': True,
            'message': '文件上传成功',
            'data': {
                'id': attachment.id,
                'original_name': attachment.original_name,
                'file_type': attachment.file_type,
                'file_size': attachment.file_size,
                'created_at': attachment.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"上传文章附件时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'上传附件时发生错误: {str(e)}'
        }), 500

@article_attachment_bp.route('/<int:attachment_id>/download')
@api_login_required
@permission_required('article_read')
def download_article_attachment(attachment_id):
    """
    下载文章附件
    """
    try:
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证附件类型
        if attachment.related_type != 'article':
            return jsonify({
                'success': False,
                'message': '附件类型不正确'
            }), 400
            
        # 验证文章权限
        if attachment.related_id > 0:
            article = Article.query.get(attachment.related_id)
            if article and article.status != 'published':
                # 非发布状态的文章，需要检查权限
                if not (current_user.has_permission('article_manage') or 
                       (current_user.has_permission('article_edit') and article.author_id == current_user.id)):
                    return jsonify({
                        'success': False,
                        'message': '您没有权限下载此附件'
                    }), 403
        
        # 验证文件记录
        if not attachment.file_path:
            logger.error(f"附件记录中缺少文件路径: {attachment_id}")
            return jsonify({
                'success': False,
                'message': '文件路径信息不完整'
            }), 400
            
        # 使用绝对路径
        file_path = os.path.abspath(attachment.file_path)
        logger.info(f"尝试下载文件: {file_path}")
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 验证路径安全性
            if not os.path.commonpath([os.path.abspath(''), file_path]).startswith(os.path.abspath('')):
                logger.error(f"文件路径不安全: {file_path}")
                return jsonify({
                    'success': False,
                    'message': '文件路径不安全'
                }), 400
                
            filename = os.path.basename(file_path)
            logger.info(f"文件存在，准备下载: {filename}")
            return send_file(file_path, as_attachment=True, download_name=attachment.original_name)
        else:
            logger.error(f"文件不存在: {file_path}")
            return jsonify({
                'success': False,
                'message': f'文件不存在: {attachment.original_name}'
            }), 404
            
    except Exception as e:
        logger.error(f"下载文件时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'下载文件时发生错误: {str(e)}'
        }), 500

@article_attachment_bp.route('/<int:attachment_id>', methods=['DELETE'])
@api_login_required
@permission_required('article_edit')
def delete_article_attachment(attachment_id):
    """
    删除文章附件
    """
    try:
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 验证附件类型
        if attachment.related_type != 'article':
            return jsonify({
                'success': False,
                'message': '附件类型不正确'
            }), 400
            
        # 验证权限
        if attachment.related_id > 0:
            article = Article.query.get(attachment.related_id)
            if article:
                if not (current_user.has_permission('article_manage') or 
                       (current_user.has_permission('article_edit') and article.author_id == current_user.id)):
                    return jsonify({
                        'success': False,
                        'message': '您没有权限删除此附件'
                    }), 403
        
        # 删除文件系统中的文件
        if attachment.file_path and os.path.exists(attachment.file_path):
            try:
                os.remove(attachment.file_path)
                logger.info(f"文件删除成功: {attachment.file_path}")
            except Exception as e:
                logger.error(f"文件删除失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'文件删除失败: {str(e)}'
                }), 500
        else:
            logger.warning(f"文件不存在，跳过删除: {attachment.file_path}")
        
        # 删除数据库记录
        db.session.delete(attachment)
        db.session.commit()
        logger.info("数据库记录删除成功")
        
        return jsonify({
            'success': True,
            'message': '附件删除成功'
        }), 200
        
    except Exception as e:
        logger.error(f"删除附件时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除附件时发生错误: {str(e)}'
        }), 500

@article_attachment_bp.route('/list', methods=['GET'])
@api_login_required
@permission_required('article_read')
def list_article_attachments():
    """
    获取文章附件列表
    """
    try:
        module = request.args.get('module', 'article')
        module_id = request.args.get('module_id', type=int)
        article_id = request.args.get('article_id', type=int)  # 兼容参数
        
        # 兼容处理
        if not module_id and article_id:
            module_id = article_id
            
        if not module_id:
            return jsonify({
                'success': False,
                'message': '缺少文章ID参数'
            }), 400
            
        # 验证文章权限
        if module_id > 0:
            article = Article.query.get(module_id)
            if article and article.status != 'published':
                # 非发布状态的文章，需要检查权限
                if not (current_user.has_permission('article_manage') or 
                       (current_user.has_permission('article_edit') and article.author_id == current_user.id)):
                    return jsonify({
                        'success': False,
                        'message': '您没有权限查看此文章的附件'
                    }), 403
        
        attachments = Attachment.query.filter_by(
            related_type='article',
            related_id=module_id
        ).order_by(Attachment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': attachment.id,
                'original_name': attachment.original_name,
                'file_type': attachment.file_type,
                'file_size': attachment.file_size,
                'created_at': attachment.created_at.isoformat(),
                'download_url': f'/api/article-attachments/{attachment.id}/download'
            } for attachment in attachments]
        }), 200
        
    except Exception as e:
        logger.error(f"获取文章附件列表时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取附件列表时发生错误: {str(e)}'
        }), 500

@article_attachment_bp.route('/update-article-id', methods=['POST'])
@api_login_required
@permission_required('article_edit')
def update_attachment_article_id():
    """
    更新附件的文章ID（用于文章保存时关联临时上传的附件）
    """
    try:
        data = request.get_json()
        attachment_ids = data.get('attachment_ids', [])
        article_id = data.get('article_id')
        
        if not article_id or not attachment_ids:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
            
        # 验证文章权限
        article = Article.query.get(article_id)
        if not article:
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404
            
        if not (current_user.has_permission('article_manage') or 
               (current_user.has_permission('article_edit') and article.author_id == current_user.id)):
            return jsonify({
                'success': False,
                'message': '您没有权限操作此文章的附件'
            }), 403
        
        # 更新附件的文章ID
        updated_count = 0
        for attachment_id in attachment_ids:
            attachment = Attachment.query.filter_by(
                id=attachment_id,
                related_type='article',
                created_by=current_user.id
            ).first()
            
            if attachment:
                attachment.related_id = article_id
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功更新 {updated_count} 个附件的关联关系'
        }), 200
        
    except Exception as e:
        logger.error(f"更新附件文章ID时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新附件关联关系时发生错误: {str(e)}'
        }), 500