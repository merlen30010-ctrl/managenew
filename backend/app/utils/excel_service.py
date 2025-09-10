"""
Excel导入导出服务模块
提供Excel文件的导入、导出和模板生成功能
"""
import pandas as pd
import os
from datetime import datetime
from flask import current_app
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelService:
    """Excel服务类"""
    
    def __init__(self):
        """初始化Excel服务"""
        pass
    
    def export_to_excel(self, data, filename, sheet_name='Sheet1'):
        """
        将数据导出为Excel文件
        
        :param data: 要导出的数据（列表或DataFrame）
        :param filename: 导出文件名
        :param sheet_name: 工作表名称
        :return: 文件路径
        """
        try:
            # 创建临时目录
            temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'temp'), 'excel')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(temp_dir, f"{filename}_{timestamp}.xlsx")
            
            # 转换数据为DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            # 导出到Excel
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
            
            logger.info(f"Excel文件导出成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出Excel文件时发生错误: {str(e)}")
            raise
    
    def import_from_excel(self, file_path, sheet_name=0):
        """
        从Excel文件导入数据
        
        :param file_path: Excel文件路径
        :param sheet_name: 工作表名称或索引
        :return: DataFrame对象
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 读取Excel文件
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            logger.info(f"Excel文件导入成功: {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"导入Excel文件时发生错误: {str(e)}")
            raise
    
    def generate_template(self, columns, filename, sample_data=None):
        """
        生成Excel导入模板
        
        :param columns: 列名列表
        :param filename: 模板文件名
        :param sample_data: 示例数据（可选）
        :return: 文件路径
        """
        try:
            # 创建临时目录
            temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'temp'), 'excel')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(temp_dir, f"{filename}_template_{timestamp}.xlsx")
            
            # 创建DataFrame
            if sample_data:
                df = pd.DataFrame([sample_data], columns=columns)
            else:
                df = pd.DataFrame(columns=columns)
            
            # 保存为Excel模板
            df.to_excel(file_path, index=False)
            
            logger.info(f"Excel模板生成成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"生成Excel模板时发生错误: {str(e)}")
            raise
    
    def validate_excel_data(self, df, required_columns=None):
        """
        验证Excel数据
        
        :param df: DataFrame数据
        :param required_columns: 必需的列名列表
        :return: 验证结果字典
        """
        try:
            result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查必需列
            if required_columns:
                missing_columns = set(required_columns) - set(df.columns)
                if missing_columns:
                    result['is_valid'] = False
                    result['errors'].append(f"缺少必需列: {', '.join(missing_columns)}")
            
            # 检查空数据
            if df.empty:
                result['warnings'].append("Excel文件中没有数据")
            
            # 检查重复行
            if df.duplicated().any():
                result['warnings'].append("发现重复行")
            
            logger.info("Excel数据验证完成")
            return result
            
        except Exception as e:
            logger.error(f"验证Excel数据时发生错误: {str(e)}")
            raise

# 创建全局实例
excel_service = ExcelService()