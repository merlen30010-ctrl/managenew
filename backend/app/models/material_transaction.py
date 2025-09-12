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
    
    # 分工协作支持字段 - 修改状态定义
    status = db.Column(db.String(20), default='loading')  # 记录状态: loading(装车), arrived(到厂), stored(入库), used(使用)
    editable = db.Column(db.Boolean, default=True)  # 是否可编辑
    
    # 司机信息字段
    driver_name = db.Column(db.String(50))  # 司机姓名
    driver_phone = db.Column(db.String(20))  # 司机电话
    driver_id_card = db.Column(db.String(20))  # 司机身份证
    
    # 状态变更记录字段
    loading_time = db.Column(db.DateTime)  # 装车时间
    arrival_time = db.Column(db.DateTime)  # 到厂时间
    storage_time = db.Column(db.DateTime)  # 入库时间
    usage_time = db.Column(db.DateTime)  # 使用时间
    
    # 操作人员字段
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人ID
    loading_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 装车操作人ID
    arrival_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 到厂确认人ID
    storage_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 入库操作人ID
    usage_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 使用操作人ID
    
    # 关联关系
    factory = db.relationship('Department', foreign_keys=[factory_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    loader = db.relationship('User', foreign_keys=[loading_by])
    arriver = db.relationship('User', foreign_keys=[arrival_by])
    storer = db.relationship('User', foreign_keys=[storage_by])
    user = db.relationship('User', foreign_keys=[usage_by])
    
    def __repr__(self):
        return f'<MaterialTransaction {self.id}: {self.material_name} ({self.transaction_type})>'