#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.employee import Employee

app = create_app()
app.app_context().push()

employees = Employee.query.all()
print(f'数据库中员工总数: {len(employees)}')

for emp in employees:
    print(f'员工: {emp.name}, 状态: {emp.employment_status}, 职位: {emp.job_title}')