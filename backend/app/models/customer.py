from app import db

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 客户名称
    code = db.Column(db.String(50), unique=True, nullable=False)  # 客户代码
    full_name = db.Column(db.String(200))  # 客户全称
    customer_type = db.Column(db.String(20))  # 类型：原料供应，产品采购，辅料供应，其他
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Customer {self.name}>'