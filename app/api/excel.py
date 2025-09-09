"""
Excel API接口
提供Excel导入导出的RESTful API
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app.api.decorators import api_login_required, permission_required
from app.utils.excel_service import excel_service
from app.utils.excel_validator import excel_validator
from app.utils.excel_template_manager import template_manager
from app.utils.excel_error_manager import error_manager
from app.models.material_transaction import MaterialTransaction
from app.models.customer import Customer
from app.models.material import Material
from app.models.department import Department
from app.models.contract import Contract
from app import db
import os
import logging
import pandas as pd
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

excel_api_bp = Blueprint('excel_api', __name__, url_prefix='/excel')

@excel_api_bp.route('/template/<module_name>')
@api_login_required
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
        else:
            return jsonify({'error': f'不支持的模块: {module_name}'}), 400
        
        # 返回文件下载
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"下载模板时发生错误: {str(e)}")
        return jsonify({'error': f'下载模板时发生错误: {str(e)}'}), 500

@excel_api_bp.route('/import/<module_name>', methods=['POST'])
@api_login_required
@permission_required('excel_import')
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

@excel_api_bp.route('/export/<module_name>')
@api_login_required
@permission_required('excel_export')
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
            if not current_user.has_permission_name('assay_data_create_all'):
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