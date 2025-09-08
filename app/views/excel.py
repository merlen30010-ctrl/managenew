"""
Excel导入导出视图控制器
处理Excel相关的HTTP请求
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app.utils.excel_service import excel_service
from app.utils.excel_validator import excel_validator
from app.utils.excel_template_manager import template_manager
from app.utils.excel_error_manager import error_manager
from app.models.material_transaction import MaterialTransaction
from app.models.customer import Customer
from app.models.material import Material
from app.models.department import Department
from app.models.contract import Contract
from app.models.production_record import ProductionRecord
from app import db
import os
import logging
import pandas as pd
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

excel_bp = Blueprint('excel', __name__, url_prefix='/excel')

@excel_bp.route('/template/<module_name>')
@login_required
def download_template(module_name):
    """
    下载指定模块的Excel导入模板
    
    :param module_name: 模块名称
    """
    try:
        # 根据模块名称生成相应模板
        if module_name == 'material_transaction':
            file_path = template_manager.generate_material_transaction_template()
        elif module_name == 'assay_data':
            file_path = template_manager.generate_assay_data_template()
        elif module_name == 'production_record':
            file_path = template_manager.generate_custom_template(
                '产能记录',
                ['日期', '分厂', '班组', '物料名称', '产量', '水含量', '锌含量', '铅含量', '氯含量', '氟含量', '备注'],
                {
                    '日期': '2023-01-01',
                    '分厂': '一分厂',
                    '班组': '一班',
                    '物料名称': '产品A',
                    '产量': 1000.0,
                    '水含量': 5.2,
                    '锌含量': 10.3,
                    '铅含量': 2.1,
                    '氯含量': 0.8,
                    '氟含量': 0.1,
                    '备注': '正常'
                }
            )
        else:
            return jsonify({'error': f'不支持的模块: {module_name}'}), 400
        
        # 返回文件下载
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"下载模板时发生错误: {str(e)}")
        return jsonify({'error': f'下载模板时发生错误: {str(e)}'}), 500

@excel_bp.route('/import/<module_name>', methods=['POST'])
@login_required
def import_excel_data(module_name):
    """
    导入Excel数据
    
    :param module_name: 模块名称
    """
    try:
        # 检查是否有上传文件
        if 'file' not in request.files:
            return jsonify({'error': '请选择要上传的文件'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': '请选择要上传的文件'}), 400
        
        # 保存上传文件
        temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'temp'), 'excel', 'uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # 读取Excel文件
        df = excel_service.import_from_excel(file_path)
        
        # 根据模块名称进行数据验证和处理
        if module_name == 'material_transaction':
            # 验证物料进出厂数据
            validation_result = excel_validator.validate_material_transaction_data(df)
            if not validation_result['valid']:
                # 生成错误报告
                error_file = error_manager.generate_error_report(
                    [{'type': '验证错误', 'message': validation_result['error']}], 
                    '物料进出厂数据导入'
                )
                return jsonify({
                    'error': '数据验证失败', 
                    'error_report': error_file
                }), 400
            
            # 导入数据到数据库
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # 处理日期
                    date_obj = pd.to_datetime(row['日期']).date()
                    
                    # 创建物料进出厂记录
                    transaction = MaterialTransaction(
                        date=date_obj,
                        customer=row['客户'],
                        material_name=row['物料名称'],
                        factory_id=Department.query.filter_by(name=row['分厂']).first().id if Department.query.filter_by(name=row['分厂']).first() else None,
                        contract_number=row.get('合同编号', ''),
                        transaction_type=row['类型'],
                        packaging=row.get('包装', ''),
                        vehicle_number=row.get('车号', ''),
                        shipped_quantity=float(row['发数']),
                        received_quantity=float(row['到数']),
                        water_content=float(row['水含量']) if pd.notna(row.get('水含量')) else None,
                        zinc_content=float(row['锌含量']) if pd.notna(row.get('锌含量')) else None,
                        lead_content=float(row['铅含量']) if pd.notna(row.get('铅含量')) else None,
                        chlorine_content=float(row['氯含量']) if pd.notna(row.get('氯含量')) else None,
                        fluorine_content=float(row['氟含量']) if pd.notna(row.get('氟含量')) else None,
                        remarks=row.get('备注', '')
                    )
                    
                    db.session.add(transaction)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append({
                        'type': '导入错误',
                        'message': f'第{index+1}行导入失败: {str(e)}',
                        'row': index+1
                    })
            
            if errors:
                # 生成错误报告
                error_file = error_manager.generate_error_report(errors, '物料进出厂数据导入')
                db.session.rollback()
                return jsonify({
                    'error': f'部分数据导入失败，成功导入{success_count}条，失败{error_count}条',
                    'error_report': error_file
                }), 400
            else:
                db.session.commit()
            
        elif module_name == 'assay_data':
            # 验证化验数据
            validation_result = excel_validator.validate_assay_data(df)
            if not validation_result['valid']:
                # 生成错误报告
                error_file = error_manager.generate_error_report(
                    [{'type': '验证错误', 'message': validation_result['error']}], 
                    '化验数据导入'
                )
                return jsonify({
                    'error': '数据验证失败', 
                    'error_report': error_file
                }), 400
            
            # TODO: 实际的数据导入逻辑需要根据具体的数据模型实现
            # 这里只是示例，实际需要根据业务逻辑处理数据
        elif module_name == 'production_record':
            # 验证产能记录数据
            required_columns = ['日期', '分厂', '物料名称', '产量']
            validation_result = excel_service.validate_excel_data(df, required_columns)
            if not validation_result['is_valid']:
                # 生成错误报告
                error_file = error_manager.generate_error_report(
                    [{'type': '验证错误', 'message': '; '.join(validation_result['errors'])}], 
                    '产能记录数据导入'
                )
                return jsonify({
                    'error': '数据验证失败', 
                    'error_report': error_file
                }), 400
            
            # 导入数据到数据库
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # 处理日期
                    date_obj = pd.to_datetime(row['日期']).date()
                    
                    # 获取分厂ID
                    factory = Department.query.filter_by(name=row['分厂'], level=1).first()
                    if not factory:
                        raise ValueError(f"分厂不存在: {row['分厂']}")
                    
                    # 获取班组ID（如果提供）
                    team_id = None
                    if pd.notna(row.get('班组')):
                        team = Department.query.filter_by(name=row['班组'], level=2).first()
                        if team:
                            team_id = team.id
                    
                    # 获取物料ID
                    material = Material.query.filter_by(name=row['物料名称'], purpose='产品').first()
                    if not material:
                        raise ValueError(f"物料不存在: {row['物料名称']}")
                    
                    # 创建产能记录
                    record = ProductionRecord(
                        date=date_obj,
                        factory_id=factory.id,
                        team_id=team_id,
                        recorder_id=current_user.id,
                        material_name=row['物料名称'],
                        quantity=float(row['产量']),
                        water_content=float(row['水含量']) if pd.notna(row.get('水含量')) else None,
                        zinc_content=float(row['锌含量']) if pd.notna(row.get('锌含量')) else None,
                        lead_content=float(row['铅含量']) if pd.notna(row.get('铅含量')) else None,
                        chlorine_content=float(row['氯含量']) if pd.notna(row.get('氯含量')) else None,
                        fluorine_content=float(row['氟含量']) if pd.notna(row.get('氟含量')) else None,
                        remarks=row.get('备注', ''),
                        created_by=current_user.id
                    )
                    
                    db.session.add(record)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append({
                        'type': '导入错误',
                        'message': f'第{index+1}行导入失败: {str(e)}',
                        'row': index+1
                    })
            
            if errors:
                # 生成错误报告
                error_file = error_manager.generate_error_report(errors, '产能记录数据导入')
                db.session.rollback()
                return jsonify({
                    'error': f'部分数据导入失败，成功导入{success_count}条，失败{error_count}条',
                    'error_report': error_file
                }), 400
            else:
                db.session.commit()
        else:
            return jsonify({'error': f'不支持的模块: {module_name}'}), 400
        
        # 清理临时文件
        os.remove(file_path)
        
        return jsonify({
            'message': '数据导入成功',
            'imported_rows': len(df)
        }), 200
        
    except Exception as e:
        logger.error(f"导入Excel数据时发生错误: {str(e)}")
        return jsonify({'error': f'导入Excel数据时发生错误: {str(e)}'}), 500

@excel_bp.route('/export/<module_name>')
@login_required
def export_excel_data(module_name):
    """
    导出Excel数据
    
    :param module_name: 模块名称
    """
    try:
        # 根据模块名称查询相应数据
        if module_name == 'material_transaction':
            # 查询物料进出厂记录
            query = MaterialTransaction.query
            
            # 根据用户权限筛选数据
            if not current_user.has_role('管理员'):
                user_departments = current_user.managed_departments
                factory_ids = [dept.id for dept in user_departments if dept.level == 1]
                query = query.filter(MaterialTransaction.factory_id.in_(factory_ids))
            
            transactions = query.all()
            
            # 转换为导出格式
            export_data = []
            for transaction in transactions:
                export_data.append({
                    '日期': transaction.date.strftime('%Y-%m-%d') if transaction.date else '',
                    '客户': transaction.customer,
                    '物料名称': transaction.material_name,
                    '分厂': transaction.factory.name if transaction.factory else '',
                    '合同编号': transaction.contract_number,
                    '类型': transaction.transaction_type,
                    '包装': transaction.packaging,
                    '车号': transaction.vehicle_number,
                    '发数': transaction.shipped_quantity,
                    '到数': transaction.received_quantity,
                    '水含量': transaction.water_content,
                    '锌含量': transaction.zinc_content,
                    '铅含量': transaction.lead_content,
                    '氯含量': transaction.chlorine_content,
                    '氟含量': transaction.fluorine_content,
                    '备注': transaction.remarks
                })
        elif module_name == 'assay_data':
            # TODO: 根据模块名称查询相应数据
            # 这里只是示例数据
            export_data = [
                {
                    '样品名称': '样品1',
                    '分厂': '一分厂',
                    '水含量': 10.5,
                    '锌含量': 20.3,
                    '铅含量': 5.2,
                    '氯含量': 1.8,
                    '氟含量': 0.5,
                    '铁含量': 3.7,
                    '硅含量': 2.1,
                    '硫含量': 1.2,
                    '高热值': 4500,
                    '低热值': 3200,
                    '银含量': 0.01,
                    '回收率': 95.5,
                    '备注': '正常'
                }
            ]
        elif module_name == 'production_record':
            # 查询产能记录
            query = ProductionRecord.query
            
            # 根据用户权限筛选数据
            if not current_user.has_role('管理员'):
                user_departments = current_user.managed_departments
                factory_ids = [dept.id for dept in user_departments if dept.level == 1]
                query = query.filter(ProductionRecord.factory_id.in_(factory_ids))
            
            records = query.all()
            
            # 转换为导出格式
            export_data = []
            for record in records:
                export_data.append({
                    '日期': record.date.strftime('%Y-%m-%d') if record.date else '',
                    '分厂': record.factory.name if record.factory else '',
                    '班组': record.team.name if record.team else '',
                    '物料名称': record.material_name,
                    '产量': record.quantity,
                    '水含量': record.water_content,
                    '锌含量': record.zinc_content,
                    '铅含量': record.lead_content,
                    '氯含量': record.chlorine_content,
                    '氟含量': record.fluorine_content,
                    '备注': record.remarks
                })
        else:
            return jsonify({'error': f'不支持的模块: {module_name}'}), 400
        
        # 导出数据
        file_path = excel_service.export_to_excel(
            export_data, 
            f"{module_name}_导出数据"
        )
        
        # 返回文件下载
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"导出Excel数据时发生错误: {str(e)}")
        return jsonify({'error': f'导出Excel数据时发生错误: {str(e)}'}), 500