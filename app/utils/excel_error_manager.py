"""
Excel错误管理器
处理Excel导入导出过程中的错误
"""
import pandas as pd
import os
from datetime import datetime
from flask import current_app
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelErrorManager:
    """Excel错误管理器"""
    
    def __init__(self):
        """初始化错误管理器"""
        pass
    
    def generate_error_report(self, errors, filename):
        """
        生成错误报告
        
        :param errors: 错误列表
        :param filename: 报告文件名
        :return: 报告文件路径
        """
        try:
            # 创建临时目录
            temp_dir = os.path.join(current_app.config.get('TEMP_FOLDER', 'excel'), 'errors')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(temp_dir, f"{filename}_错误报告_{timestamp}.xlsx")
            
            # 创建错误报告DataFrame
            error_data = []
            for i, error in enumerate(errors, 1):
                error_data.append({
                    '序号': i,
                    '错误类型': error.get('type', '未知'),
                    '错误信息': error.get('message', ''),
                    '行号': error.get('row', ''),
                    '列名': error.get('column', ''),
                    '值': error.get('value', '')
                })
            
            df = pd.DataFrame(error_data)
            
            # 保存为Excel文件
            df.to_excel(file_path, index=False)
            
            logger.info(f"错误报告生成成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"生成错误报告时发生错误: {str(e)}")
            raise
    
    def mark_error_rows(self, df, error_rows):
        """
        标记错误行
        
        :param df: 原始DataFrame
        :param error_rows: 错误行索引列表
        :return: 标记后的DataFrame
        """
        try:
            # 创建副本
            marked_df = df.copy()
            
            # 添加错误标记列
            marked_df['错误标记'] = ['错误' if i in error_rows else '' for i in range(len(marked_df))]
            
            return marked_df
            
        except Exception as e:
            logger.error(f"标记错误行时发生错误: {str(e)}")
            raise
    
    def log_import_result(self, total_rows, success_rows, error_rows, module_name):
        """
        记录导入结果
        
        :param total_rows: 总行数
        :param success_rows: 成功行数
        :param error_rows: 错误行数
        :param module_name: 模块名称
        """
        try:
            result = {
                '模块': module_name,
                '总行数': total_rows,
                '成功行数': success_rows,
                '错误行数': error_rows,
                '成功率': f"{(success_rows/total_rows)*100:.2f}%" if total_rows > 0 else "0%",
                '导入时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"Excel导入结果: {result}")
            
        except Exception as e:
            logger.error(f"记录导入结果时发生错误: {str(e)}")

# 创建全局实例
error_manager = ExcelErrorManager()