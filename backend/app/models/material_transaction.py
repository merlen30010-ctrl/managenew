from app import db
from datetime import datetime

class MaterialTransaction(db.Model):
    __tablename__ = 'material_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)  # 日期 - 添加索引用于日期查询
    customer = db.Column(db.String(100), nullable=False, index=True)  # 客户 - 添加索引用于客户搜索
    material_name = db.Column(db.String(100), nullable=False, index=True)  # 物料名称 - 添加索引用于物料搜索
    factory_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False, index=True)  # 分厂ID - 添加索引用于权限筛选
    contract_number = db.Column(db.String(50), index=True)  # 合同编号 - 添加索引用于合同查询
    transaction_type = db.Column(db.String(20), nullable=False, index=True)  # 类型（进厂/出厂）- 添加索引用于类型筛选
    packaging = db.Column(db.String(50))  # 包装
    vehicle_number = db.Column(db.String(20), index=True)  # 车号 - 添加索引用于车辆查询
    shipped_quantity = db.Column(db.Float, nullable=False)  # 发数
    received_quantity = db.Column(db.Float, nullable=False)  # 到数
    water_content = db.Column(db.Float)  # 水含量
    zinc_content = db.Column(db.Float)  # 锌含量
    lead_content = db.Column(db.Float)  # 铅含量
    chlorine_content = db.Column(db.Float)  # 氯含量
    fluorine_content = db.Column(db.Float)  # 氟含量
    remarks = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)  # 创建时间 - 添加索引用于排序
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间
    
    # 分工协作支持字段
    status = db.Column(db.String(20), default='draft')  # 记录状态: draft(草稿), weighing(过磅完成), assaying(化验完成), completed(完成)
    weighing_completed = db.Column(db.Boolean, default=False)  # 过磅数据是否完成
    assaying_completed = db.Column(db.Boolean, default=False)  # 化验数据是否完成
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人ID
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 完成人ID
    weighing_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 过磅操作人ID
    assaying_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 化验操作人ID
    
    # 关联关系
    factory = db.relationship('Department', foreign_keys=[factory_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    completer = db.relationship('User', foreign_keys=[completed_by])
    weigher = db.relationship('User', foreign_keys=[weighing_by])
    assayer = db.relationship('User', foreign_keys=[assaying_by])
    
    def __repr__(self):
        return f'<MaterialTransaction {self.id}: {self.material_name} ({self.transaction_type})>'