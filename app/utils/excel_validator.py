"""
Excel数据验证器
提供Excel导入数据的验证功能
"""
import pandas as pd
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelValidator:
    """Excel数据验证器"""
    
    def __init__(self):
        """初始化验证器"""
        pass
    
    def validate_required_fields(self, df, required_fields):
        """
        验证必需字段
        
        :param df: DataFrame数据
        :param required_fields: 必需字段列表
        :return: 验证结果
        """
        missing_fields = []
        for field in required_fields:
            if field not in df.columns:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'valid': False,
                'error': f"缺少必需字段: {', '.join(missing_fields)}"
            }
        
        # 检查必需字段是否有空值
        for field in required_fields:
            if df[field].isnull().any():
                return {
                    'valid': False,
                    'error': f"字段 '{field}' 包含空值"
                }
        
        return {'valid': True}
    
    def validate_data_types(self, df, type_rules):
        """
        验证数据类型
        
        :param df: DataFrame数据
        :param type_rules: 类型规则字典 {字段名: 数据类型}
        :return: 验证结果
        """
        errors = []
        
        for field, expected_type in type_rules.items():
            if field in df.columns:
                try:
                    if expected_type == 'date':
                        pd.to_datetime(df[field], errors='raise')
                    elif expected_type == 'numeric':
                        pd.to_numeric(df[field], errors='raise')
                    elif expected_type == 'string':
                        df[field].astype(str)
                except Exception as e:
                    errors.append(f"字段 '{field}' 数据类型不正确: {str(e)}")
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        return {'valid': True}
    
    def validate_business_rules(self, df, rules):
        """
        验证业务规则
        
        :param df: DataFrame数据
        :param rules: 业务规则列表
        :return: 验证结果
        """
        errors = []
        
        for rule in rules:
            try:
                # 执行业务规则验证
                result = rule(df)
                if not result['valid']:
                    errors.append(result['error'])
            except Exception as e:
                errors.append(f"业务规则验证错误: {str(e)}")
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        return {'valid': True}
    
    def validate_assay_data(self, df):
        """
        验证化验数据
        
        :param df: DataFrame数据
        :return: 验证结果
        """
        # 必需字段验证
        required_fields = ['样品名称', '分厂', '水含量', '锌含量', '铅含量', '氯含量', '氟含量']
        result = self.validate_required_fields(df, required_fields)
        if not result['valid']:
            return result
        
        # 数据类型验证
        type_rules = {
            '水含量': 'numeric',
            '锌含量': 'numeric',
            '铅含量': 'numeric',
            '氯含量': 'numeric',
            '氟含量': 'numeric',
            '铁含量': 'numeric',
            '硅含量': 'numeric',
            '硫含量': 'numeric',
            '高热值': 'numeric',
            '低热值': 'numeric',
            '银含量': 'numeric',
            '回收率': 'numeric'
        }
        result = self.validate_data_types(df, type_rules)
        if not result['valid']:
            return result
        
        # 业务规则验证
        business_rules = [
            self._validate_non_negative_values
        ]
        result = self.validate_business_rules(df, business_rules)
        if not result['valid']:
            return result
        
        return {'valid': True}
    
    def _validate_non_negative_values(self, df):
        """验证数值字段不能为负数"""
        try:
            # 获取所有数值列
            numeric_columns = df.select_dtypes(include=['number']).columns
            
            # 检查是否有负数
            for col in numeric_columns:
                negative_values = df[df[col] < 0]
                if len(negative_values) > 0:
                    return {
                        'valid': False,
                        'error': f'字段 {col} 不能为负数'
                    }
            
            return {'valid': True}
        except Exception as e:
            return {
                'valid': False,
                'error': f'验证数值字段时出错: {str(e)}'
            }
    
    def validate_material_transaction_data(self, df):
        """
        验证物料进出厂数据
        
        :param df: DataFrame数据
        :return: 验证结果
        """
        # 必需字段验证
        required_fields = ['日期', '客户', '物料名称', '分厂', '类型', '发数', '到数']
        result = self.validate_required_fields(df, required_fields)
        if not result['valid']:
            return result
        
        # 数据类型验证
        type_rules = {
            '日期': 'date',
            '发数': 'numeric',
            '到数': 'numeric',
            '水含量': 'numeric',
            '锌含量': 'numeric',
            '铅含量': 'numeric',
            '氯含量': 'numeric',
            '氟含量': 'numeric'
        }
        result = self.validate_data_types(df, type_rules)
        if not result['valid']:
            return result
        
        # 业务规则验证
        business_rules = [
            self._validate_positive_quantities,
            self._validate_date_not_future,
            self._validate_element_content_range
        ]
        result = self.validate_business_rules(df, business_rules)
        if not result['valid']:
            return result
        
        return {'valid': True}
    
    def _validate_positive_quantities(self, df):
        """验证发数和到数必须大于0"""
        try:
            negative_shipped = df[df['发数'] <= 0]
            negative_received = df[df['到数'] <= 0]
            
            if len(negative_shipped) > 0 or len(negative_received) > 0:
                return {
                    'valid': False,
                    'error': '发数和到数必须大于0'
                }
            
            return {'valid': True}
        except Exception as e:
            return {
                'valid': False,
                'error': f'验证发数和到数时出错: {str(e)}'
            }
    
    def _validate_date_not_future(self, df):
        """验证日期不能晚于当前日期"""
        try:
            today = pd.Timestamp(datetime.now().date())
            future_dates = df[pd.to_datetime(df['日期']).dt.date > today.date()]
            
            if len(future_dates) > 0:
                return {
                    'valid': False,
                    'error': '日期不能晚于当前日期'
                }
            
            return {'valid': True}
        except Exception as e:
            return {
                'valid': False,
                'error': f'验证日期时出错: {str(e)}'
            }
    
    def _validate_element_content_range(self, df):
        """验证元素含量范围（0-100%）"""
        try:
            element_columns = ['水含量', '锌含量', '铅含量', '氯含量', '氟含量']
            
            for col in element_columns:
                if col in df.columns:
                    invalid_values = df[(df[col] < 0) | (df[col] > 100)]
                    if len(invalid_values) > 0:
                        return {
                            'valid': False,
                            'error': f'{col} 应在0-100范围内'
                        }
            
            return {'valid': True}
        except Exception as e:
            return {
                'valid': False,
                'error': f'验证元素含量时出错: {str(e)}'
            }

# 创建全局实例
excel_validator = ExcelValidator()