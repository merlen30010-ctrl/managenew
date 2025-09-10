from app import db

class Material(db.Model):
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 物料名称
    code = db.Column(db.String(50), unique=True, nullable=False)  # 物料代码
    full_name = db.Column(db.String(200))  # 物料全称
    purpose = db.Column(db.String(20))  # 用途：原料，辅料，产品，其他
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Material {self.name}>'