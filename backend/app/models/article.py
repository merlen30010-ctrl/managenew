from app import db
from datetime import datetime
from flask_login import current_user

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # 文章标题
    content = db.Column(db.Text)  # 文章内容
    summary = db.Column(db.Text)  # 文章摘要
    category_id = db.Column(db.Integer, db.ForeignKey('article_categories.id'))  # 分类ID
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 作者ID
    status = db.Column(db.String(20), default='draft')  # 状态：draft/published/archived
    is_featured = db.Column(db.Boolean, default=False)  # 是否置顶
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间
    published_at = db.Column(db.DateTime)  # 发布时间
    
    # 关联关系
    author = db.relationship('User', backref='articles')
    
    def __repr__(self):
        return f'<Article {self.title}>'
    
    def to_dict(self, include_content=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'author_id': self.author_id,
            'author_name': self.author.username if self.author else None,
            'status': self.status,
            'is_featured': self.is_featured,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        
        if include_content:
            data['content'] = self.content
            
        return data
    
    def publish(self):
        """发布文章"""
        self.status = 'published'
        self.published_at = datetime.now()
        db.session.commit()
    
    def archive(self):
        """归档文章"""
        self.status = 'archived'
        db.session.commit()
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()
    
    @staticmethod
    def get_published_articles(category_id=None, page=1, per_page=10):
        """获取已发布的文章列表"""
        query = Article.query.filter_by(status='published')
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        return query.order_by(Article.is_featured.desc(), Article.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_featured_articles(limit=5):
        """获取置顶文章"""
        return Article.query.filter_by(status='published', is_featured=True).order_by(
            Article.published_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def search_articles(keyword, page=1, per_page=10):
        """搜索文章"""
        return Article.query.filter(
            Article.status == 'published',
            db.or_(
                Article.title.contains(keyword),
                Article.content.contains(keyword),
                Article.summary.contains(keyword)
            )
        ).order_by(Article.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )