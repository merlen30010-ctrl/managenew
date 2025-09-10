from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.metal_price import MetalPrice
from app.utils.cache_service import cache_service, CACHE_TIMEOUT
from datetime import datetime
import pandas as pd
import os
from io import BytesIO

api_metal_price_bp = Blueprint('api_metal_price', __name__, url_prefix='/api/metal-prices')

@cache_service.cache_query_result('latest_metal_prices', CACHE_TIMEOUT['MEDIUM'])
def get_latest_metal_prices_cached(metal_type=None, limit=10):
    """获取最新金属价格（带缓存）"""
    query = MetalPrice.query
    if metal_type:
        query = query.filter(MetalPrice.metal_type == metal_type)
    
    prices = query.order_by(MetalPrice.quote_date.desc()).limit(limit).all()
    return [price.to_dict() for price in prices]

@api_metal_price_bp.route('/', methods=['GET'])
@login_required
@cache_service.cache_query_result('metal_prices_list', CACHE_TIMEOUT['MEDIUM'])
def get_metal_prices():
    """获取金属价格列表"""
    # 获取筛选参数
    metal_type = request.args.get('metal_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = MetalPrice.query
    
    if metal_type:
        query = query.filter(MetalPrice.metal_type == metal_type)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(MetalPrice.quote_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(MetalPrice.quote_date <= end_date_obj)
        except ValueError:
            pass
    
    # 分页
    paginated = query.order_by(MetalPrice.quote_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 转换为字典列表
    prices = [price.to_dict() for price in paginated.items]
    
    result = {
        'prices': prices,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }
    
    return result

@api_metal_price_bp.route('/<int:price_id>', methods=['GET'])
@login_required
def get_metal_price(price_id):
    """获取单个金属价格记录"""
    metal_price = MetalPrice.query.get_or_404(price_id)
    return jsonify(metal_price.to_dict())

@api_metal_price_bp.route('/', methods=['POST'])
@login_required
def create_metal_price():
    """创建金属价格记录"""
    data = request.get_json()
    
    # 检查必填字段
    required_fields = ['quote_date', 'average_price', 'price_change']
    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({'error': f'{field} 是必填字段'}), 400
    
    # 处理日期
    try:
        quote_date = datetime.strptime(data['quote_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式不正确'}), 400
    
    # 处理数值
    try:
        average_price = float(data['average_price'])
        price_change = float(data['price_change'])
        
        # 处理可选字段
        high_price = float(data['high_price']) if 'high_price' in data and data['high_price'] is not None else average_price
        low_price = float(data['low_price']) if 'low_price' in data and data['low_price'] is not None else average_price
        
        # 验证逻辑：最高价应大于等于最低价
        if high_price < low_price:
            return jsonify({'error': '最高价不能低于最低价'}), 400
            
        # 验证逻辑：均价应在最高价和最低价之间
        if 'high_price' in data and data['high_price'] is not None and average_price > high_price:
            return jsonify({'error': '均价不能高于最高价'}), 400
            
        if 'low_price' in data and data['low_price'] is not None and average_price < low_price:
            return jsonify({'error': '均价不能低于最低价'}), 400
    except ValueError:
        return jsonify({'error': '价格字段必须是有效的数字'}), 400
    
    # 创建记录
    metal_price = MetalPrice(
        metal_type=data.get('metal_type', '1#锌'),
        quote_date=quote_date,
        high_price=high_price,
        low_price=low_price,
        average_price=average_price,
        price_change=price_change
    )
    
    db.session.add(metal_price)
    db.session.commit()
    
    return jsonify(metal_price.to_dict()), 201

@api_metal_price_bp.route('/<int:price_id>', methods=['PUT'])
@login_required
def update_metal_price(price_id):
    """更新金属价格记录"""
    metal_price = MetalPrice.query.get_or_404(price_id)
    data = request.get_json()
    
    # 处理可选更新字段
    if 'metal_type' in data:
        metal_price.metal_type = data['metal_type']
    
    if 'quote_date' in data:
        try:
            metal_price.quote_date = datetime.strptime(data['quote_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式不正确'}), 400
    
    if 'average_price' in data:
        try:
            average_price = float(data['average_price'])
            
            # 如果更新了均价，但没有更新最高价或最低价，则相应更新它们
            if 'high_price' not in data and metal_price.high_price == metal_price.average_price:
                metal_price.high_price = average_price
            if 'low_price' not in data and metal_price.low_price == metal_price.average_price:
                metal_price.low_price = average_price
                
            metal_price.average_price = average_price
        except ValueError:
            return jsonify({'error': '均价必须是有效的数字'}), 400
    
    if 'price_change' in data:
        try:
            metal_price.price_change = float(data['price_change'])
        except ValueError:
            return jsonify({'error': '涨跌必须是有效的数字'}), 400
    
    if 'high_price' in data:
        try:
            high_price = float(data['high_price'])
            
            # 验证逻辑：最高价应大于等于最低价
            if high_price < metal_price.low_price:
                return jsonify({'error': '最高价不能低于最低价'}), 400
                
            # 验证逻辑：均价应在最高价和最低价之间
            if metal_price.average_price > high_price:
                return jsonify({'error': '均价不能高于最高价'}), 400
                
            metal_price.high_price = high_price
        except ValueError:
            return jsonify({'error': '最高价必须是有效的数字'}), 400
    
    if 'low_price' in data:
        try:
            low_price = float(data['low_price'])
            
            # 验证逻辑：最高价应大于等于最低价
            if metal_price.high_price < low_price:
                return jsonify({'error': '最高价不能低于最低价'}), 400
                
            # 验证逻辑：均价应在最高价和最低价之间
            if metal_price.average_price < low_price:
                return jsonify({'error': '均价不能低于最低价'}), 400
                
            metal_price.low_price = low_price
        except ValueError:
            return jsonify({'error': '最低价必须是有效的数字'}), 400
    
    db.session.commit()
    
    return jsonify(metal_price.to_dict())

@api_metal_price_bp.route('/<int:price_id>', methods=['DELETE'])
@login_required
def delete_metal_price(price_id):
    """删除金属价格记录"""
    metal_price = MetalPrice.query.get_or_404(price_id)
    
    db.session.delete(metal_price)
    db.session.commit()
    
    return jsonify({'message': '删除成功'})

@api_metal_price_bp.route('/export', methods=['GET'])
@login_required
def export_metal_prices():
    """导出金属价格为Excel"""
    # 获取筛选参数
    metal_type = request.args.get('metal_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # 构建查询
    query = MetalPrice.query
    
    if metal_type:
        query = query.filter(MetalPrice.metal_type == metal_type)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(MetalPrice.quote_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(MetalPrice.quote_date <= end_date_obj)
        except ValueError:
            pass
    
    # 获取数据
    prices = query.order_by(MetalPrice.quote_date.desc()).all()
    
    # 转换为DataFrame
    data = []
    for price in prices:
        data.append({
            '金属种类': price.metal_type,
            '报价日期': price.quote_date.strftime('%Y-%m-%d') if price.quote_date else '',
            '最高价': price.high_price,
            '最低价': price.low_price,
            '均价': price.average_price,
            '涨跌': price.price_change
        })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='金属价格')
    
    output.seek(0)
    
    # 返回Excel文件
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=metal_prices.xlsx'}
    )

@api_metal_price_bp.route('/import', methods=['POST'])
@login_required
def import_metal_prices():
    """从Excel导入金属价格"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({'error': '只支持Excel文件(.xls, .xlsx)'}), 400
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 检查必需字段
        required_columns = ['金属种类', '报价日期', '均价', '涨跌']
        for col in required_columns:
            if col not in df.columns:
                return jsonify({'error': f'缺少必需列: {col}'}), 400
        
        # 处理数据
        created_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查必填字段
                if pd.isna(row['报价日期']) or pd.isna(row['均价']) or pd.isna(row['涨跌']):
                    errors.append(f'第{index+1}行: 必填字段不能为空')
                    continue
                
                # 处理日期
                if isinstance(row['报价日期'], str):
                    quote_date = datetime.strptime(row['报价日期'], '%Y-%m-%d').date()
                else:
                    quote_date = row['报价日期'].date()
                
                # 处理数值
                average_price = float(row['均价'])
                price_change = float(row['涨跌'])
                
                # 处理可选字段
                high_price = float(row['最高价']) if '最高价' in df.columns and not pd.isna(row['最高价']) else average_price
                low_price = float(row['最低价']) if '最低价' in df.columns and not pd.isna(row['最低价']) else average_price
                
                # 验证逻辑：最高价应大于等于最低价
                if high_price < low_price:
                    errors.append(f'第{index+1}行: 最高价不能低于最低价')
                    continue
                    
                # 验证逻辑：均价应在最高价和最低价之间
                if '最高价' in df.columns and not pd.isna(row['最高价']) and average_price > high_price:
                    errors.append(f'第{index+1}行: 均价不能高于最高价')
                    continue
                    
                if '最低价' in df.columns and not pd.isna(row['最低价']) and average_price < low_price:
                    errors.append(f'第{index+1}行: 均价不能低于最低价')
                    continue
                
                # 创建记录
                metal_price = MetalPrice(
                    metal_type=row['金属种类'] if not pd.isna(row['金属种类']) else '1#锌',
                    quote_date=quote_date,
                    high_price=high_price,
                    low_price=low_price,
                    average_price=average_price,
                    price_change=price_change
                )
                
                db.session.add(metal_price)
                created_count += 1
            except Exception as e:
                errors.append(f'第{index+1}行: {str(e)}')
        
        if errors:
            db.session.rollback()
            return jsonify({'error': '导入过程中出现错误', 'details': errors}), 400
        
        db.session.commit()
        return jsonify({'message': f'成功导入{created_count}条记录'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

@api_metal_price_bp.route('/template', methods=['GET'])
@login_required
def download_template():
    """下载Excel模板"""
    # 创建模板数据
    data = [{
        '金属种类': '1#锌',
        '报价日期': '2023-01-01',
        '最高价': 25000,
        '最低价': 24000,
        '均价': 24500,
        '涨跌': 100
    }]
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='金属价格模板')
    
    output.seek(0)
    
    # 返回Excel文件
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=metal_price_template.xlsx'}
    )