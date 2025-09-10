from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.metal_price import MetalPrice
from datetime import datetime
import os

metal_price_bp = Blueprint('metal_price', __name__)

@metal_price_bp.route('/')
@login_required
def list_prices():
    """金属价格列表"""
    # 获取筛选条件
    metal_type_filter = request.args.get('metal_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # 构建查询
    query = MetalPrice.query
    
    if metal_type_filter:
        query = query.filter(MetalPrice.metal_type == metal_type_filter)
    
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
    
    # 按日期降序排列
    prices = query.order_by(MetalPrice.quote_date.desc()).all()
    
    # 获取所有金属种类用于筛选
    metal_types = db.session.query(MetalPrice.metal_type).distinct().all()
    metal_types = [mt[0] for mt in metal_types]
    
    return render_template('metal_prices/list.html', 
                         prices=prices,
                         metal_types=metal_types,
                         metal_type_filter=metal_type_filter,
                         start_date=start_date,
                         end_date=end_date)

@metal_price_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_price():
    """创建金属价格"""
    if request.method == 'POST':
        # 获取表单数据
        metal_type = request.form.get('metal_type', '1#锌')
        quote_date_str = request.form.get('quote_date')
        high_price_str = request.form.get('high_price')
        low_price_str = request.form.get('low_price')
        average_price_str = request.form.get('average_price')
        price_change_str = request.form.get('price_change')
        
        # 检查必填字段
        if not quote_date_str or not average_price_str or not price_change_str:
            flash('请填写所有必填字段')
            return redirect(url_for('metal_price.create_price'))
        
        # 处理日期
        try:
            quote_date = datetime.strptime(quote_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式不正确')
            return redirect(url_for('metal_price.create_price'))
        
        # 处理数值
        try:
            average_price = float(average_price_str)
            price_change = float(price_change_str)
            
            # 处理可选字段
            high_price = float(high_price_str) if high_price_str else average_price
            low_price = float(low_price_str) if low_price_str else average_price
            
            # 验证逻辑：最高价应大于等于最低价
            if high_price < low_price:
                flash('最高价不能低于最低价')
                return redirect(url_for('metal_price.create_price'))
                
            # 验证逻辑：均价应在最高价和最低价之间
            if high_price_str and average_price > high_price:
                flash('均价不能高于最高价')
                return redirect(url_for('metal_price.create_price'))
                
            if low_price_str and average_price < low_price:
                flash('均价不能低于最低价')
                return redirect(url_for('metal_price.create_price'))
        except ValueError:
            flash('价格字段必须是有效的数字')
            return redirect(url_for('metal_price.create_price'))
        
        # 创建记录
        metal_price = MetalPrice(
            metal_type=metal_type,
            quote_date=quote_date,
            high_price=high_price,
            low_price=low_price,
            average_price=average_price,
            price_change=price_change
        )
        
        db.session.add(metal_price)
        db.session.commit()
        
        flash('金属价格记录创建成功')
        return redirect(url_for('metal_price.list_prices'))
    
    return render_template('metal_prices/create.html')

@metal_price_bp.route('/<int:price_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_price(price_id):
    """编辑金属价格"""
    metal_price = MetalPrice.query.get_or_404(price_id)
    
    if request.method == 'POST':
        # 获取表单数据
        metal_type = request.form.get('metal_type', '1#锌')
        quote_date_str = request.form.get('quote_date')
        high_price_str = request.form.get('high_price')
        low_price_str = request.form.get('low_price')
        average_price_str = request.form.get('average_price')
        price_change_str = request.form.get('price_change')
        
        # 检查必填字段
        if not quote_date_str or not average_price_str or not price_change_str:
            flash('请填写所有必填字段')
            return redirect(url_for('metal_price.edit_price', price_id=price_id))
        
        # 处理日期
        try:
            quote_date = datetime.strptime(quote_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式不正确')
            return redirect(url_for('metal_price.edit_price', price_id=price_id))
        
        # 处理数值
        try:
            average_price = float(average_price_str)
            price_change = float(price_change_str)
            
            # 处理可选字段
            high_price = float(high_price_str) if high_price_str else average_price
            low_price = float(low_price_str) if low_price_str else average_price
            
            # 验证逻辑：最高价应大于等于最低价
            if high_price < low_price:
                flash('最高价不能低于最低价')
                return redirect(url_for('metal_price.edit_price', price_id=price_id))
                
            # 验证逻辑：均价应在最高价和最低价之间
            if high_price_str and average_price > high_price:
                flash('均价不能高于最高价')
                return redirect(url_for('metal_price.edit_price', price_id=price_id))
                
            if low_price_str and average_price < low_price:
                flash('均价不能低于最低价')
                return redirect(url_for('metal_price.edit_price', price_id=price_id))
        except ValueError:
            flash('价格字段必须是有效的数字')
            return redirect(url_for('metal_price.edit_price', price_id=price_id))
        
        # 更新记录
        metal_price.metal_type = metal_type
        metal_price.quote_date = quote_date
        metal_price.high_price = high_price
        metal_price.low_price = low_price
        metal_price.average_price = average_price
        metal_price.price_change = price_change
        
        db.session.commit()
        
        flash('金属价格记录更新成功')
        return redirect(url_for('metal_price.list_prices'))
    
    return render_template('metal_prices/edit.html', metal_price=metal_price)

@metal_price_bp.route('/<int:price_id>/delete', methods=['POST'])
@login_required
def delete_price(price_id):
    """删除金属价格"""
    metal_price = MetalPrice.query.get_or_404(price_id)
    
    db.session.delete(metal_price)
    db.session.commit()
    
    flash('金属价格记录删除成功')
    return redirect(url_for('metal_price.list_prices'))