#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文章功能测试脚本
用于验证文章管理系统的功能是否正常工作
"""

import os
import sys
import unittest
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置Flask应用环境变量
os.environ['FLASK_APP'] = 'run.py'

from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.article import Article
from app.models.article_category import ArticleCategory
from app.models.attachment import Attachment

class ArticleTestCase(unittest.TestCase):
    """文章功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试数据
        self.create_test_data()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建测试用户
        self.test_user = User(
            username='testuser',

        )
        self.test_user.set_password('test123')
        db.session.add(self.test_user)
        
        # 创建测试角色和权限
        self.test_role = Role(name='测试角色', description='测试用角色')
        db.session.add(self.test_role)
        
        # 创建文章相关权限（如果不存在）
        permission_data = [
            ('article_read', '查看文章', 'article', 'read'),
            ('article_create', '创建文章', 'article', 'create'),
            ('article_update', '更新文章', 'article', 'update'),
            ('article_delete', '删除文章', 'article', 'delete'),
            ('article_category_create', '创建分类', 'article_category', 'create'),
        ]
        
        permissions = []
        for name, desc, module, action in permission_data:
            perm = Permission.query.filter_by(name=name).first()
            if not perm:
                perm = Permission(name=name, description=desc, module=module, action=action)
                db.session.add(perm)
            permissions.append(perm)
        
        db.session.commit()
        
        # 为角色分配权限
        for perm in permissions:
            self.test_role.add_permission(perm)
        
        # 为用户分配角色
        from app.models.role import UserRole
        user_role = UserRole(user_id=self.test_user.id, role_id=self.test_role.id)
        db.session.add(user_role)
        
        # 创建测试分类
        self.test_category = ArticleCategory(
            name='测试分类',
            description='这是一个测试分类',
            sort_order=1
        )
        db.session.add(self.test_category)
        
        db.session.commit()
    
    def test_article_category_model(self):
        """测试文章分类模型"""
        category = ArticleCategory(
            name='新分类',
            description='新分类描述',
            sort_order=2
        )
        db.session.add(category)
        db.session.commit()
        
        # 验证分类创建成功
        self.assertEqual(ArticleCategory.query.count(), 2)  # 包括setUp中创建的测试分类
        self.assertEqual(category.name, '新分类')
        self.assertEqual(category.description, '新分类描述')
        self.assertEqual(category.sort_order, 2)
        self.assertTrue(category.is_active)
    
    def test_article_model(self):
        """测试文章模型"""
        article = Article(
            title='测试文章',
            content='这是测试文章的内容',
            summary='文章摘要',
            author_id=self.test_user.id,
            category_id=self.test_category.id,
            status='published'
        )
        db.session.add(article)
        db.session.commit()
        
        # 验证文章创建成功
        self.assertEqual(Article.query.count(), 1)
        self.assertEqual(article.title, '测试文章')
        self.assertEqual(article.content, '这是测试文章的内容')
        self.assertEqual(article.author_id, self.test_user.id)
        self.assertEqual(article.category_id, self.test_category.id)
        self.assertEqual(article.status, 'published')
    
    def test_article_api_create(self):
        """测试创建文章API"""
        # 模拟登录
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user.id)
            sess['_fresh'] = True
        
        article_data = {
            'title': 'API测试文章',
            'content': '通过API创建的文章内容',
            'summary': 'API文章摘要',
            'category_id': self.test_category.id,
            'status': 'draft'
        }
        
        response = self.client.post(
            '/api/articles',
            data=json.dumps(article_data),
            content_type='application/json'
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], 'API测试文章')
    
    def test_article_api_list(self):
        """测试获取文章列表API"""
        # 模拟登录
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user.id)
            sess['_fresh'] = True
        
        # 创建测试文章
        article = Article(
            title='列表测试文章',
            content='文章内容',
            author_id=self.test_user.id,
            category_id=self.test_category.id,
            status='published'
        )
        db.session.add(article)
        db.session.commit()
        
        response = self.client.get('/api/articles')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['articles']), 1)
        self.assertEqual(data['data']['articles'][0]['title'], '列表测试文章')
    
    def test_article_category_api_create(self):
        """测试创建分类API"""
        # 模拟登录
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user.id)
            sess['_fresh'] = True
        
        category_data = {
            'name': 'API测试分类',
            'description': '通过API创建的分类',
            'sort_order': 10
        }
        
        response = self.client.post(
            '/api/article-categories',
            data=json.dumps(category_data),
            content_type='application/json'
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'API测试分类')
    
    def test_article_permissions(self):
        """测试文章权限"""
        # 测试用户权限检查
        self.assertTrue(self.test_user.has_permission_name('article_read'))
        self.assertTrue(self.test_user.has_permission_name('article_create'))
        self.assertTrue(self.test_user.has_permission_name('article_update'))
        self.assertTrue(self.test_user.has_permission_name('article_delete'))
        
        # 测试不存在的权限
        self.assertFalse(self.test_user.has_permission_name('nonexistent_permission'))
    
    def test_article_views(self):
        """测试文章视图"""
        # 模拟登录
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user.id)
            sess['_fresh'] = True
        
        # 创建测试文章
        article = Article(
            title='视图测试文章',
            content='文章内容',
            author_id=self.test_user.id,
            category_id=self.test_category.id,
            status='published'
        )
        db.session.add(article)
        db.session.commit()
        
        # 测试用户文章列表页面
        response = self.client.get('/articles')
        self.assertEqual(response.status_code, 200)
        
        # 测试文章详情页面
        response = self.client.get(f'/articles/{article.id}')
        self.assertEqual(response.status_code, 200)
        
        # 测试分类列表页面
        response = self.client.get('/admin/article-categories')
        self.assertEqual(response.status_code, 200)

def run_article_tests():
    """运行文章功能测试"""
    print("开始运行文章功能测试...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(ArticleTestCase)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    if result.wasSuccessful():
        print("\n所有文章功能测试通过！")
    else:
        print(f"\n测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        for failure in result.failures:
            print(f"失败: {failure[0]} - {failure[1]}")
        for error in result.errors:
            print(f"错误: {error[0]} - {error[1]}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_article_tests()