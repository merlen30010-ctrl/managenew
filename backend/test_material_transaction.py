import unittest
import json
from app import create_app, db
from app.models.material_transaction import MaterialTransaction
from app.models.user import User
from app.models.department import Department
from datetime import datetime

class MaterialTransactionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # 创建测试用户
        self.admin_user = User(username='admin_test', is_superuser=True)
        self.admin_user.set_password('password')
        
        # 创建测试部门
        self.factory = Department(name='测试工厂', level=1)
        
        # 添加到数据库
        db.session.add(self.admin_user)
        db.session.add(self.factory)
        db.session.commit()
        
        # 登录
        response = self.client.post('/api/auth/login', 
                                  data=json.dumps({'username': 'admin_test', 'password': 'password'}),
                                  content_type='application/json')
        self.token = json.loads(response.data)['token']
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_material_transaction_status_flow(self):
        """测试物料进出厂状态流转功能"""
        # 1. 创建物料进出厂记录
        transaction_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'customer': '测试客户',
            'material_name': '测试物料',
            'factory_id': self.factory.id,
            'contract_number': 'TEST-001',
            'transaction_type': 'in',
            'packaging': '袋装',
            'vehicle_number': '粤A12345',
            'shipped_quantity': 100,
            'driver_name': '张三',
            'driver_phone': '13800138000',
            'driver_id_card': '440101199001011234'
        }
        
        response = self.client.post('/api/material-transactions',
                                  data=json.dumps(transaction_data),
                                  content_type='application/json',
                                  headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 201)
        transaction_id = json.loads(response.data)['id']
        
        # 2. 验证初始状态为loading
        response = self.client.get(f'/api/material-transactions/{transaction_id}',
                                 headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'loading')
        self.assertTrue(data['editable'])
        
        # 3. 更新状态为arrived
        status_data = {'status': 'arrived'}
        response = self.client.put(f'/api/material-transactions/{transaction_id}/status',
                                data=json.dumps(status_data),
                                content_type='application/json',
                                headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'arrived')
        self.assertTrue(data['editable'])
        self.assertIsNotNone(data['arrival_time'])
        self.assertEqual(data['arrival_by'], self.admin_user.id)
        
        # 4. 更新状态为stored
        status_data = {'status': 'stored'}
        response = self.client.put(f'/api/material-transactions/{transaction_id}/status',
                                data=json.dumps(status_data),
                                content_type='application/json',
                                headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'stored')
        self.assertTrue(data['editable'])
        self.assertIsNotNone(data['storage_time'])
        self.assertEqual(data['storage_by'], self.admin_user.id)
        
        # 5. 更新状态为used
        status_data = {'status': 'used'}
        response = self.client.put(f'/api/material-transactions/{transaction_id}/status',
                                data=json.dumps(status_data),
                                content_type='application/json',
                                headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'used')
        self.assertFalse(data['editable'])  # 使用后不可编辑
        self.assertIsNotNone(data['usage_time'])
        self.assertEqual(data['usage_by'], self.admin_user.id)
        
        # 6. 尝试编辑已使用的记录（应该失败）
        edit_data = {'remarks': '尝试编辑已使用的记录'}
        response = self.client.put(f'/api/material-transactions/{transaction_id}',
                                data=json.dumps(edit_data),
                                content_type='application/json',
                                headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 403)
        
        # 7. 测试无效的状态转换（从loading直接到stored，应该失败）
        # 创建新记录
        response = self.client.post('/api/material-transactions',
                                  data=json.dumps(transaction_data),
                                  content_type='application/json',
                                  headers={'Authorization': f'Bearer {self.token}'})
        
        new_transaction_id = json.loads(response.data)['id']
        
        # 尝试从loading直接到stored
        status_data = {'status': 'stored'}
        response = self.client.put(f'/api/material-transactions/{new_transaction_id}/status',
                                data=json.dumps(status_data),
                                content_type='application/json',
                                headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 400)  # 应该返回错误

if __name__ == '__main__':
    unittest.main()