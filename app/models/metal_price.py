from app import db
from datetime import datetime

class MetalPrice(db.Model):
    __tablename__ = 'metal_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    metal_type = db.Column(db.String(50), default='1#锌', index=True)  # 金属种类 - 添加索引用于金属搜索
    quote_date = db.Column(db.Date, nullable=False, index=True)  # 报价日期 - 添加索引用于日期查询
    high_price = db.Column(db.Float)  # 最高价
    low_price = db.Column(db.Float)  # 最低价
    average_price = db.Column(db.Float, nullable=False, index=True)  # 均价 - 添加索引用于价格查询
    price_change = db.Column(db.Float, nullable=False)  # 涨跌
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # 创建时间 - 添加索引用于排序
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间
    
    def __repr__(self):
        return f'<MetalPrice {self.metal_type} {self.quote_date}>'
    
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'metal_type': self.metal_type,
            'quote_date': self.quote_date.strftime('%Y-%m-%d') if self.quote_date else None,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'average_price': self.average_price,
            'price_change': self.price_change,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }