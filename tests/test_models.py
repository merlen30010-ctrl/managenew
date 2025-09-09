import unittest
from app import create_app, db
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.material import Material
from app.models.customer import Customer
from app.models.department import Department, DepartmentManager
from app.models.contract import Contract, ContractFile

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_user_model(self):
        user = User(username='testuser')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        self.assertEqual(User.query.count(), 1)
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.check_password('wrongpassword'))
        
    def test_role_model(self):
        role = Role(name='admin', description='Administrator')
        db.session.add(role)
        db.session.commit()
        
        self.assertEqual(Role.query.count(), 1)
        self.assertEqual(role.name, 'admin')
        
    def test_user_role_relationship(self):
        user = User(username='testuser')
        user.set_password('password')
        role = Role(name='admin', description='Administrator')
        db.session.add(user)
        db.session.add(role)
        db.session.commit()
        
        # 创建用户角色关联
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.session.add(user_role)
        db.session.commit()
        
        self.assertEqual(UserRole.query.count(), 1)
        self.assertEqual(user.roles[0].name, 'admin')
        
    def test_material_model(self):
        material = Material(name='测试物料', code='MAT001', full_name='测试物料全称', purpose='原料')
        db.session.add(material)
        db.session.commit()
        
        self.assertEqual(Material.query.count(), 1)
        self.assertEqual(material.name, '测试物料')
        self.assertEqual(material.purpose, '原料')
        
    def test_customer_model(self):
        customer = Customer(name='测试客户', code='CUS001', full_name='测试客户全称', 
                          customer_type='产品采购', phone='13800138000', address='测试地址')
        db.session.add(customer)
        db.session.commit()
        
        self.assertEqual(Customer.query.count(), 1)
        self.assertEqual(customer.name, '测试客户')
        self.assertEqual(customer.customer_type, '产品采购')
        
    def test_department_model(self):
        # 创建分厂
        factory = Department(name='一分厂', short_name='一分厂', full_name='第一分厂', level=1)
        db.session.add(factory)
        db.session.commit()
        
        # 创建部门
        dept = Department(name='生产部', short_name='生产部', full_name='生产部', level=2, parent_id=factory.id)
        db.session.add(dept)
        db.session.commit()
        
        self.assertEqual(Department.query.count(), 2)
        self.assertEqual(dept.parent.name, '一分厂')
        
    def test_contract_model(self):
        # 创建客户
        customer = Customer(name='测试客户', code='CUS001', customer_type='产品采购')
        db.session.add(customer)
        db.session.commit()
        
        # 创建物料
        material = Material(name='测试物料', code='MAT001', purpose='产品')
        db.session.add(material)
        db.session.commit()
        
        # 创建分厂
        factory = Department(name='一分厂', level=1)
        db.session.add(factory)
        db.session.commit()
        
        # 创建用户
        user = User(username='testuser')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # 创建合同
        contract = Contract(
            contract_type='产品销售',
            contract_number='CON001',
            customer_id=customer.id,
            material_id=material.id,
            factory_id=factory.id,
            responsible_id=user.id,
            status='执行'
        )
        db.session.add(contract)
        db.session.commit()
        
        self.assertEqual(Contract.query.count(), 1)
        self.assertEqual(contract.contract_type, '产品销售')
        self.assertEqual(contract.customer.name, '测试客户')
        self.assertEqual(contract.material.name, '测试物料')

if __name__ == '__main__':
    unittest.main()