from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.material_transaction import MaterialTransaction
from app.models.customer import Customer
from app.models.material import Material
from app.models.department import Department
from app.models.contract import Contract
from app.utils.pagination_service import pagination_service
from sqlalchemy.orm import joinedload
from datetime import datetime

material_transaction_bp = Blueprint('material_transaction', __name__)

@material_transaction_bp.route('/')
@login_required
def list_transactions():
    """物料进出厂记录列表"""
    # 获取筛选条件
    customer_filter = request.args.get('customer', '')
    material_filter = request.args.get('material', '')
    factory_filter = request.args.get('factory', '')
    transaction_type_filter = request.args.get('transaction_type', '')
    
    # 构建查询 - 使用eager loading预加载关联对象
    query = MaterialTransaction.query.options(
        joinedload(MaterialTransaction.factory)
    )
    
    # 构建筛选条件
    filters = {}
    if customer_filter:
        filters['customer'] = customer_filter
    if material_filter:
        filters['material_name'] = material_filter
    if factory_filter:
        filters['factory_id'] = int(factory_filter)
    if transaction_type_filter:
        filters['transaction_type'] = transaction_type_filter
    
    # 应用筛选条件
    query = pagination_service.build_filter_query(query, MaterialTransaction, filters)
    
    # 根据用户权限筛选数据
    if not current_user.has_role('管理员'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        query = query.filter(MaterialTransaction.factory_id.in_(factory_ids))
    
    # 使用分页服务
    pagination_result = pagination_service.paginate_query(
        query,
        MaterialTransaction,
        default_sort='date',
        allowed_sorts=['date', 'customer', 'material_name', 'quantity', 'created_at']
    )
    
    transactions = pagination_result['items']
    
    # 获取筛选选项
    factories = Department.query.filter_by(level=1).all()
    
    return render_template('material_transactions/list.html',
                         transactions=transactions,
                         factories=factories,
                         pagination=pagination_result,
                         customer_filter=customer_filter,
                         material_filter=material_filter,
                         factory_filter=factory_filter,
                         transaction_type_filter=transaction_type_filter)

@material_transaction_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_transaction():
    """创建物料进出厂记录"""
    if request.method == 'POST':
        # 获取表单数据
        date_str = request.form.get('date')
        customer = request.form.get('customer')
        material_id = request.form.get('material_id')
        factory_id = request.form.get('factory_id')
        contract_id = request.form.get('contract_id')
        transaction_type = request.form.get('transaction_type')
        packaging = request.form.get('packaging')
        vehicle_number = request.form.get('vehicle_number')
        shipped_quantity = request.form.get('shipped_quantity')
        received_quantity = request.form.get('received_quantity')
        water_content = request.form.get('water_content')
        zinc_content = request.form.get('zinc_content')
        lead_content = request.form.get('lead_content')
        chlorine_content = request.form.get('chlorine_content')
        fluorine_content = request.form.get('fluorine_content')
        remarks = request.form.get('remarks')
        
        # 检查必填字段
        if not date_str or not customer or not material_id or not factory_id or not transaction_type or not shipped_quantity or not received_quantity:
            flash('请填写所有必填字段')
            return redirect(url_for('material_transaction.create_transaction'))
        
        # 检查权限
        if not current_user.has_role('管理员'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if int(factory_id) not in factory_ids:
                flash('您没有权限在此分厂创建记录')
                return redirect(url_for('material_transaction.create_transaction'))
        
        # 处理日期
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式不正确')
            return redirect(url_for('material_transaction.create_transaction'))
        
        # 创建记录
        transaction = MaterialTransaction(
            date=date_obj,
            customer=customer,
            material_name=Material.query.get(material_id).name if material_id else '',
            factory_id=int(factory_id),
            contract_number=Contract.query.get(contract_id).contract_number if contract_id else '',
            transaction_type=transaction_type,
            packaging=packaging,
            vehicle_number=vehicle_number,
            shipped_quantity=float(shipped_quantity) if shipped_quantity else 0,
            received_quantity=float(received_quantity) if received_quantity else 0,
            water_content=float(water_content) if water_content else None,
            zinc_content=float(zinc_content) if zinc_content else None,
            lead_content=float(lead_content) if lead_content else None,
            chlorine_content=float(chlorine_content) if chlorine_content else None,
            fluorine_content=float(fluorine_content) if fluorine_content else None,
            remarks=remarks,
            created_by=current_user.id  # 记录创建人
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('物料进出厂记录创建成功')
        return redirect(url_for('material_transaction.list_transactions'))
    
    # 获取下拉选项数据
    customers = Customer.query.all()
    materials = Material.query.all()
    factories = Department.query.filter_by(level=1).all()
    contracts = Contract.query.all()
    
    return render_template('material_transactions/create.html',
                         customers=customers,
                         materials=materials,
                         factories=factories,
                         contracts=contracts)

@material_transaction_bp.route('/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """编辑物料进出厂记录"""
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    
    # 检查权限
    if not current_user.has_role('管理员'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            flash('您没有权限编辑此记录')
            return redirect(url_for('material_transaction.list_transactions'))
    
    if request.method == 'POST':
        # 获取表单数据
        date_str = request.form.get('date')
        customer = request.form.get('customer')
        material_id = request.form.get('material_id')
        factory_id = request.form.get('factory_id')
        contract_id = request.form.get('contract_id')
        transaction_type = request.form.get('transaction_type')
        packaging = request.form.get('packaging')
        vehicle_number = request.form.get('vehicle_number')
        shipped_quantity = request.form.get('shipped_quantity')
        received_quantity = request.form.get('received_quantity')
        water_content = request.form.get('water_content')
        zinc_content = request.form.get('zinc_content')
        lead_content = request.form.get('lead_content')
        chlorine_content = request.form.get('chlorine_content')
        fluorine_content = request.form.get('fluorine_content')
        remarks = request.form.get('remarks')
        
        # 检查必填字段
        if not date_str or not customer or not material_id or not factory_id or not transaction_type or not shipped_quantity or not received_quantity:
            flash('请填写所有必填字段')
            return redirect(url_for('material_transaction.edit_transaction', transaction_id=transaction_id))
        
        # 检查权限
        if not current_user.has_role('管理员'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if int(factory_id) not in factory_ids:
                flash('您没有权限将记录转移到此分厂')
                return redirect(url_for('material_transaction.edit_transaction', transaction_id=transaction_id))
        
        # 处理日期
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式不正确')
            return redirect(url_for('material_transaction.edit_transaction', transaction_id=transaction_id))
        
        # 更新记录
        transaction.date = date_obj
        transaction.customer = customer
        transaction.material_name = Material.query.get(material_id).name if material_id else ''
        transaction.factory_id = int(factory_id)
        transaction.contract_number = Contract.query.get(contract_id).contract_number if contract_id else ''
        transaction.transaction_type = transaction_type
        transaction.packaging = packaging
        transaction.vehicle_number = vehicle_number
        transaction.shipped_quantity = float(shipped_quantity) if shipped_quantity else 0
        transaction.received_quantity = float(received_quantity) if received_quantity else 0
        transaction.water_content = float(water_content) if water_content else None
        transaction.zinc_content = float(zinc_content) if zinc_content else None
        transaction.lead_content = float(lead_content) if lead_content else None
        transaction.chlorine_content = float(chlorine_content) if chlorine_content else None
        transaction.fluorine_content = float(fluorine_content) if fluorine_content else None
        transaction.remarks = remarks
        
        db.session.commit()
        
        flash('物料进出厂记录更新成功')
        return redirect(url_for('material_transaction.list_transactions'))
    
    # 获取下拉选项数据
    customers = Customer.query.all()
    materials = Material.query.all()
    factories = Department.query.filter_by(level=1).all()
    contracts = Contract.query.all()
    
    return render_template('material_transactions/edit.html',
                         transaction=transaction,
                         customers=customers,
                         materials=materials,
                         factories=factories,
                         contracts=contracts)

@material_transaction_bp.route('/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """删除物料进出厂记录"""
    transaction = MaterialTransaction.query.get_or_404(transaction_id)
    
    # 检查权限
    if not current_user.has_role('管理员'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if transaction.factory_id not in factory_ids:
            flash('您没有权限删除此记录')
            return redirect(url_for('material_transaction.list_transactions'))
    
    db.session.delete(transaction)
    db.session.commit()
    
    flash('物料进出厂记录删除成功')
    return redirect(url_for('material_transaction.list_transactions'))

@material_transaction_bp.route('/api/customers')
@login_required
def api_customers():
    """获取客户列表API"""
    customers = Customer.query.all()
    return jsonify([{
        'id': customer.id,
        'name': customer.name
    } for customer in customers])

@material_transaction_bp.route('/api/materials')
@login_required
def api_materials():
    """获取物料列表API"""
    materials = Material.query.all()
    return jsonify([{
        'id': material.id,
        'name': material.name
    } for material in materials])

@material_transaction_bp.route('/api/factories')
@login_required
def api_factories():
    """获取分厂列表API"""
    factories = Department.query.filter_by(level=1).all()
    return jsonify([{
        'id': factory.id,
        'name': factory.name
    } for factory in factories])

@material_transaction_bp.route('/api/contracts')
@login_required
def api_contracts():
    """获取合同列表API"""
    contracts = Contract.query.all()
    return jsonify([{
        'id': contract.id,
        'contract_number': contract.contract_number
    } for contract in contracts])