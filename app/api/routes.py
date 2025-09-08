# API路由文件 - 已按模块拆分
# 拆分后的模块：
# - auth.py: 认证相关API（登录、注册、登出等）
# - user.py: 用户管理API
# - material.py: 物料管理API
# - customer.py: 客户管理API
# - department.py: 部门管理API
# - contract.py: 合同管理API
# - assay_data.py: 化验数据和附件相关API
# - material_transaction.py: 物料交易API
# 已存在的模块：excel.py, metal_price.py, vehicle.py

# 导入拆分后的模块以注册路由
from app.api import auth
from app.api import user
from app.api import material
from app.api import customer
from app.api import department
from app.api import contract
from app.api import assay_data
from app.api import material_transaction

# 导入已存在的模块
from app.api import excel
from app.api import metal_price
from app.api import vehicle

# 基础导入
from flask import jsonify, request
from app.api import api_bp
from app import db
from datetime import datetime
import logging
from flask_login import current_user

# 装饰器导入
from app.api.decorators import api_login_required, permission_required

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 生产记录相关API ====================
# TODO: 建议移动到 app/api/production_record.py

@api_bp.route('/production-records/<int:record_id>', methods=['DELETE'])
@api_login_required
@permission_required('production_record_delete')
def delete_production_record(record_id):
    """删除生产记录"""
    from app.models.production_record import ProductionRecord
    record = ProductionRecord.query.get_or_404(record_id)
    
    # 检查权限
    if not current_user.has_role('管理员'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if record.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限删除此记录'}), 403
    
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '生产记录删除成功'})

@api_bp.route('/production-records/<int:record_id>/status', methods=['PUT'])
@api_login_required
@permission_required('production_record_status_manage')
def update_production_record_status(record_id):
    """更新生产记录状态"""
    from app.models.production_record import ProductionRecord
    record = ProductionRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    # 检查权限
    if not current_user.has_role('管理员'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if record.factory_id not in factory_ids:
            return jsonify({'error': '您没有权限更新此记录状态'}), 403
    
    # 更新状态字段
    if 'status' in data:
        record.status = data['status']
    
    if 'completed_by' in data:
        record.completed_by = data['completed_by']
    
    if 'completion_date' in data:
        try:
            record.completion_date = datetime.strptime(data['completion_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '完成日期格式不正确，应为YYYY-MM-DD'}), 400
    
    db.session.commit()
    
    return jsonify({
        'id': record.id,
        'status': record.status,
        'completed_by': record.completed_by,
        'completion_date': record.completion_date.isoformat() if record.completion_date else None,
        'updated_at': record.updated_at.isoformat() if record.updated_at else None
    })
