"""
Excel模板管理器
提供Excel导入模板的生成功能
"""
import pandas as pd
import os
from datetime import datetime
from flask import current_app
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelTemplateManager:
    """Excel模板管理器"""
    
    def __init__(self):
        """初始化模板管理器"""
        pass
    
    def generate_material_transaction_template(self):
        """
        生成物料进出厂记录导入模板
        
        :return: 模板文件路径
        """
        try:
            # 定义模板列
            columns = [
                '日期', '客户', '物料名称', '分厂', '合同编号', '类型', 
                '包装', '车号', '发数', '到数', '水含量', '锌含量', 
                '铅含量', '氯含量', '氟含量', '备注'
            ]
            
            # 示例数据
            sample_data = {
                '日期': '2023-01-01',
                '客户': '客户名称',
                '物料名称': '物料名称',
                '分厂': '一分厂',
                '合同编号': 'HT20230101',
                '类型': '进厂',
                '包装': '包装方式',
                '车号': '车牌号',
                '发数': 100.0,
                '到数': 98.5,
                '水含量': 5.2,
                '锌含量': 10.3,
                '铅含量': 2.1,
                '氯含量': 0.8,
                '氟含量': 0.1,
                '备注': '备注信息'
            }
            
            # 创建临时目录
            temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'temp'), 'excel')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(temp_dir, f"物料进出厂记录模板_{timestamp}.xlsx")
            
            # 创建DataFrame
            df = pd.DataFrame([sample_data], columns=columns)
            
            # 保存为Excel模板
            df.to_excel(file_path, index=False)
            
            logger.info(f"物料进出厂记录模板生成成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"生成物料进出厂记录模板时发生错误: {str(e)}")
            raise
    
    def generate_assay_data_template(self):
        """
        生成化验数据导入模板
        
        :return: 模板文件路径
        """
        try:
            # 定义模板列
            columns = [
                '样品名称', '分厂', '水含量', '锌含量', '铅含量', '氯含量', 
                '氟含量', '铁含量', '硅含量', '硫含量', '高热值', '低热值', 
                '银含量', '回收率', '备注'
            ]
            
            # 示例数据
            sample_data = {
                '样品名称': '样品名称',
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
                '备注': '备注信息'
            }
            
            # 创建临时目录
            temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'temp'), 'excel')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(temp_dir, f"化验数据模板_{timestamp}.xlsx")
            
            # 创建DataFrame
            df = pd.DataFrame([sample_data], columns=columns)
            
            # 保存为Excel模板
            df.to_excel(file_path, index=False)
            
            logger.info(f"化验数据模板生成成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"生成化验数据模板时发生错误: {str(e)}")
            raise

    def generate_production_record_template(self):
        """
        生成产能记录导入模板
        
        :return: 模板文件路径
        """
        try:
            # 定义模板列
            columns = [
                '日期', '分厂', '班组', '物料名称', '产量', '水含量', '锌含量', 
                '铅含量', '氯含量', '氟含量', '备注'
            ]
            
            # 示例数据
            sample_data = {
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
            
            # 创建临时目录
            temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'temp'), 'excel')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(temp_dir, f"产能记录模板_{timestamp}.xlsx")
            
            # 创建DataFrame
            df = pd.DataFrame([sample_data], columns=columns)
            
            # 保存为Excel模板
            df.to_excel(file_path, index=False)
            
            logger.info(f"产能记录模板生成成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"生成产能记录模板时发生错误: {str(e)}")
            raise

    def generate_custom_template(self, module_name, columns, sample_data=None):
        """
        生成自定义模块模板
        
        :param module_name: 模块名称
        :param columns: 列名列表
        :param sample_data: 示例数据（可选）
        :return: 模板文件路径
        """
        try:
            # 创建临时目录
            temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'temp'), 'excel')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(temp_dir, f"{module_name}_模板_{timestamp}.xlsx")
            
            # 创建DataFrame
            if sample_data:
                df = pd.DataFrame([sample_data], columns=columns)
            else:
                df = pd.DataFrame(columns=columns)
            
            # 保存为Excel模板
            df.to_excel(file_path, index=False)
            
            logger.info(f"自定义模板生成成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"生成自定义模板时发生错误: {str(e)}")
            raise

# 创建全局实例
template_manager = ExcelTemplateManager()
