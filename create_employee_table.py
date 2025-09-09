#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.employee import Employee

def create_employee_table():
    """专门创建employees表"""
    app = create_app()
    
    with app.app_context():
        # 检查表是否存在
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"现有表: {existing_tables}")
        
        # 强制创建employees表
        print("正在创建employees表...")
        Employee.__table__.create(db.engine, checkfirst=True)
        
        # 再次检查
        existing_tables = inspector.get_table_names()
        print(f"创建后的表: {existing_tables}")
        
        if 'employees' in existing_tables:
            print("employees表创建成功！")
        else:
            print("employees表创建失败！")

if __name__ == '__main__':
    create_employee_table()