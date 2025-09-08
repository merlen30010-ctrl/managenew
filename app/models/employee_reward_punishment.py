from app import db
from datetime import datetime
from sqlalchemy import Numeric

class EmployeeRewardPunishment(db.Model):
    """员工奖惩记录模型"""
    __tablename__ = 'employee_reward_punishment'
    
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    employee_id = db.Column(db.String(20), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工工号')
    
    # 奖惩基本信息
    type = db.Column(db.String(20), nullable=False, comment='类型：奖励/惩罚')
    category = db.Column(db.String(50), nullable=False, comment='奖惩类别')
    title = db.Column(db.String(200), nullable=False, comment='奖惩标题')
    description = db.Column(db.Text, comment='详细描述')
    
    # 奖惩详情
    reason = db.Column(db.Text, comment='奖惩原因')
    amount = db.Column(Numeric(10, 2), comment='奖惩金额')
    decision_date = db.Column(db.Date, nullable=False, comment='决定日期')
    effective_date = db.Column(db.Date, comment='生效日期')
    
    # 决定信息
    decision_maker = db.Column(db.String(50), comment='决定人')
    decision_department = db.Column(db.String(100), comment='决定部门')
    approval_level = db.Column(db.String(50), comment='审批级别')
    
    # 状态信息
    status = db.Column(db.String(20), default='生效', comment='状态')
    is_public = db.Column(db.Boolean, default=False, comment='是否公开')
    
    # 附件信息
    attachment_path = db.Column(db.String(500), comment='附件路径')
    attachment_name = db.Column(db.String(200), comment='附件名称')
    
    # 备注
    notes = db.Column(db.Text, comment='备注')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    employee = db.relationship('Employee', backref='reward_punishments')
    
    def __repr__(self):
        return f'<RewardPunishment {self.title}({self.employee_id})>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'type': self.type,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'reason': self.reason,
            'amount': float(self.amount) if self.amount else None,
            'decision_date': self.decision_date.isoformat() if self.decision_date else None,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'decision_maker': self.decision_maker,
            'decision_department': self.decision_department,
            'approval_level': self.approval_level,
            'status': self.status,
            'is_public': self.is_public,
            'attachment_path': self.attachment_path,
            'attachment_name': self.attachment_name,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RewardPunishmentType(db.Model):
    """奖惩类型配置模型"""
    __tablename__ = 'reward_punishment_types'
    
    id = db.Column(db.Integer, primary_key=True, comment='类型ID')
    type_code = db.Column(db.String(50), unique=True, nullable=False, comment='类型代码')
    type_name = db.Column(db.String(100), nullable=False, comment='类型名称')
    category = db.Column(db.String(20), nullable=False, comment='分类：奖励/惩罚')
    level = db.Column(db.String(20), comment='级别')
    has_amount = db.Column(db.Boolean, default=False, comment='是否涉及金额')
    requires_approval = db.Column(db.Boolean, default=True, comment='是否需要审批')
    approval_level = db.Column(db.String(50), comment='审批级别')
    description = db.Column(db.Text, comment='描述')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<RewardPunishmentType {self.type_name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'type_code': self.type_code,
            'type_name': self.type_name,
            'category': self.category,
            'level': self.level,
            'has_amount': self.has_amount,
            'requires_approval': self.requires_approval,
            'approval_level': self.approval_level,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }