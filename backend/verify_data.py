#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.models.material import Material
from app.models.customer import Customer
from app.models.contract import Contract
from app.models.vehicle import Vehicle
from app.models.assay_data import AssayData
from app.models.metal_price import MetalPrice
from app.models.material_transaction import MaterialTransaction
from app.models.production_record import ProductionRecord
from app.models.notification import Notification
from app.models.article import Article
from app.models.article_category import ArticleCategory

def verify_data():
    """验证数据"""
    app = create_app()
    
    with app.app_context():
        print("数据验证结果:")
        print(f"- 用户: {User.query.count()} 个")
        print(f"- 部门: {Department.query.count()} 个")
        print(f"- 员工: {Employee.query.count()} 个")
        print(f"- 物料: {Material.query.count()} 种")
        print(f"- 客户: {Customer.query.count()} 个")
        print(f"- 合同: {Contract.query.count()} 份")
        print(f"- 车辆: {Vehicle.query.count()} 辆")
        print(f"- 化验数据: {AssayData.query.count()} 条")
        print(f"- 金属价格: {MetalPrice.query.count()} 条")
        print(f"- 物料交易记录: {MaterialTransaction.query.count()} 条")
        print(f"- 生产记录: {ProductionRecord.query.count()} 条")
        print(f"- 通知: {Notification.query.count()} 条")
        print(f"- 文章分类: {ArticleCategory.query.count()} 个")
        print(f"- 文章: {Article.query.count()} 篇")

if __name__ == '__main__':
    verify_data()