import unittest
import os
import tempfile
import json
from datetime import datetime
from app import create_app, db
from app.models import User, Department, Attachment
from app.models.material_transaction import MaterialTransaction

class MaterialTransactionAttachmentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # 创建测试用户和部门
        self.department = Department(name='测试工厂', level=1)
        db.session.add(self.department)
        
        # 创建测试用户
        self.user = User(
            username='test_user',
            name='测试用户'
        )
        self.user.set_password('password')
        # 不再使用departments和permissions属性
        db.session.add(self.user)
        
        # 创建测试物料进出记录
        self.transaction = MaterialTransaction(
            factory_id=self.department.id,
            date=datetime.now().date(),
            customer='测试客户',
            material_name='测试物料',
            transaction_type='进厂',
            shipped_quantity=100.0,
            received_quantity=100.0,
            status='loading',
            created_by=self.user.id
        )
        db.session.add(self.transaction)
        db.session.commit()
        
        # 登录
        response = self.client.post('/api/auth/login', json={
            'username': 'test_user',
            'password': 'password'
        })
        data = json.loads(response.data)
        self.token = data['token']
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_upload_attachment(self):
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b'Test attachment content')
            temp_path = temp.name
        
        try:
            # 上传附件
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    f'/api/material-transactions/{self.transaction.id}/attachments',
                    data={'file': (f, 'test.txt')},
                    headers={'Authorization': f'Bearer {self.token}'},
                    content_type='multipart/form-data'
                )
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            attachment_id = data['id']
            
            # 验证数据库中的附件记录
            attachment = Attachment.query.get(attachment_id)
            self.assertIsNotNone(attachment)
            self.assertEqual(attachment.filename, 'test.txt')
            self.assertEqual(attachment.material_transaction_id, self.transaction.id)
            
            # 下载附件
            response = self.client.get(
                f'/api/attachments/{attachment_id}/download',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, b'Test attachment content')
            
            # 删除附件
            response = self.client.delete(
                f'/api/attachments/{attachment_id}',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            self.assertEqual(response.status_code, 200)
            
            # 验证附件已被删除
            attachment = Attachment.query.get(attachment_id)
            self.assertIsNone(attachment)
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_attachment_permission(self):
        # 创建无权限用户
        no_perm_user = User(
            username='no_perm_user',
            name='无权限用户'
        )
        no_perm_user.set_password('password')
        # 不再使用departments和permissions属性
        db.session.add(no_perm_user)
        db.session.commit()
        
        # 登录无权限用户
        response = self.client.post('/api/auth/login', json={
            'username': 'no_perm_user',
            'password': 'password'
        })
        data = json.loads(response.data)
        no_perm_token = data['token']
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b'Test attachment content')
            temp_path = temp.name
        
        try:
            # 尝试上传附件（应该失败）
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    f'/api/material-transactions/{self.transaction.id}/attachments',
                    data={'file': (f, 'test.txt')},
                    headers={'Authorization': f'Bearer {no_perm_token}'},
                    content_type='multipart/form-data'
                )
            
            # 验证上传失败
            self.assertEqual(response.status_code, 403)
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_attachments(self):
        # 创建多个临时文件并上传
        temp_files = []
        attachment_ids = []
        
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
                temp.write(f'Test attachment content {i}'.encode())
                temp_files.append(temp.name)
        
        try:
            # 上传多个附件
            for i, temp_path in enumerate(temp_files):
                with open(temp_path, 'rb') as f:
                    response = self.client.post(
                        f'/api/material-transactions/{self.transaction.id}/attachments',
                        data={'file': (f, f'test_{i}.txt')},
                        headers={'Authorization': f'Bearer {self.token}'},
                        content_type='multipart/form-data'
                    )
                
                self.assertEqual(response.status_code, 201)
                data = json.loads(response.data)
                attachment_ids.append(data['id'])
            
            # 获取附件列表
            response = self.client.get(
                f'/api/material-transactions/{self.transaction.id}/attachments',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # 验证附件列表
            self.assertEqual(len(data), 3)
            filenames = [attachment['filename'] for attachment in data]
            for i in range(3):
                self.assertIn(f'test_{i}.txt', filenames)
            
            # 清理附件
            for attachment_id in attachment_ids:
                response = self.client.delete(
                    f'/api/attachments/{attachment_id}',
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                self.assertEqual(response.status_code, 200)
        finally:
            # 清理临时文件
            for temp_path in temp_files:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()