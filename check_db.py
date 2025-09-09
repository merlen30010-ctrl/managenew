#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.employee import Employee

def check_database():
    app = create_app()
    
    with app.app_context():
        try:
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"现有表: {existing_tables}")
            
            if 'employees' not in existing_tables:
                print("employees表不存在")
                return
            
            print("employees表存在！")
            
            # 使用原生SQL检查表结构
            with db.engine.connect() as connection:
                result = connection.execute(db.text("PRAGMA table_info(employees)"))
                columns = result.fetchall()
            
            print("\nemployees表结构:")
            print("列号 | 列名 | 类型 | 非空 | 默认值 | 主键")
            print("-" * 60)
            for col in columns:
                print(f"{col[0]:4} | {col[1]:15} | {col[2]:10} | {col[3]:4} | {str(col[4]) or 'NULL':10} | {col[5]:4}")
            
            # 检查记录数
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT COUNT(*) FROM employees"))
                count = result.fetchone()[0]
            print(f"\n员工记录总数: {count}")
            
            # 显示最近的几条记录
            if count > 0:
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SELECT id, name, job_title, employment_status, created_at FROM employees ORDER BY created_at DESC LIMIT 5"))
                    records = result.fetchall()
                print("\n最近的员工记录:")
                print("ID | 姓名 | 职位 | 状态 | 创建时间")
                print("-" * 60)
                for record in records:
                    print(f"{record[0]:2} | {record[1] or 'N/A':10} | {record[2] or 'N/A':15} | {record[3] or 'N/A':6} | {record[4]}")
            
        except Exception as e:
            print(f"检查数据库时出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_database()