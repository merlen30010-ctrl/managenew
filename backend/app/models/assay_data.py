from app import db
from datetime import datetime

class AssayData(db.Model):
    __tablename__ = 'assay_data'
    
    id = db.Column(db.Integer, primary_key=True)
    sample_name = db.Column(db.String(100), nullable=False, comment='样品名称')
    factory_id = db.Column(db.Integer, nullable=False, comment='分厂ID')
    
    # 常用指标
    water_content = db.Column(db.Float, comment='水含量')
    zinc_content = db.Column(db.Float, comment='锌含量')
    lead_content = db.Column(db.Float, comment='铅含量')
    chlorine_content = db.Column(db.Float, comment='氯含量')
    
    # 其他指标
    fluorine_content = db.Column(db.Float, comment='氟含量')
    iron_content = db.Column(db.Float, comment='铁含量')
    silicon_content = db.Column(db.Float, comment='硅含量')
    sulfur_content = db.Column(db.Float, comment='硫含量')
    high_heat = db.Column(db.Float, comment='高热值')
    low_heat = db.Column(db.Float, comment='低热值')
    silver_content = db.Column(db.Float, comment='银含量')
    recovery_rate = db.Column(db.Float, comment='回收率')
    
    # 备注
    remarks = db.Column(db.Text, comment='备注信息')
    
    # 关联信息
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f'<AssayData {self.sample_name}>'