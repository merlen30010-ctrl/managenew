from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.vehicle import Vehicle, VehicleUsageRecord, MaintenanceRecord, InsuranceRecord
from app.models.attachment import Attachment
from app.views.decorators import permission_required
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
vehicle_bp = Blueprint('vehicle', __name__, url_prefix='/vehicles')

@vehicle_bp.route('/')
@login_required
@permission_required('vehicle_read')
def list_vehicles():
    """车辆列表页面"""
    vehicles = Vehicle.query.all()
    return render_template('vehicle/list.html', vehicles=vehicles)

@vehicle_bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_create')
def create_vehicle():
    """创建车辆页面"""
    if request.method == 'POST':
        try:
            # 获取表单数据
            plate_number = request.form.get('license_plate')
            brand = request.form.get('brand')
            model = request.form.get('model')
            color = request.form.get('color')
            purchase_date_str = request.form.get('purchase_date')
            status = request.form.get('status', '可用')
            
            # 检查必填字段
            if not plate_number:
                flash('车牌号是必填字段', 'error')
                return render_template('vehicle/create.html')
            
            # 检查车牌号是否已存在
            if Vehicle.query.filter_by(plate_number=plate_number).first():
                flash('车牌号已存在', 'error')
                return render_template('vehicle/create.html')
            
            # 处理日期
            purchase_date = None
            if purchase_date_str:
                try:
                    purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('购买日期格式不正确', 'error')
                    return render_template('vehicle/create.html')
            
            # 创建新车辆
            vehicle = Vehicle(
                plate_number=plate_number,
                brand=brand,
                model=model,
                color=color,
                purchase_date=purchase_date,
                status=status
            )
            
            db.session.add(vehicle)
            db.session.commit()
            
            flash('车辆创建成功', 'success')
            return redirect(url_for('vehicle.list_vehicles'))
            
        except Exception as e:
            logger.error(f"创建车辆时发生错误: {str(e)}")
            flash(f'创建车辆时发生错误: {str(e)}', 'error')
            return render_template('vehicle/create.html')
    
    return render_template('vehicle/create.html')

@vehicle_bp.route('/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_update')
def edit_vehicle(vehicle_id):
    """编辑车辆页面"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            plate_number = request.form.get('license_plate')
            brand = request.form.get('brand')
            model = request.form.get('model')
            color = request.form.get('color')
            purchase_date_str = request.form.get('purchase_date')
            status = request.form.get('status')
            
            # 检查必填字段
            if not plate_number:
                flash('车牌号是必填字段', 'error')
                return render_template('vehicle/edit.html', vehicle=vehicle)
            
            # 检查车牌号是否已存在
            existing_vehicle = Vehicle.query.filter_by(plate_number=plate_number).first()
            if existing_vehicle and existing_vehicle.id != vehicle_id:
                flash('车牌号已存在', 'error')
                return render_template('vehicle/edit.html', vehicle=vehicle)
            
            # 处理日期
            purchase_date = None
            if purchase_date_str:
                try:
                    purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('购买日期格式不正确', 'error')
                    return render_template('vehicle/edit.html', vehicle=vehicle)
            
            # 更新车辆信息
            vehicle.plate_number = plate_number
            vehicle.brand = brand
            vehicle.model = model
            vehicle.color = color
            vehicle.purchase_date = purchase_date
            vehicle.status = status
            
            db.session.commit()
            
            flash('车辆信息更新成功', 'success')
            return redirect(url_for('vehicle.list_vehicles'))
            
        except Exception as e:
            logger.error(f"更新车辆信息时发生错误: {str(e)}")
            flash(f'更新车辆信息时发生错误: {str(e)}', 'error')
            return render_template('vehicle/edit.html', vehicle=vehicle)
    
    return render_template('vehicle/edit.html', vehicle=vehicle)

@vehicle_bp.route('/<int:vehicle_id>/delete', methods=['POST'])
@login_required
@permission_required('vehicle_delete')
def delete_vehicle(vehicle_id):
    """删除车辆"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        db.session.delete(vehicle)
        db.session.commit()
        flash('车辆删除成功', 'success')
    except Exception as e:
        logger.error(f"删除车辆时发生错误: {str(e)}")
        flash(f'删除车辆时发生错误: {str(e)}', 'error')
    
    return redirect(url_for('vehicle.list_vehicles'))

@vehicle_bp.route('/usage')
@login_required
@permission_required('vehicle_usage_read')
def list_usage_records():
    """车辆借还记录列表页面"""
    records = VehicleUsageRecord.query.all()
    return render_template('vehicle/usage_list.html', records=records)

@vehicle_bp.route('/usage/borrow/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_usage_create')
def borrow_vehicle(vehicle_id):
    """借车登记页面"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            borrower = request.form.get('borrower')
            borrow_time_str = request.form.get('borrow_time')
            borrow_mileage = request.form.get('borrow_mileage')
            purpose = request.form.get('purpose')
            remarks = request.form.get('remarks')
            
            # 处理借车时间
            borrow_time = datetime.now()
            if borrow_time_str:
                try:
                    borrow_time = datetime.strptime(borrow_time_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('借车时间格式不正确', 'error')
                    return render_template('vehicle/borrow.html', vehicle=vehicle)
            
            # 处理里程数
            borrow_mileage_val = None
            if borrow_mileage:
                try:
                    borrow_mileage_val = float(borrow_mileage)
                except ValueError:
                    flash('里程数格式不正确', 'error')
                    return render_template('vehicle/borrow.html', vehicle=vehicle)
            
            # 处理照片上传
            borrow_photo_id = None
            if 'borrow_photo' in request.files:
                photo_file = request.files['borrow_photo']
                if photo_file and photo_file.filename:
                    from app.utils.file_handler import save_uploaded_file
                    try:
                        attachment = save_uploaded_file(photo_file, 'vehicle_photos')
                        if attachment:
                            borrow_photo_id = attachment.id
                    except Exception as e:
                        logger.error(f"照片上传失败: {str(e)}")
                        flash('照片上传失败，但借车记录已创建', 'warning')
            
            # 创建借车记录
            record = VehicleUsageRecord(
                vehicle_id=vehicle.id,
                borrower_id=current_user.id,
                borrow_time=borrow_time,
                borrow_mileage=borrow_mileage_val,
                borrow_photo_id=borrow_photo_id,
                purpose=purpose,
                remarks=remarks
            )
            
            db.session.add(record)
            db.session.flush()  # 获取记录ID
            
            # 更新车辆状态
            vehicle.status = '使用中'
            
            db.session.commit()
            
            flash('借车登记成功', 'success')
            return redirect(url_for('vehicle.list_usage_records'))
            
        except Exception as e:
            logger.error(f"借车登记时发生错误: {str(e)}")
            flash(f'借车登记时发生错误: {str(e)}', 'error')
            return render_template('vehicle/borrow.html', vehicle=vehicle, datetime=datetime)
    
    return render_template('vehicle/borrow.html', vehicle=vehicle, datetime=datetime)

@vehicle_bp.route('/usage/return/<int:record_id>', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_usage_create')
def return_vehicle(record_id):
    """还车登记页面"""
    borrow_record = VehicleUsageRecord.query.get_or_404(record_id)
    vehicle = borrow_record.vehicle
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            return_time_str = request.form.get('return_time')
            return_mileage = request.form.get('return_mileage')
            remarks = request.form.get('remarks')
            
            # 处理还车时间
            return_time = datetime.now()
            if return_time_str:
                try:
                    return_time = datetime.strptime(return_time_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('还车时间格式不正确', 'error')
                    return render_template('vehicle/return.html', borrow_record=borrow_record, vehicle=vehicle)
            
            # 处理里程数
            return_mileage_val = None
            if return_mileage:
                try:
                    return_mileage_val = float(return_mileage)
                except ValueError:
                    flash('里程数格式不正确', 'error')
                    return render_template('vehicle/return.html', borrow_record=borrow_record, vehicle=vehicle)
            
            # 处理照片上传
            return_photo_id = None
            if 'return_photo' in request.files:
                photo_file = request.files['return_photo']
                if photo_file and photo_file.filename:
                    from app.utils.file_handler import save_uploaded_file
                    try:
                        attachment = save_uploaded_file(photo_file, 'vehicle_photos')
                        if attachment:
                            return_photo_id = attachment.id
                    except Exception as e:
                        logger.error(f"照片上传失败: {str(e)}")
                        flash('照片上传失败，但还车记录已更新', 'warning')
            
            # 更新借车记录为还车状态
            borrow_record.return_time = return_time
            borrow_record.return_mileage = return_mileage_val
            borrow_record.return_photo_id = return_photo_id
            if remarks:
                borrow_record.remarks = (borrow_record.remarks or '') + '\n还车备注: ' + remarks
            
            # 更新车辆状态
            vehicle.status = '可用'
            
            db.session.commit()
            
            flash('还车登记成功', 'success')
            return redirect(url_for('vehicle.list_usage_records'))
            
        except Exception as e:
            logger.error(f"还车登记时发生错误: {str(e)}")
            flash(f'还车登记时发生错误: {str(e)}', 'error')
            return render_template('vehicle/return.html', borrow_record=borrow_record, vehicle=vehicle, datetime=datetime)
    
    return render_template('vehicle/return.html', borrow_record=borrow_record, vehicle=vehicle, datetime=datetime)

@vehicle_bp.route('/maintenance')
@login_required
@permission_required('vehicle_maintenance_read')
def list_maintenance_records():
    """保养记录列表页面"""
    records = MaintenanceRecord.query.all()
    return render_template('vehicle/maintenance_list.html', records=records)

@vehicle_bp.route('/maintenance/create/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_maintenance_create')
def create_maintenance_record(vehicle_id):
    """创建保养记录页面"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            maintenance_date_str = request.form.get('maintenance_date')
            maintenance_type = request.form.get('maintenance_type')
            cost_str = request.form.get('cost')
            service_provider = request.form.get('service_provider')
            next_maintenance_date_str = request.form.get('next_maintenance_date')
            remarks = request.form.get('remarks')
            
            # 检查必填字段
            if not maintenance_date_str:
                flash('保养日期是必填字段', 'error')
                return render_template('vehicle/maintenance_create.html', vehicle=vehicle)
            
            # 处理保养日期
            try:
                maintenance_date = datetime.strptime(maintenance_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('保养日期格式不正确', 'error')
                return render_template('vehicle/maintenance_create.html', vehicle=vehicle)
            
            # 处理费用
            cost = 0
            if cost_str:
                try:
                    cost = float(cost_str)
                except ValueError:
                    flash('费用格式不正确', 'error')
                    return render_template('vehicle/maintenance_create.html', vehicle=vehicle)
            
            # 处理下次保养日期
            next_maintenance_date = None
            if next_maintenance_date_str:
                try:
                    next_maintenance_date = datetime.strptime(next_maintenance_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('下次保养日期格式不正确', 'error')
                    return render_template('vehicle/maintenance_create.html', vehicle=vehicle)
            
            # 创建保养记录
            record = MaintenanceRecord(
                vehicle_id=vehicle.id,
                maintenance_date=maintenance_date,
                maintenance_type=maintenance_type,
                cost=cost,
                service_provider=service_provider,
                next_maintenance_date=next_maintenance_date,
                remarks=remarks
            )
            
            db.session.add(record)
            db.session.commit()
            
            flash('保养记录创建成功', 'success')
            return redirect(url_for('vehicle.list_maintenance_records'))
            
        except Exception as e:
            logger.error(f"创建保养记录时发生错误: {str(e)}")
            flash(f'创建保养记录时发生错误: {str(e)}', 'error')
            return render_template('vehicle/maintenance_create.html', vehicle=vehicle)
    
    return render_template('vehicle/maintenance_create.html', vehicle=vehicle)

@vehicle_bp.route('/maintenance/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_maintenance_update')
def edit_maintenance_record(record_id):
    """编辑保养记录页面"""
    record = MaintenanceRecord.query.get_or_404(record_id)
    vehicle = record.vehicle
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            maintenance_date_str = request.form.get('maintenance_date')
            maintenance_type = request.form.get('maintenance_type')
            cost_str = request.form.get('cost')
            service_provider = request.form.get('service_provider')
            next_maintenance_date_str = request.form.get('next_maintenance_date')
            remarks = request.form.get('remarks')
            
            # 处理保养日期
            if maintenance_date_str:
                try:
                    record.maintenance_date = datetime.strptime(maintenance_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('保养日期格式不正确', 'error')
                    return render_template('vehicle/maintenance_edit.html', record=record, vehicle=vehicle)
            
            # 处理费用
            if cost_str:
                try:
                    record.cost = float(cost_str)
                except ValueError:
                    flash('费用格式不正确', 'error')
                    return render_template('vehicle/maintenance_edit.html', record=record, vehicle=vehicle)
            else:
                record.cost = 0
            
            # 处理下次保养日期
            if next_maintenance_date_str:
                try:
                    record.next_maintenance_date = datetime.strptime(next_maintenance_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('下次保养日期格式不正确', 'error')
                    return render_template('vehicle/maintenance_edit.html', record=record, vehicle=vehicle)
            else:
                record.next_maintenance_date = None
            
            # 更新保养记录信息
            record.maintenance_type = maintenance_type
            record.service_provider = service_provider
            record.remarks = remarks
            
            db.session.commit()
            
            flash('保养记录更新成功', 'success')
            return redirect(url_for('vehicle.list_maintenance_records'))
            
        except Exception as e:
            logger.error(f"更新保养记录时发生错误: {str(e)}")
            flash(f'更新保养记录时发生错误: {str(e)}', 'error')
            return render_template('vehicle/maintenance_edit.html', record=record, vehicle=vehicle)
    
    return render_template('vehicle/maintenance_edit.html', record=record, vehicle=vehicle)

@vehicle_bp.route('/maintenance/<int:record_id>/delete', methods=['POST'])
@login_required
@permission_required('vehicle_maintenance_delete')
def delete_maintenance_record(record_id):
    """删除保养记录"""
    try:
        record = MaintenanceRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        flash('保养记录删除成功', 'success')
    except Exception as e:
        logger.error(f"删除保养记录时发生错误: {str(e)}")
        flash(f'删除保养记录时发生错误: {str(e)}', 'error')
    
    return redirect(url_for('vehicle.list_maintenance_records'))

@vehicle_bp.route('/insurance')
@login_required
@permission_required('vehicle_insurance_read')
def list_insurance_records():
    """保险记录列表页面"""
    records = InsuranceRecord.query.all()
    return render_template('vehicle/insurance_list.html', records=records)

@vehicle_bp.route('/insurance/create/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_insurance_create')
def create_insurance_record(vehicle_id):
    """创建保险记录页面"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            insurance_company = request.form.get('insurance_company')
            policy_number = request.form.get('policy_number')
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            premium_str = request.form.get('premium')
            remarks = request.form.get('remarks')
            
            # 检查必填字段
            if not insurance_company or not start_date_str or not end_date_str:
                flash('保险公司、开始日期和结束日期是必填字段', 'error')
                return render_template('vehicle/insurance_create.html', vehicle=vehicle)
            
            # 处理开始日期
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('开始日期格式不正确', 'error')
                return render_template('vehicle/insurance_create.html', vehicle=vehicle)
            
            # 处理结束日期
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('结束日期格式不正确', 'error')
                return render_template('vehicle/insurance_create.html', vehicle=vehicle)
            
            # 处理保费
            premium = 0
            if premium_str:
                try:
                    premium = float(premium_str)
                except ValueError:
                    flash('保费格式不正确', 'error')
                    return render_template('vehicle/insurance_create.html', vehicle=vehicle)
            
            # 创建保险记录
            record = InsuranceRecord(
                vehicle_id=vehicle.id,
                insurance_company=insurance_company,
                policy_number=policy_number,
                start_date=start_date,
                end_date=end_date,
                premium=premium,
                remarks=remarks
            )
            
            db.session.add(record)
            db.session.commit()
            
            flash('保险记录创建成功', 'success')
            return redirect(url_for('vehicle.list_insurance_records'))
            
        except Exception as e:
            logger.error(f"创建保险记录时发生错误: {str(e)}")
            flash(f'创建保险记录时发生错误: {str(e)}', 'error')
            return render_template('vehicle/insurance_create.html', vehicle=vehicle)
    
    return render_template('vehicle/insurance_create.html', vehicle=vehicle)

@vehicle_bp.route('/insurance/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('vehicle_insurance_update')
def edit_insurance_record(record_id):
    """编辑保险记录页面"""
    record = InsuranceRecord.query.get_or_404(record_id)
    vehicle = record.vehicle
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            insurance_company = request.form.get('insurance_company')
            policy_number = request.form.get('policy_number')
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            premium_str = request.form.get('premium')
            remarks = request.form.get('remarks')
            
            # 处理开始日期
            if start_date_str:
                try:
                    record.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('开始日期格式不正确', 'error')
                    return render_template('vehicle/insurance_edit.html', record=record, vehicle=vehicle)
            
            # 处理结束日期
            if end_date_str:
                try:
                    record.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('结束日期格式不正确', 'error')
                    return render_template('vehicle/insurance_edit.html', record=record, vehicle=vehicle)
            
            # 处理保费
            if premium_str:
                try:
                    record.premium = float(premium_str)
                except ValueError:
                    flash('保费格式不正确', 'error')
                    return render_template('vehicle/insurance_edit.html', record=record, vehicle=vehicle)
            else:
                record.premium = 0
            
            # 更新保险记录信息
            record.insurance_company = insurance_company
            record.policy_number = policy_number
            record.remarks = remarks
            
            db.session.commit()
            
            flash('保险记录更新成功', 'success')
            return redirect(url_for('vehicle.list_insurance_records'))
            
        except Exception as e:
            logger.error(f"更新保险记录时发生错误: {str(e)}")
            flash(f'更新保险记录时发生错误: {str(e)}', 'error')
            return render_template('vehicle/insurance_edit.html', record=record, vehicle=vehicle)
    
    return render_template('vehicle/insurance_edit.html', record=record, vehicle=vehicle)

@vehicle_bp.route('/insurance/<int:record_id>/delete', methods=['POST'])
@login_required
@permission_required('vehicle_insurance_delete')
def delete_insurance_record(record_id):
    """删除保险记录"""
    try:
        record = InsuranceRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        flash('保险记录删除成功', 'success')
    except Exception as e:
        logger.error(f"删除保险记录时发生错误: {str(e)}")
        flash(f'删除保险记录时发生错误: {str(e)}', 'error')
    
    return redirect(url_for('vehicle.list_insurance_records'))