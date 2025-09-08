from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    read_at = db.Column(db.DateTime)
    
    # 关联关系
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'

class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    exam_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_score = db.Column(db.Float, default=100.0)
    exam_date = db.Column(db.DateTime, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    user = db.relationship('User', backref='exam_results')
    
    def __repr__(self):
        return f'<ExamResult {self.exam_name}: {self.score}/{self.total_score}>'
    
    @property
    def percentage(self):
        """计算百分比"""
        if self.total_score:
            return round((self.score / self.total_score) * 100, 2)
        return 0