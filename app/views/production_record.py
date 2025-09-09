from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.production_record import ProductionRecord
from app.models.material import Material
from app.models.department import Department
from app.utils.pagination_service import pagination_service
from sqlalchemy.orm import joinedload
from datetime import datetime, date

production_record_bp = Blueprint('production_record', __name__)

@production_record_bp.route('/')
@login_required
def list_records():
    """产能记录列表"""
    # 获取筛选条件
    material_filter = request.args.get('material', '')
    factory_filter = request.args.get('factory', '')
    date_filter = request.args.get('date', '')
    
    # 构建查询 - 使用eager loading预加载关联对象
    query = ProductionRecord.query.options(
        joinedload(ProductionRecord.factory),
        joinedload(ProductionRecord.team),
        joinedload(ProductionRecord.recorder),
        joinedload(ProductionRecord.creator),
        joinedload(ProductionRecord.completer)
    )
    
    # 构建筛选条件
    filters = {}
    if material_filter:
        filters['material_name'] = material_filter
    if factory_filter:
        filters['factory_id'] = int(factory_filter)
    if date_filter:
        filters['date'] = datetime.strptime(date_filter, '%Y-%m-%d').date()
    
    # 应用筛选条件
    query = pagination_service.build_filter_query(query, ProductionRecord, filters)
    
    # 根据用户权限筛选数据
    if not current_user.has_permission('production_record_read_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        query = query.filter(ProductionRecord.factory_id.in_(factory_ids))
    
    # 使用分页服务
    pagination_result = pagination_service.paginate_query(
        query, 
        ProductionRecord,
        default_sort='date',
        allowed_sorts=['date', 'material_name', 'quantity', 'created_at']
    )
    
    records = pagination_result['items']
    
    # 获取筛选选项
    factories = Department.query.filter_by(level=1).all()
    
    return render_template('production_records/list.html', 
                         records=records,
                         factories=factories,
                         pagination=pagination_result,
                         material_filter=material_filter,
                         factory_filter=factory_filter,
                         date_filter=date_filter)

@production_record_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_record():
    """创建产能记录"""
    if request.method == 'POST':
        # 获取表单数据
        date_str = request.form.get('date')
        factory_id = request.form.get('factory_id')
        team_id = request.form.get('team_id')
        material_id = request.form.get('material_id')
        quantity = request.form.get('quantity')
        water_content = request.form.get('water_content')
        zinc_content = request.form.get('zinc_content')
        lead_content = request.form.get('lead_content')
        chlorine_content = request.form.get('chlorine_content')
        fluorine_content = request.form.get('fluorine_content')
        remarks = request.form.get('remarks')
        
        # 检查必填字段
        if not date_str or not factory_id or not material_id or not quantity:
            flash('请填写所有必填字段')
            return redirect(url_for('production_record.create_record'))
        
        # 检查权限
        if not current_user.has_permission('production_record_create_all'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if int(factory_id) not in factory_ids:
                flash('您没有权限在此分厂创建记录')
                return redirect(url_for('production_record.create_record'))
        
        # 处理日期
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式不正确')
            return redirect(url_for('production_record.create_record'))
        
        # 创建记录
        record = ProductionRecord(
            date=date_obj,
            factory_id=int(factory_id),
            team_id=int(team_id) if team_id else None,
            recorder_id=current_user.id,
            material_name=Material.query.get(material_id).name if material_id else '',
            quantity=float(quantity) if quantity else 0,
            water_content=float(water_content) if water_content else None,
            zinc_content=float(zinc_content) if zinc_content else None,
            lead_content=float(lead_content) if lead_content else None,
            chlorine_content=float(chlorine_content) if chlorine_content else None,
            fluorine_content=float(fluorine_content) if fluorine_content else None,
            remarks=remarks,
            created_by=current_user.id  # 记录创建人
        )
        
        db.session.add(record)
        db.session.commit()
        
        flash('产能记录创建成功')
        return redirect(url_for('production_record.list_records'))
    
    # 获取下拉选项数据
    factories = Department.query.filter_by(level=1).all()
    materials = Material.query.filter_by(purpose='产品').all()  # 只获取产品类型的物料
    
    # 获取班组数据（二级部门）
    teams = Department.query.filter_by(level=2).all()
    
    # 获取今天的日期字符串
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('production_records/create.html',
                         factories=factories,
                         materials=materials,
                         teams=teams,
                         today=today)

@production_record_bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    """编辑产能记录"""
    record = ProductionRecord.query.get_or_404(record_id)
    
    # 检查权限
    if not current_user.has_permission('production_record_update_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if record.factory_id not in factory_ids:
            flash('您没有权限编辑此记录')
            return redirect(url_for('production_record.list_records'))
    
    if request.method == 'POST':
        # 获取表单数据
        date_str = request.form.get('date')
        factory_id = request.form.get('factory_id')
        team_id = request.form.get('team_id')
        material_id = request.form.get('material_id')
        quantity = request.form.get('quantity')
        water_content = request.form.get('water_content')
        zinc_content = request.form.get('zinc_content')
        lead_content = request.form.get('lead_content')
        chlorine_content = request.form.get('chlorine_content')
        fluorine_content = request.form.get('fluorine_content')
        remarks = request.form.get('remarks')
        
        # 检查必填字段
        if not date_str or not factory_id or not material_id or not quantity:
            flash('请填写所有必填字段')
            return redirect(url_for('production_record.edit_record', record_id=record_id))
        
        # 检查权限
        if not current_user.has_permission('production_record_update_all'):
            user_departments = current_user.managed_departments
            factory_ids = [dept.id for dept in user_departments if dept.level == 1]
            if int(factory_id) not in factory_ids:
                flash('您没有权限将记录转移到此分厂')
                return redirect(url_for('production_record.edit_record', record_id=record_id))
        
        # 处理日期
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式不正确')
            return redirect(url_for('production_record.edit_record', record_id=record_id))
        
        # 更新记录
        record.date = date_obj
        record.factory_id = int(factory_id)
        record.team_id = int(team_id) if team_id else None
        record.material_name = Material.query.get(material_id).name if material_id else ''
        record.quantity = float(quantity) if quantity else 0
        record.water_content = float(water_content) if water_content else None
        record.zinc_content = float(zinc_content) if zinc_content else None
        record.lead_content = float(lead_content) if lead_content else None
        record.chlorine_content = float(chlorine_content) if chlorine_content else None
        record.fluorine_content = float(fluorine_content) if fluorine_content else None
        record.remarks = remarks
        
        db.session.commit()
        
        flash('产能记录更新成功')
        return redirect(url_for('production_record.list_records'))
    
    # 获取下拉选项数据
    factories = Department.query.filter_by(level=1).all()
    materials = Material.query.filter_by(purpose='产品').all()  # 只获取产品类型的物料
    teams = Department.query.filter_by(level=2).all()
    
    return render_template('production_records/edit.html',
                         record=record,
                         factories=factories,
                         materials=materials,
                         teams=teams)

@production_record_bp.route('/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    """删除产能记录"""
    record = ProductionRecord.query.get_or_404(record_id)
    
    # 检查权限
    if not current_user.has_permission('production_record_delete_all'):
        user_departments = current_user.managed_departments
        factory_ids = [dept.id for dept in user_departments if dept.level == 1]
        if record.factory_id not in factory_ids:
            flash('您没有权限删除此记录')
            return redirect(url_for('production_record.list_records'))
    
    db.session.delete(record)
    db.session.commit()
    
    flash('产能记录删除成功')
    return redirect(url_for('production_record.list_records'))

@production_record_bp.route('/api/materials')
@login_required
def api_materials():
    """获取产品列表API"""
    materials = Material.query.filter_by(purpose='产品').all()
    return jsonify([{
        'id': material.id,
        'name': material.name
    } for material in materials])

@production_record_bp.route('/api/factories')
@login_required
def api_factories():
    """获取分厂列表API"""
    factories = Department.query.filter_by(level=1).all()
    return jsonify([{
        'id': factory.id,
        'name': factory.name
    } for factory in factories])

@production_record_bp.route('/api/teams')
@login_required
def api_teams():
    """获取班组列表API"""
    teams = Department.query.filter_by(level=2).all()
    return jsonify([{
        'id': team.id,
        'name': team.name
    } for team in teams])