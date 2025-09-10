from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.customer import Customer

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
@login_required
def list_customers():
    customers = Customer.query.all()
    return render_template('customers/list.html', customers=customers)

@customer_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        full_name = request.form.get('full_name')
        customer_type = request.form.get('customer_type')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # 检查客户代码是否已存在
        if Customer.query.filter_by(code=code).first():
            flash('客户代码已存在')
            return redirect(url_for('customer.create_customer'))
        
        # 创建新客户
        customer = Customer(name=name, code=code, full_name=full_name, 
                          customer_type=customer_type, phone=phone, address=address)
        db.session.add(customer)
        db.session.commit()
        
        flash('客户创建成功')
        return redirect(url_for('customer.list_customers'))
        
    return render_template('customers/create.html')

@customer_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.code = request.form.get('code')
        customer.full_name = request.form.get('full_name')
        customer.customer_type = request.form.get('customer_type')
        customer.phone = request.form.get('phone')
        customer.address = request.form.get('address')
        
        db.session.commit()
        flash('客户信息更新成功')
        return redirect(url_for('customer.list_customers'))
        
    return render_template('customers/edit.html', customer=customer)

@customer_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('客户删除成功')
    return redirect(url_for('customer.list_customers'))