from flask import request, jsonify
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import Article, ArticleCategory
from app import db
from app.views.decorators import permission_required
from datetime import datetime

# 文章分类API
@api_bp.route('/article-categories', methods=['GET'])
@login_required
def get_article_categories():
    """获取文章分类列表"""
    try:
        categories = ArticleCategory.get_active_categories()
        return jsonify({
            'success': True,
            'data': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/article-categories', methods=['POST'])
@login_required
@permission_required('article_category_create')
def create_article_category():
    """创建文章分类"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
        
        # 检查分类名称是否已存在
        existing = ArticleCategory.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'success': False, 'message': '分类名称已存在'}), 400
        
        category = ArticleCategory(
            name=data['name'],
            description=data.get('description', ''),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分类创建成功',
            'data': category.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/article-categories/<int:category_id>', methods=['PUT'])
@login_required
@permission_required('article_category_edit')
def update_article_category(category_id):
    """更新文章分类"""
    try:
        category = ArticleCategory.query.get_or_404(category_id)
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
        
        # 检查分类名称是否已存在（排除当前分类）
        existing = ArticleCategory.query.filter(
            ArticleCategory.name == data['name'],
            ArticleCategory.id != category_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': '分类名称已存在'}), 400
        
        category.name = data['name']
        category.description = data.get('description', category.description)
        category.sort_order = data.get('sort_order', category.sort_order)
        category.is_active = data.get('is_active', category.is_active)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分类更新成功',
            'data': category.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/article-categories/<int:category_id>', methods=['DELETE'])
@login_required
@permission_required('article_category_delete')
def delete_article_category(category_id):
    """删除文章分类"""
    try:
        category = ArticleCategory.query.get_or_404(category_id)
        
        # 检查是否有文章使用此分类
        if category.articles.count() > 0:
            return jsonify({'success': False, 'message': '该分类下还有文章，无法删除'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分类删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 文章API
@api_bp.route('/articles', methods=['GET'])
@login_required
def get_articles():
    """获取文章列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status', 'published')
        keyword = request.args.get('keyword', '')
        
        # 构建查询
        query = Article.query
        
        # 根据权限过滤
        if not current_user.has_permission_name('article_manage'):
            # 普通用户只能看到已发布的文章
            query = query.filter_by(status='published')
        else:
            # 管理员可以看到指定状态的文章
            if status:
                query = query.filter_by(status=status)
        
        # 分类过滤
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                db.or_(
                    Article.title.contains(keyword),
                    Article.content.contains(keyword),
                    Article.summary.contains(keyword)
                )
            )
        
        # 排序和分页
        pagination = query.order_by(
            Article.is_featured.desc(),
            Article.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'articles': [article.to_dict() for article in pagination.items],
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/articles/<int:article_id>', methods=['GET'])
@login_required
def get_article(article_id):
    """获取文章详情"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # 权限检查
        if article.status != 'published' and not current_user.has_permission_name('article_manage'):
            return jsonify({'success': False, 'message': '无权访问此文章'}), 403
        
        # 增加浏览次数（仅对已发布文章）
        if article.status == 'published':
            article.increment_view_count()
        
        return jsonify({
            'success': True,
            'data': article.to_dict(include_content=True)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/articles', methods=['POST'])
@login_required
@permission_required('article_create')
def create_article():
    """创建文章"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify({'success': False, 'message': '文章标题不能为空'}), 400
        
        article = Article(
            title=data['title'],
            content=data.get('content', ''),
            summary=data.get('summary', ''),
            category_id=data.get('category_id'),
            author_id=current_user.id,
            status=data.get('status', 'draft'),
            is_featured=data.get('is_featured', False)
        )
        
        # 如果状态为发布，设置发布时间
        if article.status == 'published':
            article.published_at = datetime.now()
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文章创建成功',
            'data': article.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/articles/<int:article_id>', methods=['PUT'])
@login_required
@permission_required('article_edit')
def update_article(article_id):
    """更新文章"""
    try:
        article = Article.query.get_or_404(article_id)
        data = request.get_json()
        
        # 权限检查：只有作者或管理员可以编辑
        if article.author_id != current_user.id and not current_user.has_permission_name('article_manage'):
            return jsonify({'success': False, 'message': '无权编辑此文章'}), 403
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify({'success': False, 'message': '文章标题不能为空'}), 400
        
        # 记录原状态
        old_status = article.status
        
        # 更新字段
        article.title = data['title']
        article.content = data.get('content', article.content)
        article.summary = data.get('summary', article.summary)
        article.category_id = data.get('category_id', article.category_id)
        article.status = data.get('status', article.status)
        article.is_featured = data.get('is_featured', article.is_featured)
        
        # 如果从草稿变为发布，设置发布时间
        if old_status != 'published' and article.status == 'published':
            article.published_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文章更新成功',
            'data': article.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@login_required
@permission_required('article_delete')
def delete_article(article_id):
    """删除文章"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # 权限检查：只有作者或管理员可以删除
        if article.author_id != current_user.id and not current_user.has_permission('article_manage'):
            return jsonify({'success': False, 'message': '无权删除此文章'}), 403
        
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文章删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/articles/<int:article_id>/publish', methods=['POST'])
@login_required
@permission_required('article_publish')
def publish_article(article_id):
    """发布文章"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # 权限检查
        if article.author_id != current_user.id and not current_user.has_permission('article_manage'):
            return jsonify({'success': False, 'message': '无权发布此文章'}), 403
        
        article.publish()
        
        return jsonify({
            'success': True,
            'message': '文章发布成功',
            'data': article.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/articles/<int:article_id>/archive', methods=['POST'])
@login_required
@permission_required('article_manage')
def archive_article(article_id):
    """归档文章"""
    try:
        article = Article.query.get_or_404(article_id)
        article.archive()
        
        return jsonify({
            'success': True,
            'message': '文章归档成功',
            'data': article.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/articles/featured', methods=['GET'])
@login_required
def get_featured_articles():
    """获取置顶文章"""
    try:
        limit = request.args.get('limit', 5, type=int)
        articles = Article.get_featured_articles(limit=limit)
        
        return jsonify({
            'success': True,
            'data': [article.to_dict() for article in articles]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500