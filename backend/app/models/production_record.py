from app import db
from datetime import datetime

class ProductionRecord(db.Model):
    __tablename__ = 'production_records'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)  # 日期 - 添加索引用于日期查询
    factory_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False, index=True)  # 分厂ID - 添加索引用于权限筛选
    team_id = db.Column(db.Integer, db.ForeignKey('departments.id'), index=True)  # 班组ID - 添加索引
    recorder_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # 记录人ID - 添加索引
    material_name = db.Column(db.String(100), nullable=False, index=True)  # 物料名称 - 添加索引用于搜索
    quantity = db.Column(db.Float, nullable=False)  # 产量
    water_content = db.Column(db.Float)  # 水含量
    zinc_content = db.Column(db.Float)  # 锌含量
    lead_content = db.Column(db.Float)  # 铅含量
    chlorine_content = db.Column(db.Float)  # 氯含量
    fluorine_content = db.Column(db.Float)  # 氟含量
    remarks = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)  # 创建时间 - 添加索引用于排序
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间
    
    # 协作功能支持字段
    status = db.Column(db.String(20), default='draft', index=True)  # 记录状态 - 添加索引用于状态筛选
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # 创建人ID - 添加索引
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # 完成人ID - 添加索引
    
    # 关联关系
    factory = db.relationship('Department', foreign_keys=[factory_id])
    team = db.relationship('Department', foreign_keys=[team_id])
    recorder = db.relationship('User', foreign_keys=[recorder_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    completer = db.relationship('User', foreign_keys=[completed_by])
    
    def __repr__(self):
        return f'<ProductionRecord {self.id}: {self.material_name} ({self.date})>'