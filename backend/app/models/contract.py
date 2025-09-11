from app import db
import json
from datetime import datetime

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    # 计价方式枚举
    PRICING_METHODS = {
        'weight': '金吨计价',
        'content': '含量加点',
        'processing': '加工费用',
        'gross_weight': '毛吨计价'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    contract_type = db.Column(db.String(20), index=True)  # 类型：原料采购，辅料采购，产品销售，其他
    contract_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 合同编号
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), index=True)  # 客户ID
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), index=True)  # 物料ID
    factory_id = db.Column(db.Integer, db.ForeignKey('departments.id'), index=True)  # 分厂ID
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # 负责人ID
    sign_date = db.Column(db.Date, index=True)  # 签订日期
    expiry_date = db.Column(db.Date, index=True)  # 到期日期
    tax_rate = db.Column(db.Float, default=0.0)  # 税率
    pricing_method = db.Column(db.String(20), index=True)  # 计价方式
    coefficient = db.Column(db.Float)  # 系数
    status = db.Column(db.String(20), default='执行', index=True)  # 阶段：执行，归档
    # 新增布尔字段与操作日志（JSON文本）
    is_tax_inclusive = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_invoice_received = db.Column(db.Boolean, default=False, nullable=False, index=True)
    operation_logs = db.Column(db.Text, default='[]', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # 关联关系
    customer = db.relationship('Customer', backref='contracts')
    material = db.relationship('Material', backref='contracts')
    factory = db.relationship('Department', backref='contracts')
    responsible = db.relationship('User', backref='managed_contracts')
    
    def __repr__(self):
        return f'<Contract {self.contract_number}>'
    
    @property
    def pricing_method_display(self):
        """获取计价方式的显示名称"""
        return self.PRICING_METHODS.get(self.pricing_method, self.pricing_method)
    
    def calculate_price(self, base_price, quantity):
        """根据计价方式和系数计算价格"""
        if self.coefficient is None:
            return base_price * quantity
            
        if self.pricing_method == 'weight':
            # 金吨计价：基础价格 + 系数
            return (base_price + self.coefficient) * quantity
        elif self.pricing_method == 'content':
            # 含量加点：基础价格 * (1 + 系数/100)
            return base_price * (1 + self.coefficient / 100) * quantity
        elif self.pricing_method == 'processing':
            # 加工费用：基础价格 + 系数
            return (base_price + self.coefficient) * quantity
        elif self.pricing_method == 'gross_weight':
            # 毛吨计价：基础价格 + 系数
            return (base_price + self.coefficient) * quantity
        else:
            return base_price * quantity
    
    # 操作日志相关方法
    def _get_logs(self):
        try:
            return json.loads(self.operation_logs) if self.operation_logs else []
        except Exception:
            return []
    
    def _set_logs(self, logs):
        try:
            self.operation_logs = json.dumps(logs, ensure_ascii=False)
        except Exception:
            # 最差情况下避免因日志序列化影响主流程
            self.operation_logs = '[]'
    
    def append_log(self, action, actor_id=None, details=None):
        """追加一条操作日志，JSON格式存储在operation_logs
        action: 字符串，如 create/update/status_change/attachment_upload/attachment_delete
        actor_id: 执行人的用户ID
        details: 任意可JSON序列化的dict
        """
        entry = {
            'ts': datetime.utcnow().isoformat() + 'Z',
            'action': action,
            'actor_id': actor_id,
            'details': details or {}
        }
        logs = self._get_logs()
        logs.append(entry)
        self._set_logs(logs)
        return entry
    
    @property
    def operation_logs_list(self):
        return self._get_logs()

class ContractFile(db.Model):
    __tablename__ = 'contract_files'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    file_path = db.Column(db.String(200))  # 文件路径
    file_name = db.Column(db.String(100))  # 文件名
    file_type = db.Column(db.String(10))  # 文件类型
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # 关联关系
    contract = db.relationship('Contract', backref='files')
    
    def __repr__(self):
        return f'<ContractFile {self.file_name}>'