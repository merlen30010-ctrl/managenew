from app import db
from datetime import datetime

class ArticleCategory(db.Model):
    __tablename__ = 'article_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # 分类名称
    description = db.Column(db.Text)  # 分类描述
    sort_order = db.Column(db.Integer, default=0)  # 排序
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    
    # 关联关系
    articles = db.relationship('Article', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ArticleCategory {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'article_count': self.articles.filter_by(status='published').count()
        }
    
    @staticmethod
    def get_active_categories():
        """获取所有启用的分类"""
        return ArticleCategory.query.filter_by(is_active=True).order_by(ArticleCategory.sort_order).all()