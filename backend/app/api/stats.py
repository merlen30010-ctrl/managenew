from flask import jsonify
from app.api import api_bp
from app.api.decorators import api_login_required
from app import db
from sqlalchemy import func

@api_bp.route('/stats/dashboard', methods=['GET'])
@api_login_required
def get_dashboard_stats():
    """获取首页统计数据"""
    try:
        # 导入模型
        from app.models.employee import Employee
        from app.models.contract import Contract
        
        # 统计员工数据
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(status='在职').count()
        
        # 统计合同数据
        total_contracts = Contract.query.count()
        pending_contracts = Contract.query.filter_by(status='待审核').count()
        
        # 返回统计数据
        stats = {
            'employeeCount': total_employees,
            'contractCount': total_contracts,
            'activeEmployees': active_employees,
            'pendingContracts': pending_contracts
        }
        
        return jsonify({
            'success': True,
            'message': '获取统计数据成功',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500