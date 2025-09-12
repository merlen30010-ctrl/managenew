import unittest
import json
import os
import io
from app import create_app, db
from app.models import User, Department
from app.models.material_transaction import MaterialTransaction

class MaterialTransactionComprehensiveTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # 创建测试用户和部门
        self.department = Department(name='测试工厂', level=1)
        db.session.add(self.department)
        
        self.user = User(
            username='test_user',
            password='password',
            name='测试用户'
        )
        self.user.set_password('password')
        self.user.departments.append(self.department)
        self.user.permissions = ['material_transaction_read', 'material_transaction_update', 'material_transaction_create']
        db.session.add(self.user)
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
        
        # 清理测试过程中创建的附件文件
        test_upload_folder = os.path.join(self.app.config['UPLOAD_FOLDER'], 'material_transaction')
        if os.path.exists(test_upload_folder):
            for filename in os.listdir(test_upload_folder):
                file_path = os.path.join(test_upload_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    
    def test_create_and_update_transaction(self):
        # 创建物料进出记录
        response = self.client.post('/api/material-transactions', json={
            'factory_id': self.department.id,
            'material_name': '测试物料',
            'supplier': '测试供应商',
            'quantity': 100.0,
            'unit': '吨',
            'remarks': '测试备注'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        transaction_id = data['id']
        
        # 验证记录已创建
        transaction = MaterialTransaction.query.get(transaction_id)
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.material_name, '测试物料')
        self.assertEqual(transaction.supplier, '测试供应商')
        self.assertEqual(transaction.quantity, 100.0)
        self.assertEqual(transaction.unit, '吨')
        self.assertEqual(transaction.remarks, '测试备注')
        self.assertEqual(transaction.status, 'loading')
        self.assertEqual(transaction.editable, True)
        
        # 更新物料进出记录
        response = self.client.put(f'/api/material-transactions/{transaction_id}', json={
            'material_name': '更新后的物料',
            'quantity': 200.0,
            'remarks': '更新后的备注'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        
        # 验证记录已更新
        transaction = MaterialTransaction.query.get(transaction_id)
        self.assertEqual(transaction.material_name, '更新后的物料')
        self.assertEqual(transaction.quantity, 200.0)
        self.assertEqual(transaction.remarks, '更新后的备注')
        # 其他字段应保持不变
        self.assertEqual(transaction.supplier, '测试供应商')
        self.assertEqual(transaction.unit, '吨')
    
    def test_full_lifecycle(self):
        # 1. 创建物料进出记录
        response = self.client.post('/api/material-transactions', json={
            'factory_id': self.department.id,
            'material_name': '生命周期测试物料',
            'supplier': '生命周期测试供应商',
            'quantity': 150.0,
            'unit': '千克',
            'remarks': '生命周期测试'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        transaction_id = data['id']
        
        # 2. 上传附件
        test_file_content = b'This is a test file content'
        response = self.client.post(
            f'/api/material-transactions/{transaction_id}/attachments',
            data={
                'file': (io.BytesIO(test_file_content), 'test_file.txt')
            },
            headers={'Authorization': f'Bearer {self.token}'},
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 201)
        attachment_data = json.loads(response.data)
        attachment_id = attachment_data['id']
        
        # 3. 获取附件列表
        response = self.client.get(
            f'/api/material-transactions/{transaction_id}/attachments',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        attachments = json.loads(response.data)
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]['id'], attachment_id)
        self.assertEqual(attachments[0]['filename'], 'test_file.txt')
        
        # 4. 状态转换: loading -> arrived
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [transaction_id],
            'status': 'arrived'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], 1)
        
        # 验证状态已更新
        transaction = MaterialTransaction.query.get(transaction_id)
        self.assertEqual(transaction.status, 'arrived')
        
        # 5. 状态转换: arrived -> stored
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [transaction_id],
            'status': 'stored'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], 1)
        
        # 验证状态已更新
        transaction = MaterialTransaction.query.get(transaction_id)
        self.assertEqual(transaction.status, 'stored')
        
        # 6. 下载附件
        response = self.client.get(
            f'/api/material-transactions/{transaction_id}/attachments/{attachment_id}/download',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, test_file_content)
        
        # 7. 删除附件
        response = self.client.delete(
            f'/api/material-transactions/{transaction_id}/attachments/{attachment_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 204)
        
        # 验证附件已删除
        response = self.client.get(
            f'/api/material-transactions/{transaction_id}/attachments',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        attachments = json.loads(response.data)
        self.assertEqual(len(attachments), 0)
    
    def test_search_and_filter(self):
        # 创建多个测试记录
        transactions = [
            {
                'factory_id': self.department.id,
                'material_name': '测试物料A',
                'supplier': '供应商X',
                'quantity': 100.0,
                'unit': '吨',
                'status': 'loading'
            },
            {
                'factory_id': self.department.id,
                'material_name': '测试物料B',
                'supplier': '供应商Y',
                'quantity': 200.0,
                'unit': '千克',
                'status': 'loading'
            },
            {
                'factory_id': self.department.id,
                'material_name': '测试物料C',
                'supplier': '供应商X',
                'quantity': 300.0,
                'unit': '吨',
                'status': 'loading'
            }
        ]
        
        for transaction_data in transactions:
            transaction = MaterialTransaction(**transaction_data, created_by=self.user.id, editable=True)
            db.session.add(transaction)
        db.session.commit()
        
        # 测试按物料名称搜索
        response = self.client.get(
            '/api/material-transactions?material_name=物料B',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['material_name'], '测试物料B')
        
        # 测试按供应商筛选
        response = self.client.get(
            '/api/material-transactions?supplier=供应商X',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['items']), 2)
        
        # 测试按状态筛选
        response = self.client.get(
            '/api/material-transactions?status=loading',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['items']), 3)
        
        # 测试组合筛选
        response = self.client.get(
            '/api/material-transactions?supplier=供应商X&unit=吨',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['items']), 2)

if __name__ == '__main__':
    unittest.main()