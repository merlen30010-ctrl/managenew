#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.employee import Employee
from app.models.user import User

def check_employee_user_relation():
    """检查员工和用户的关联关系"""
    app = create_app()
    
    with app.app_context():
        print("=== 检查员工和用户关联关系 ===")
        
        # 获取所有员工
        employees = Employee.query.all()
        print(f"\n数据库中员工总数: {len(employees)}")
        
        for emp in employees:
            print(f"\n员工: {emp.name}")
            print(f"  - ID: {emp.id}")
            print(f"  - 员工编号: {emp.employee_id}")
            print(f"  - 用户ID: {emp.user_id}")
            print(f"  - 状态: {emp.employment_status}")
            print(f"  - 部门ID: {emp.department_id}")
            
            # 检查关联的用户
            if emp.user_id:
                user = User.query.get(emp.user_id)
                if user:
                    print(f"  - 关联用户: {user.username} ({user.email})")
                    print(f"  - 用户状态: {'活跃' if user.is_active else '非活跃'}")
                else:
                    print(f"  - 警告: 用户ID {emp.user_id} 不存在！")
            else:
                print(f"  - 警告: 没有关联用户！")
        
        # 测试不同的查询方式
        print("\n=== 测试不同查询方式 ===")
        
        # 1. 直接查询Employee
        direct_query = Employee.query.all()
        print(f"\n1. 直接查询Employee: {len(direct_query)} 条记录")
        
        # 2. Employee join User (inner join)
        try:
            inner_join_query = db.session.query(Employee).join(User).all()
            print(f"2. Employee inner join User: {len(inner_join_query)} 条记录")
        except Exception as e:
            print(f"2. Employee inner join User 失败: {str(e)}")
        
        # 3. Employee left join User
        try:
            left_join_query = db.session.query(Employee).outerjoin(User).all()
            print(f"3. Employee left join User: {len(left_join_query)} 条记录")
        except Exception as e:
            print(f"3. Employee left join User 失败: {str(e)}")
        
        # 4. 检查没有user_id的员工
        no_user_employees = Employee.query.filter(Employee.user_id.is_(None)).all()
        print(f"4. 没有user_id的员工: {len(no_user_employees)} 条记录")
        for emp in no_user_employees:
            print(f"   - {emp.name} (ID: {emp.id})")
        
        # 5. 检查user_id不存在的员工
        invalid_user_employees = []
        for emp in employees:
            if emp.user_id and not User.query.get(emp.user_id):
                invalid_user_employees.append(emp)
        print(f"5. user_id无效的员工: {len(invalid_user_employees)} 条记录")
        for emp in invalid_user_employees:
            print(f"   - {emp.name} (user_id: {emp.user_id})")

if __name__ == '__main__':
    check_employee_user_relation()