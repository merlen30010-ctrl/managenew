from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Article, ArticleCategory, User
from app.views.decorators import permission_required
from datetime import datetime

article_bp = Blueprint('article', __name__)

# 用户端路由
@article_bp.route('/articles')
@login_required
def user_list():
    """用户查看文章列表"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '')
    per_page = 10
    
    # 构建查询
    query = Article.query.filter_by(status='published')
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if keyword:
        query = query.filter(
            db.or_(
                Article.title.contains(keyword),
                Article.content.contains(keyword),
                Article.summary.contains(keyword)
            )
        )
    
    articles = query.order_by(
        Article.is_featured.desc(),
        Article.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取分类列表
    categories = ArticleCategory.get_active_categories()
    
    # 获取置顶文章
    featured_articles = Article.get_featured_articles(limit=3)
    
    return render_template('articles/user_list.html', 
                         articles=articles, 
                         categories=categories,
                         featured_articles=featured_articles,
                         current_category_id=category_id,
                         keyword=keyword)

@article_bp.route('/articles/<int:article_id>')
@login_required
def user_detail(article_id):
    """用户查看文章详情"""
    article = Article.query.filter_by(id=article_id, status='published').first_or_404()
    
    # 增加浏览次数
    article.increment_view_count()
    
    # 获取相关文章（同分类的其他文章）
    related_articles = []
    if article.category_id:
        related_articles = Article.query.filter(
            Article.category_id == article.category_id,
            Article.id != article.id,
            Article.status == 'published'
        ).order_by(Article.published_at.desc()).limit(5).all()
    
    return render_template('articles/user_detail.html', 
                         article=article,
                         related_articles=related_articles)

# 管理端路由
@article_bp.route('/admin/articles')
@login_required
@permission_required('article_read')
def admin_list():
    """管理员查看文章列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    category_id = request.args.get('category_id', type=int)
    author_id = request.args.get('author_id', type=int)
    keyword = request.args.get('keyword', '')
    per_page = 15
    
    # 构建查询
    query = Article.query
    
    if status:
        query = query.filter_by(status=status)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if author_id:
        query = query.filter_by(author_id=author_id)
    
    if keyword:
        query = query.filter(
            db.or_(
                Article.title.contains(keyword),
                Article.content.contains(keyword)
            )
        )
    
    articles = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取分类和作者列表
    categories = ArticleCategory.query.all()
    authors = User.query.join(Article).distinct().all()
    
    return render_template('articles/admin_list.html',
                         articles=articles,
                         categories=categories,
                         authors=authors,
                         current_status=status,
                         current_category_id=category_id,
                         current_author_id=author_id,
                         keyword=keyword)

@article_bp.route('/admin/articles/create', methods=['GET', 'POST'])
@login_required
@permission_required('article_create')
def admin_create():
    """创建文章"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            summary = request.form.get('summary')
            category_id = request.form.get('category_id', type=int)
            status = request.form.get('status', 'draft')
            is_featured = bool(request.form.get('is_featured'))
            
            if not title:
                flash('文章标题不能为空', 'error')
                return redirect(url_for('article.admin_create'))
            
            article = Article(
                title=title,
                content=content,
                summary=summary,
                category_id=category_id if category_id else None,
                author_id=current_user.id,
                status=status,
                is_featured=is_featured
            )
            
            # 如果状态为发布，设置发布时间
            if status == 'published':
                article.published_at = datetime.now()
            
            db.session.add(article)
            db.session.commit()
            
            flash('文章创建成功', 'success')
            return redirect(url_for('article.admin_edit', article_id=article.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
    
    categories = ArticleCategory.get_active_categories()
    return render_template('articles/admin_form.html', categories=categories)

@article_bp.route('/admin/articles/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('article_update')
def admin_edit(article_id):
    """编辑文章"""
    article = Article.query.get_or_404(article_id)
    
    # 权限检查：只有作者或管理员可以编辑
    if article.author_id != current_user.id and not current_user.has_permission('article_manage'):
        flash('无权编辑此文章', 'error')
        return redirect(url_for('article.admin_list'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            summary = request.form.get('summary')
            category_id = request.form.get('category_id', type=int)
            status = request.form.get('status')
            is_featured = bool(request.form.get('is_featured'))
            
            if not title:
                flash('文章标题不能为空', 'error')
                return redirect(url_for('article.admin_edit', article_id=article_id))
            
            # 记录原状态
            old_status = article.status
            
            # 更新字段
            article.title = title
            article.content = content
            article.summary = summary
            article.category_id = category_id if category_id else None
            article.status = status
            article.is_featured = is_featured
            
            # 如果从草稿变为发布，设置发布时间
            if old_status != 'published' and status == 'published':
                article.published_at = datetime.now()
            
            db.session.commit()
            
            flash('文章更新成功', 'success')
            return redirect(url_for('article.admin_edit', article_id=article_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    categories = ArticleCategory.get_active_categories()
    return render_template('articles/admin_form.html', article=article, categories=categories)

@article_bp.route('/admin/articles/<int:article_id>/delete', methods=['POST'])
@login_required
@permission_required('article_delete')
def admin_delete(article_id):
    """删除文章"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # 权限检查：只有作者或管理员可以删除
        if article.author_id != current_user.id and not current_user.has_permission('article_manage'):
            return jsonify({'success': False, 'message': '无权删除此文章'}), 403
        
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '文章删除成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 测试编辑器路由
@article_bp.route('/test-editor')
@login_required
def test_editor():
    """测试编辑器页面"""
    return render_template('articles/test_editor.html')

@article_bp.route('/admin/articles/<int:article_id>/publish', methods=['POST'])
@login_required
@permission_required('article_publish')
def admin_publish(article_id):
    """发布文章"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # 权限检查
        if article.author_id != current_user.id and not current_user.has_permission('article_manage'):
            return jsonify({'success': False, 'message': '无权发布此文章'}), 403
        
        article.publish()
        
        return jsonify({'success': True, 'message': '文章发布成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@article_bp.route('/admin/articles/<int:article_id>/archive', methods=['POST'])
@login_required
@permission_required('article_manage')
def admin_archive(article_id):
    """归档文章"""
    try:
        article = Article.query.get_or_404(article_id)
        article.archive()
        
        return jsonify({'success': True, 'message': '文章归档成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 分类管理路由
@article_bp.route('/admin/article-categories')
@login_required
@permission_required('article_category_read')
def admin_category_list():
    """分类管理列表"""
    categories = ArticleCategory.query.order_by(ArticleCategory.sort_order).all()
    return render_template('articles/admin_category_list.html', categories=categories)

@article_bp.route('/admin/article-categories/create', methods=['GET', 'POST'])
@login_required
@permission_required('article_category_create')
def admin_category_create():
    """创建分类"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            sort_order = request.form.get('sort_order', 0, type=int)
            
            if not name:
                flash('分类名称不能为空', 'error')
                return redirect(url_for('article.admin_category_create'))
            
            # 检查分类名称是否已存在
            existing = ArticleCategory.query.filter_by(name=name).first()
            if existing:
                flash('分类名称已存在', 'error')
                return redirect(url_for('article.admin_category_create'))
            
            category = ArticleCategory(
                name=name,
                description=description,
                sort_order=sort_order
            )
            
            db.session.add(category)
            db.session.commit()
            
            flash('分类创建成功', 'success')
            return redirect(url_for('article.admin_category_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
    
    return render_template('articles/admin_category_create.html')

@article_bp.route('/admin/article-categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('article_category_update')
def admin_category_edit(category_id):
    """编辑分类"""
    category = ArticleCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            sort_order = request.form.get('sort_order', type=int)
            is_active = bool(request.form.get('is_active'))
            
            if not name:
                flash('分类名称不能为空', 'error')
                return redirect(url_for('article.admin_category_edit', category_id=category_id))
            
            # 检查分类名称是否已存在（排除当前分类）
            existing = ArticleCategory.query.filter(
                ArticleCategory.name == name,
                ArticleCategory.id != category_id
            ).first()
            if existing:
                flash('分类名称已存在', 'error')
                return redirect(url_for('article.admin_category_edit', category_id=category_id))
            
            category.name = name
            category.description = description
            category.sort_order = sort_order
            category.is_active = is_active
            
            db.session.commit()
            
            flash('分类更新成功', 'success')
            return redirect(url_for('article.admin_category_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('articles/admin_category_edit.html', category=category)

@article_bp.route('/admin/article-categories/<int:category_id>/delete', methods=['POST'])
@login_required
@permission_required('article_category_delete')
def admin_category_delete(category_id):
    """删除分类"""
    try:
        category = ArticleCategory.query.get_or_404(category_id)
        
        # 检查是否有文章使用此分类
        if category.articles.count() > 0:
            return jsonify({'success': False, 'message': '该分类下还有文章，无法删除'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '分类删除成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500