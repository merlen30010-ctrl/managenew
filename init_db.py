#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.material import Material
from app.models.customer import Customer
from app.models.department import Department
from app.models.contract import Contract, ContractFile
from app.models.attachment import Attachment
from app.models.article import Article
from app.models.article_category import ArticleCategory

def init_db():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建权限
        permissions_data = [
            # 用户管理权限
            {'name': 'user_read', 'description': '查看用户', 'module': 'user', 'action': 'read'},
            {'name': 'user_create', 'description': '创建用户', 'module': 'user', 'action': 'create'},
            {'name': 'user_update', 'description': '更新用户', 'module': 'user', 'action': 'update'},
            {'name': 'user_delete', 'description': '删除用户', 'module': 'user', 'action': 'delete'},
            
            # 物料管理权限
            {'name': 'material_read', 'description': '查看物料', 'module': 'material', 'action': 'read'},
            {'name': 'material_create', 'description': '创建物料', 'module': 'material', 'action': 'create'},
            {'name': 'material_update', 'description': '更新物料', 'module': 'material', 'action': 'update'},
            {'name': 'material_delete', 'description': '删除物料', 'module': 'material', 'action': 'delete'},
            
            # 客户管理权限
            {'name': 'customer_read', 'description': '查看客户', 'module': 'customer', 'action': 'read'},
            {'name': 'customer_create', 'description': '创建客户', 'module': 'customer', 'action': 'create'},
            {'name': 'customer_update', 'description': '更新客户', 'module': 'customer', 'action': 'update'},
            {'name': 'customer_delete', 'description': '删除客户', 'module': 'customer', 'action': 'delete'},
            
            # 部门管理权限
            {'name': 'department_read', 'description': '查看部门', 'module': 'department', 'action': 'read'},
            {'name': 'department_create', 'description': '创建部门', 'module': 'department', 'action': 'create'},
            {'name': 'department_update', 'description': '更新部门', 'module': 'department', 'action': 'update'},
            {'name': 'department_delete', 'description': '删除部门', 'module': 'department', 'action': 'delete'},
            
            # 合同管理权限
            {'name': 'contract_read', 'description': '查看合同', 'module': 'contract', 'action': 'read'},
            {'name': 'contract_create', 'description': '创建合同', 'module': 'contract', 'action': 'create'},
            {'name': 'contract_update', 'description': '更新合同', 'module': 'contract', 'action': 'update'},
            {'name': 'contract_delete', 'description': '删除合同', 'module': 'contract', 'action': 'delete'},
            
            # 附件管理权限
            {'name': 'attachment_read', 'description': '查看附件', 'module': 'attachment', 'action': 'read'},
            {'name': 'attachment_create', 'description': '上传附件', 'module': 'attachment', 'action': 'create'},
            {'name': 'attachment_update', 'description': '更新附件', 'module': 'attachment', 'action': 'update'},
            {'name': 'attachment_delete', 'description': '删除附件', 'module': 'attachment', 'action': 'delete'},
            
            # 化验数据管理权限
            {'name': 'assay_data_read', 'description': '查看化验数据', 'module': 'assay_data', 'action': 'read'},
            {'name': 'assay_data_create', 'description': '创建化验数据', 'module': 'assay_data', 'action': 'create'},
            {'name': 'assay_data_update', 'description': '更新化验数据', 'module': 'assay_data', 'action': 'update'},
            {'name': 'assay_data_delete', 'description': '删除化验数据', 'module': 'assay_data', 'action': 'delete'},
            
            # 物料进出厂管理权限
            {'name': 'material_transaction_read', 'description': '查看物料进出厂记录', 'module': 'material_transaction', 'action': 'read'},
            {'name': 'material_transaction_create', 'description': '创建物料进出厂记录', 'module': 'material_transaction', 'action': 'create'},
            {'name': 'material_transaction_update', 'description': '更新物料进出厂记录', 'module': 'material_transaction', 'action': 'update'},
            {'name': 'material_transaction_delete', 'description': '删除物料进出厂记录', 'module': 'material_transaction', 'action': 'delete'},
            
            # 物料进出厂分工协作权限
            {'name': 'material_transaction_weighing', 'description': '物料进出厂过磅操作', 'module': 'material_transaction', 'action': 'weighing'},
            {'name': 'material_transaction_assaying', 'description': '物料进出厂化验操作', 'module': 'material_transaction', 'action': 'assaying'},
            {'name': 'material_transaction_status_manage', 'description': '物料进出厂状态管理', 'module': 'material_transaction', 'action': 'status_manage'},
            
            # 产品产能管理权限
            {'name': 'production_record_read', 'description': '查看产能记录', 'module': 'production_record', 'action': 'read'},
            {'name': 'production_record_create', 'description': '创建产能记录', 'module': 'production_record', 'action': 'create'},
            {'name': 'production_record_update', 'description': '更新产能记录', 'module': 'production_record', 'action': 'update'},
            {'name': 'production_record_delete', 'description': '删除产能记录', 'module': 'production_record', 'action': 'delete'},
            {'name': 'production_record_status_manage', 'description': '产能记录状态管理', 'module': 'production_record', 'action': 'status_manage'},
            
            # 金属价格管理权限
            {'name': 'metal_price_read', 'description': '查看金属价格', 'module': 'metal_price', 'action': 'read'},
            {'name': 'metal_price_create', 'description': '创建金属价格', 'module': 'metal_price', 'action': 'create'},
            {'name': 'metal_price_update', 'description': '更新金属价格', 'module': 'metal_price', 'action': 'update'},
            {'name': 'metal_price_delete', 'description': '删除金属价格', 'module': 'metal_price', 'action': 'delete'},
            {'name': 'metal_price_import', 'description': '导入金属价格', 'module': 'metal_price', 'action': 'import'},
            {'name': 'metal_price_export', 'description': '导出金属价格', 'module': 'metal_price', 'action': 'export'},
            
            # Excel导入导出权限
            {'name': 'excel_import', 'description': 'Excel数据导入', 'module': 'excel', 'action': 'import'},
            {'name': 'excel_export', 'description': 'Excel数据导出', 'module': 'excel', 'action': 'export'},
            {'name': 'excel_template', 'description': 'Excel模板下载', 'module': 'excel', 'action': 'template'},
            
            # 车辆管理权限
            {'name': 'vehicle_read', 'description': '查看车辆', 'module': 'vehicle', 'action': 'read'},
            {'name': 'vehicle_create', 'description': '创建车辆', 'module': 'vehicle', 'action': 'create'},
            {'name': 'vehicle_update', 'description': '更新车辆', 'module': 'vehicle', 'action': 'update'},
            {'name': 'vehicle_delete', 'description': '删除车辆', 'module': 'vehicle', 'action': 'delete'},
            
            # 车辆借还权限
            {'name': 'vehicle_usage_read', 'description': '查看车辆借还记录', 'module': 'vehicle_usage', 'action': 'read'},
            {'name': 'vehicle_usage_create', 'description': '创建车辆借还记录', 'module': 'vehicle_usage', 'action': 'create'},
            {'name': 'vehicle_usage_update', 'description': '更新车辆借还记录', 'module': 'vehicle_usage', 'action': 'update'},
            {'name': 'vehicle_usage_delete', 'description': '删除车辆借还记录', 'module': 'vehicle_usage', 'action': 'delete'},
            
            # 车辆保养权限
            {'name': 'vehicle_maintenance_read', 'description': '查看保养记录', 'module': 'vehicle_maintenance', 'action': 'read'},
            {'name': 'vehicle_maintenance_create', 'description': '创建保养记录', 'module': 'vehicle_maintenance', 'action': 'create'},
            {'name': 'vehicle_maintenance_update', 'description': '更新保养记录', 'module': 'vehicle_maintenance', 'action': 'update'},
            {'name': 'vehicle_maintenance_delete', 'description': '删除保养记录', 'module': 'vehicle_maintenance', 'action': 'delete'},
            
            # 车辆保险权限
            {'name': 'vehicle_insurance_read', 'description': '查看保险记录', 'module': 'vehicle_insurance', 'action': 'read'},
            {'name': 'vehicle_insurance_create', 'description': '创建保险记录', 'module': 'vehicle_insurance', 'action': 'create'},
            {'name': 'vehicle_insurance_update', 'description': '更新保险记录', 'module': 'vehicle_insurance', 'action': 'update'},
            {'name': 'vehicle_insurance_delete', 'description': '删除保险记录', 'module': 'vehicle_insurance', 'action': 'delete'},
            
            # 通知管理权限
            {'name': 'notification_read', 'description': '查看通知', 'module': 'notification', 'action': 'read'},
            {'name': 'notification_create', 'description': '创建通知', 'module': 'notification', 'action': 'create'},
            {'name': 'notification_update', 'description': '更新通知', 'module': 'notification', 'action': 'update'},
            {'name': 'notification_delete', 'description': '删除通知', 'module': 'notification', 'action': 'delete'},
            {'name': 'notification_manage', 'description': '通知管理', 'module': 'notification', 'action': 'manage'},
            
            # 文章管理权限
            {'name': 'article_read', 'description': '查看文章', 'module': 'article', 'action': 'read'},
            {'name': 'article_create', 'description': '创建文章', 'module': 'article', 'action': 'create'},
            {'name': 'article_update', 'description': '更新文章', 'module': 'article', 'action': 'update'},
            {'name': 'article_delete', 'description': '删除文章', 'module': 'article', 'action': 'delete'},
            {'name': 'article_publish', 'description': '发布文章', 'module': 'article', 'action': 'publish'},
            {'name': 'article_manage', 'description': '文章管理', 'module': 'article', 'action': 'manage'},
            
            # 文章分类权限
            {'name': 'article_category_read', 'description': '查看文章分类', 'module': 'article_category', 'action': 'read'},
            {'name': 'article_category_create', 'description': '创建文章分类', 'module': 'article_category', 'action': 'create'},
            {'name': 'article_category_update', 'description': '更新文章分类', 'module': 'article_category', 'action': 'update'},
            {'name': 'article_category_delete', 'description': '删除文章分类', 'module': 'article_category', 'action': 'delete'},
        ]
        
        # 创建权限
        for perm_data in permissions_data:
            permission = Permission.query.filter_by(name=perm_data['name']).first()
            if not permission:
                permission = Permission(**perm_data)
                db.session.add(permission)
        
        db.session.commit()
        
        # 检查是否已存在管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        admin_role = Role.query.filter_by(name='管理员').first()
        
        # 如果管理员角色不存在，创建它
        if not admin_role:
            admin_role = Role(name='管理员', description='系统管理员')
            db.session.add(admin_role)
            db.session.commit()
        
        # 为管理员角色分配所有权限
        all_permissions = Permission.query.all()
        for permission in all_permissions:
            # 检查权限是否已分配给角色
            from app.models.permission import RolePermission
            existing_rp = RolePermission.query.filter_by(
                role_id=admin_role.id,
                permission_id=permission.id
            ).first()
            
            if not existing_rp:
                admin_role.add_permission(permission)
        
        # 如果管理员用户不存在，创建它
        if not admin_user:
            # 创建管理员用户
            admin_user = User()
            admin_user.username = 'admin'
            admin_user.email = 'admin@example.com'
            # name字段已移至Employee表
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            
            # 分配管理员角色
            admin_user.roles.append(admin_role)
            db.session.commit()
            
            print("管理员用户创建成功，用户名: admin，密码: admin123")
        else:
            # 确保管理员用户具有管理员角色
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)
                db.session.commit()
            print("管理员用户已存在")
        
        # 确保提交所有更改
        db.session.commit()
        
        print("数据库初始化完成")

if __name__ == '__main__':
    init_db()