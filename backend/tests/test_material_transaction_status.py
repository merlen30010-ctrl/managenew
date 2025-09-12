import unittest
import json
from app import create_app, db
from app.models import User, Department
from app.models.material_transaction import MaterialTransaction

class MaterialTransactionStatusTestCase(unittest.TestCase):
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
        self.user.permissions = ['material_transaction_read', 'material_transaction_update']
        db.session.add(self.user)
        
        # 创建测试物料进出记录
        self.transaction1 = MaterialTransaction(
            factory_id=self.department.id,
            material_name='测试物料1',
            supplier='测试供应商',
            quantity=100.0,
            unit='吨',
            status='loading',
            editable=True,
            created_by=self.user.id
        )
        
        self.transaction2 = MaterialTransaction(
            factory_id=self.department.id,
            material_name='测试物料2',
            supplier='测试供应商',
            quantity=200.0,
            unit='吨',
            status='loading',
            editable=True,
            created_by=self.user.id
        )
        
        db.session.add(self.transaction1)
        db.session.add(self.transaction2)
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
    
    def test_batch_update_status(self):
        # 从loading到arrived
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [self.transaction1.id, self.transaction2.id],
            'status': 'arrived'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], 2)
        self.assertEqual(data['failed'], 0)
        
        # 验证数据库中的状态
        transaction1 = MaterialTransaction.query.get(self.transaction1.id)
        transaction2 = MaterialTransaction.query.get(self.transaction2.id)
        self.assertEqual(transaction1.status, 'arrived')
        self.assertEqual(transaction2.status, 'arrived')
        
        # 从arrived到stored
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [self.transaction1.id, self.transaction2.id],
            'status': 'stored'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], 2)
        self.assertEqual(data['failed'], 0)
        
        # 验证数据库中的状态
        transaction1 = MaterialTransaction.query.get(self.transaction1.id)
        transaction2 = MaterialTransaction.query.get(self.transaction2.id)
        self.assertEqual(transaction1.status, 'stored')
        self.assertEqual(transaction2.status, 'stored')
        
        # 从stored到used
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [self.transaction1.id, self.transaction2.id],
            'status': 'used'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], 2)
        self.assertEqual(data['failed'], 0)
        
        # 验证数据库中的状态
        transaction1 = MaterialTransaction.query.get(self.transaction1.id)
        transaction2 = MaterialTransaction.query.get(self.transaction2.id)
        self.assertEqual(transaction1.status, 'used')
        self.assertEqual(transaction2.status, 'used')
    
    def test_invalid_status_transition(self):
        # 尝试从loading直接到stored（无效的状态转换）
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [self.transaction1.id],
            'status': 'stored'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], 0)
        self.assertEqual(data['failed'], 1)
        
        # 验证数据库中的状态未变
        transaction1 = MaterialTransaction.query.get(self.transaction1.id)
        self.assertEqual(transaction1.status, 'loading')
    
    def test_permission_check(self):
        # 创建无权限用户
        no_perm_user = User(
            username='no_perm_user',
            password='password',
            name='无权限用户'
        )
        no_perm_user.set_password('password')
        no_perm_user.departments.append(self.department)
        # 不添加material_transaction_update权限
        db.session.add(no_perm_user)
        db.session.commit()
        
        # 登录无权限用户
        response = self.client.post('/api/auth/login', json={
            'username': 'no_perm_user',
            'password': 'password'
        })
        data = json.loads(response.data)
        no_perm_token = data['token']
        
        # 尝试更新状态（应该失败）
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [self.transaction1.id],
            'status': 'arrived'
        }, headers={'Authorization': f'Bearer {no_perm_token}'})
        
        # 验证更新失败
        self.assertEqual(response.status_code, 403)
        
        # 验证数据库中的状态未变
        transaction1 = MaterialTransaction.query.get(self.transaction1.id)
        self.assertEqual(transaction1.status, 'loading')
    
    def test_partial_update(self):
        # 创建不同状态的记录
        transaction3 = MaterialTransaction(
            factory_id=self.department.id,
            material_name='测试物料3',
            supplier='测试供应商',
            quantity=300.0,
            unit='吨',
            status='loading',
            editable=True,
            created_by=self.user.id
        )
        
        # 先将transaction1更新到arrived状态
        self.transaction1.status = 'arrived'
        db.session.add(transaction3)
        db.session.commit()
        
        # 批量更新状态，应该只有符合条件的记录会被更新
        response = self.client.post('/api/material-transactions/batch-update-status', json={
            'ids': [self.transaction1.id, self.transaction2.id, transaction3.id],
            'status': 'stored'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], 1)  # 只有transaction1应该成功更新
        self.assertEqual(data['failed'], 2)   # transaction2和transaction3应该失败
        
        # 验证数据库中的状态
        transaction1 = MaterialTransaction.query.get(self.transaction1.id)
        transaction2 = MaterialTransaction.query.get(self.transaction2.id)
        transaction3 = MaterialTransaction.query.get(transaction3.id)
        self.assertEqual(transaction1.status, 'stored')   # 已更新
        self.assertEqual(transaction2.status, 'loading')  # 未更新
        self.assertEqual(transaction3.status, 'loading')  # 未更新

if __name__ == '__main__':
    unittest.main()