from app import db
from app import db
from datetime import datetime

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    # 附件关联的对象类型（如：contract, user, material等）
    related_type = db.Column(db.String(50), nullable=False)
    # 附件关联的对象ID
    related_id = db.Column(db.Integer, nullable=False)
    # 文件路径
    file_path = db.Column(db.String(200))
    # 原始文件名
    original_name = db.Column(db.String(100))
    # 存储文件名
    stored_name = db.Column(db.String(100))
    # 文件类型
    file_type = db.Column(db.String(10))
    # 文件大小
    file_size = db.Column(db.Integer)
    # 附件说明
    description = db.Column(db.String(200))
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.now)
    # 创建人
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 关联关系
    creator = db.relationship('User', backref='attachments')
    
    def __repr__(self):
        return f'<Attachment {self.original_name}>'