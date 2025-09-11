#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
from datetime import datetime, date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.department import Department
from app.models.employee import Employee
from app.models.material import Material
from app.models.customer import Customer
from app.models.contract import Contract
from app.models.vehicle import Vehicle, VehicleUsageRecord, MaintenanceRecord, InsuranceRecord
from app.models.assay_data import AssayData
from app.models.metal_price import MetalPrice
from app.models.material_transaction import MaterialTransaction
from app.models.production_record import ProductionRecord
from app.models.notification import Notification
from app.models.article import Article
from app.models.article_category import ArticleCategory

# 随机数据生成函数
def random_date(start_date, end_date):
    """生成随机日期"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def random_phone():
    """生成随机电话号码"""
    return f"1{random.randint(3, 9)}{random.randint(0, 9)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"

def random_id_card():
    """生成随机身份证号"""
    return f"{random.randint(110000, 659000)}{random.randint(1980, 2000)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

def random_name():
    """生成随机姓名"""
    surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
    names = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞"]
    return random.choice(surnames) + random.choice(names)

def add_test_data():
    """添加测试数据"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已有测试数据
        if User.query.count() > 1:  # 超过管理员用户
            print("检测到已有测试数据，是否继续添加？(y/n)")
            # 这里简化处理，实际应用中可以添加用户确认
            pass
        
        print("开始添加测试数据...")
        
        # 1. 添加部门数据
        departments_data = [
            {"name": "生产一部", "short_name": "一部", "full_name": "第一生产分厂", "level": 1, "phone": "010-12345678"},
            {"name": "生产二部", "short_name": "二部", "full_name": "第二生产分厂", "level": 1, "phone": "010-12345679"},
            {"name": "生产三部", "short_name": "三部", "full_name": "第三生产分厂", "level": 1, "phone": "010-12345680"},
            {"name": "质检部", "short_name": "质检", "full_name": "质量检测部门", "level": 2, "phone": "010-12345681"},
            {"name": "仓储部", "short_name": "仓储", "full_name": "仓储管理部门", "level": 2, "phone": "010-12345682"},
            {"name": "销售部", "short_name": "销售", "full_name": "产品销售部门", "level": 2, "phone": "010-12345683"},
            {"name": "采购部", "short_name": "采购", "full_name": "原材料采购部门", "level": 2, "phone": "010-12345684"},
            {"name": "人事部", "short_name": "人事", "full_name": "人力资源部门", "level": 2, "phone": "010-12345685"},
            {"name": "财务部", "short_name": "财务", "full_name": "财务管理部", "level": 2, "phone": "010-12345686"},
            {"name": "行政部", "short_name": "行政", "full_name": "行政管理部门", "level": 2, "phone": "010-12345687"}
        ]
        
        departments = []
        for dept_data in departments_data:
            dept = Department.query.filter_by(name=dept_data["name"]).first()
            if not dept:
                dept = Department(**dept_data)
                db.session.add(dept)
                db.session.commit()
            departments.append(dept)
        
        print(f"已添加/确认 {len(departments)} 个部门")
        
        # 2. 添加用户数据
        users = []
        # 先获取已存在的管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            users.append(admin_user)
        
        # 添加普通用户
        for i in range(10):
            username = f"user{i+1:03d}"
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User()
                user.username = username
                user.name = random_name()
                user.set_password("123456")
                user.is_active = True
                db.session.add(user)
                db.session.commit()
                
                # 随机分配部门
                if departments:
                    dept = random.choice(departments)
                    # 这里简化处理，实际应用中可能需要通过员工表关联
            users.append(user)
        
        print(f"已添加/确认 {len(users)} 个用户")
        
        # 3. 添加员工数据
        employees = []
        for i in range(20):
            employee_id = f"EMP{i+1:04d}"
            emp = Employee.query.filter_by(employee_id=employee_id).first()
            if not emp:
                emp = Employee()
                emp.employee_id = employee_id
                emp.name = random_name()
                emp.gender = random.choice(["男", "女"])
                emp.birth_date = random_date(date(1980, 1, 1), date(1995, 12, 31))
                emp.id_card = random_id_card()
                emp.phone = random_phone()
                emp.department_id = random.choice(departments).id if departments else None
                emp.job_title = random.choice(["操作工", "技术员", "班组长", "主管", "经理"])
                emp.hire_date = random_date(date(2015, 1, 1), date(2023, 12, 31))
                emp.education = random.choice(["高中", "大专", "本科", "硕士"])
                emp.employment_status = random.choice(["在职", "储备", "试用"])
                emp.address = f"北京市朝阳区{random.randint(1, 100)}号"
                db.session.add(emp)
                db.session.commit()
            employees.append(emp)
        
        print(f"已添加/确认 {len(employees)} 个员工")
        
        # 4. 添加物料数据
        materials_data = [
            {"name": "锌精矿", "code": "MAT001", "full_name": "锌精矿原料", "purpose": "原料"},
            {"name": "焙砂", "code": "MAT002", "full_name": "锌焙砂产品", "purpose": "产品"},
            {"name": "硫酸", "code": "MAT003", "full_name": "工业硫酸", "purpose": "辅料"},
            {"name": "煤炭", "code": "MAT004", "full_name": "工业煤炭", "purpose": "辅料"},
            {"name": "石灰石", "code": "MAT005", "full_name": "石灰石粉", "purpose": "辅料"},
            {"name": "液氨", "code": "MAT006", "full_name": "液氨", "purpose": "辅料"},
            {"name": "锌锭", "code": "MAT007", "full_name": "1#锌锭", "purpose": "产品"},
            {"name": "铅精矿", "code": "MAT008", "full_name": "铅精矿原料", "purpose": "原料"},
            {"name": "银精矿", "code": "MAT009", "full_name": "银精矿原料", "purpose": "原料"},
            {"name": "铜精矿", "code": "MAT010", "full_name": "铜精矿原料", "purpose": "原料"}
        ]
        
        materials = []
        for mat_data in materials_data:
            mat = Material.query.filter_by(code=mat_data["code"]).first()
            if not mat:
                mat = Material(**mat_data)
                db.session.add(mat)
                db.session.commit()
            materials.append(mat)
        
        print(f"已添加/确认 {len(materials)} 种物料")
        
        # 5. 添加客户数据
        customers_data = [
            {"name": "北方矿业集团", "code": "CUS001", "full_name": "北方矿业集团有限公司", "customer_type": "原料供应", "phone": "010-87654321", "address": "北京市海淀区中关村大街1号"},
            {"name": "南方冶炼厂", "code": "CUS002", "full_name": "南方有色金属冶炼厂", "customer_type": "产品采购", "phone": "020-87654322", "address": "广州市天河区珠江新城2号"},
            {"name": "华东化工", "code": "CUS003", "full_name": "华东化工有限公司", "customer_type": "辅料供应", "phone": "021-87654323", "address": "上海市浦东新区陆家嘴3号"},
            {"name": "西部能源", "code": "CUS004", "full_name": "西部能源集团", "customer_type": "辅料供应", "phone": "0991-87654324", "address": "乌鲁木齐市天山区解放路4号"},
            {"name": "中部贸易", "code": "CUS005", "full_name": "中部国际贸易有限公司", "customer_type": "原料供应", "phone": "0371-87654325", "address": "郑州市金水区商务内环5号"},
            {"name": "南方金属", "code": "CUS006", "full_name": "南方有色金属贸易有限公司", "customer_type": "产品采购", "phone": "0755-87654326", "address": "深圳市福田区深南大道6号"},
            {"name": "东方物流", "code": "CUS007", "full_name": "东方物流集团有限公司", "customer_type": "其他", "phone": "0512-87654327", "address": "苏州市工业园区星湖街7号"},
            {"name": "北方化工", "code": "CUS008", "full_name": "北方化工股份有限公司", "customer_type": "辅料供应", "phone": "0411-87654328", "address": "大连市中山区港湾街8号"},
            {"name": "西南矿业", "code": "CUS009", "full_name": "西南矿业集团有限公司", "customer_type": "原料供应", "phone": "0871-87654329", "address": "昆明市五华区金碧路9号"},
            {"name": "东北钢铁", "code": "CUS010", "full_name": "东北特殊钢集团有限公司", "customer_type": "产品采购", "phone": "0411-87654330", "address": "大连市经济技术开发区黄海西路10号"}
        ]
        
        customers = []
        for cust_data in customers_data:
            cust = Customer.query.filter_by(code=cust_data["code"]).first()
            if not cust:
                cust = Customer(**cust_data)
                db.session.add(cust)
                db.session.commit()
            customers.append(cust)
        
        print(f"已添加/确认 {len(customers)} 个客户")
        
        # 6. 添加合同数据
        contracts = []
        for i in range(10):
            contract_number = f"CON{i+1:04d}"
            cont = Contract.query.filter_by(contract_number=contract_number).first()
            if not cont:
                cont = Contract()
                cont.contract_number = contract_number
                cont.contract_type = random.choice(["原料采购", "产品销售", "辅料采购"])
                cont.customer_id = random.choice(customers).id
                cont.material_id = random.choice(materials).id
                cont.factory_id = random.choice(departments[:3]).id  # 从生产部门中选择
                cont.responsible_id = random.choice(users).id
                cont.sign_date = random_date(date(2023, 1, 1), date(2024, 12, 31))
                cont.expiry_date = cont.sign_date + timedelta(days=random.randint(30, 365))
                cont.tax_rate = random.choice([0.0, 0.03, 0.06, 0.09, 0.13])
                cont.pricing_method = random.choice(["weight", "content", "processing", "gross_weight"])
                cont.coefficient = round(random.uniform(-0.5, 2.0), 2)
                cont.status = random.choice(["执行", "归档"])
                db.session.add(cont)
                db.session.commit()
            contracts.append(cont)
        
        print(f"已添加/确认 {len(contracts)} 份合同")
        
        # 7. 添加车辆数据
        vehicles_data = [
            {"plate_number": "京A12345", "brand": "解放", "model": "J6P", "color": "红色", "status": "可用"},
            {"plate_number": "京B23456", "brand": "东风", "model": "天龙", "color": "蓝色", "status": "可用"},
            {"plate_number": "京C34567", "brand": "重汽", "model": "豪沃", "color": "白色", "status": "已借出"},
            {"plate_number": "京D45678", "brand": "陕汽", "model": "德龙", "color": "黄色", "status": "维修中"},
            {"plate_number": "京E56789", "brand": "福田", "model": "欧曼", "color": "绿色", "status": "可用"},
            {"plate_number": "京F67890", "brand": "一汽", "model": "解放J7", "color": "灰色", "status": "可用"},
            {"plate_number": "京G78901", "brand": "沃尔沃", "model": "FH", "color": "白色", "status": "已借出"},
            {"plate_number": "京H89012", "brand": "奔驰", "model": "Actros", "color": "红色", "status": "可用"},
            {"plate_number": "京J90123", "brand": "斯堪尼亚", "model": "S系列", "color": "蓝色", "status": "报废"},
            {"plate_number": "京K01234", "brand": "曼", "model": "TGX", "color": "白色", "status": "可用"}
        ]
        
        vehicles = []
        for veh_data in vehicles_data:
            veh = Vehicle.query.filter_by(plate_number=veh_data["plate_number"]).first()
            if not veh:
                veh = Vehicle()
                veh.plate_number = veh_data["plate_number"]
                veh.brand = veh_data["brand"]
                veh.model = veh_data["model"]
                veh.color = veh_data["color"]
                veh.status = veh_data["status"]
                veh.purchase_date = random_date(date(2018, 1, 1), date(2023, 12, 31))
                veh.responsible_person_id = random.choice(users).id if users else None
                veh.insurance_expiry_date = date(2025, random.randint(1, 12), random.randint(1, 28))
                veh.last_maintenance_date = random_date(date(2023, 1, 1), date(2024, 12, 31))
                veh.next_maintenance_mileage = round(random.uniform(50000, 200000), 1)
                db.session.add(veh)
                db.session.commit()
            vehicles.append(veh)
        
        print(f"已添加/确认 {len(vehicles)} 辆车")
        
        # 8. 添加车辆使用记录
        usage_records = []
        for i in range(10):
            usage = VehicleUsageRecord.query.offset(i).first()
            if not usage:
                usage = VehicleUsageRecord()
                usage.vehicle_id = random.choice(vehicles).id
                usage.borrower_id = random.choice(users).id
                usage.borrow_time = datetime.now() - timedelta(days=random.randint(1, 30))
                usage.borrow_mileage = round(random.uniform(10000, 150000), 1)
                usage.purpose = random.choice(["送货", "提货", "出差", "维修", "其他"])
                usage.remarks = f"第{i+1}次用车记录"
                db.session.add(usage)
                db.session.commit()
            usage_records.append(usage)
        
        print(f"已添加/确认 {len(usage_records)} 条车辆使用记录")
        
        # 9. 添加化验数据
        assay_data = []
        for i in range(10):
            assay = AssayData.query.offset(i).first()
            if not assay:
                assay = AssayData()
                assay.sample_name = f"样品{i+1:03d}"
                assay.factory_id = random.choice(departments[:3]).id  # 从生产部门中选择
                assay.water_content = round(random.uniform(0.1, 5.0), 2)
                assay.zinc_content = round(random.uniform(40.0, 60.0), 2)
                assay.lead_content = round(random.uniform(0.1, 2.0), 2)
                assay.chlorine_content = round(random.uniform(0.01, 0.5), 2)
                assay.fluorine_content = round(random.uniform(0.01, 0.3), 2)
                assay.iron_content = round(random.uniform(1.0, 10.0), 2)
                assay.silicon_content = round(random.uniform(0.5, 5.0), 2)
                assay.sulfur_content = round(random.uniform(20.0, 40.0), 2)
                assay.remarks = f"第{i+1}号化验样品"
                assay.created_by = random.choice(users).id if users else None
                db.session.add(assay)
                db.session.commit()
            assay_data.append(assay)
        
        print(f"已添加/确认 {len(assay_data)} 条化验数据")
        
        # 10. 添加金属价格数据
        metal_prices = []
        metal_types = ["1#锌", "1#铅", "1#铜", "1#铝", "1#镍", "1#锡", "1#锑", "1#铋"]
        for i in range(10):
            price_date = date(2024, random.randint(1, 12), random.randint(1, 28))
            metal_type = random.choice(metal_types)
            
            # 检查是否已有相同日期和类型的记录
            price = MetalPrice.query.filter_by(quote_date=price_date, metal_type=metal_type).first()
            if not price:
                price = MetalPrice()
                price.metal_type = metal_type
                price.quote_date = price_date
                base_price = random.uniform(15000, 25000)
                price.high_price = round(base_price * random.uniform(1.01, 1.05), 2)
                price.low_price = round(base_price * random.uniform(0.95, 0.99), 2)
                price.average_price = round((price.high_price + price.low_price) / 2, 2)
                price.price_change = round(random.uniform(-500, 500), 2)
                db.session.add(price)
                db.session.commit()
            metal_prices.append(price)
        
        print(f"已添加/确认 {len(metal_prices)} 条金属价格数据")
        
        # 11. 添加物料交易记录
        transactions = []
        transaction_types = ["进厂", "出厂"]
        for i in range(10):
            trans = MaterialTransaction.query.offset(i).first()
            if not trans:
                trans = MaterialTransaction()
                trans.date = random_date(date(2024, 1, 1), date(2024, 12, 31))
                trans.customer = random.choice(customers).name
                trans.material_name = random.choice(materials).name
                trans.factory_id = random.choice(departments[:3]).id  # 从生产部门中选择
                trans.contract_number = f"CON{random.randint(1, 100):04d}"
                trans.transaction_type = random.choice(transaction_types)
                trans.packaging = random.choice(["散装", "袋装", "桶装", "箱装"])
                trans.vehicle_number = f"京{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000, 9999)}"
                trans.shipped_quantity = round(random.uniform(10, 1000), 2)
                trans.received_quantity = round(trans.shipped_quantity * random.uniform(0.95, 1.05), 2)
                trans.water_content = round(random.uniform(0.1, 5.0), 2)
                trans.zinc_content = round(random.uniform(40.0, 60.0), 2)
                trans.lead_content = round(random.uniform(0.1, 2.0), 2)
                trans.chlorine_content = round(random.uniform(0.01, 0.5), 2)
                trans.fluorine_content = round(random.uniform(0.01, 0.3), 2)
                trans.remarks = f"第{i+1}笔物料交易"
                trans.created_by = random.choice(users).id if users else None
                db.session.add(trans)
                db.session.commit()
            transactions.append(trans)
        
        print(f"已添加/确认 {len(transactions)} 条物料交易记录")
        
        # 12. 添加生产记录
        production_records = []
        for i in range(10):
            prod = ProductionRecord.query.offset(i).first()
            if not prod:
                prod = ProductionRecord()
                prod.date = random_date(date(2024, 1, 1), date(2024, 12, 31))
                prod.factory_id = random.choice(departments[:3]).id  # 从生产部门中选择
                prod.team_id = random.choice(departments[:3]).id  # 从生产部门中选择
                prod.recorder_id = random.choice(users).id
                prod.material_name = random.choice(materials).name
                prod.quantity = round(random.uniform(100, 10000), 2)
                prod.water_content = round(random.uniform(0.1, 5.0), 2)
                prod.zinc_content = round(random.uniform(40.0, 60.0), 2)
                prod.lead_content = round(random.uniform(0.1, 2.0), 2)
                prod.chlorine_content = round(random.uniform(0.01, 0.5), 2)
                prod.fluorine_content = round(random.uniform(0.01, 0.3), 2)
                prod.remarks = f"第{i+1}条生产记录"
                prod.created_by = random.choice(users).id if users else None
                db.session.add(prod)
                db.session.commit()
            production_records.append(prod)
        
        print(f"已添加/确认 {len(production_records)} 条生产记录")
        
        # 13. 添加通知数据
        notifications = []
        for i in range(10):
            notif = Notification.query.offset(i).first()
            if not notif:
                notif = Notification()
                notif.title = f"系统通知{i+1:02d}"
                notif.content = f"这是第{i+1}条系统通知的内容，用于测试通知功能。"
                notif.user_id = random.choice(users).id if users else None
                notif.is_read = random.choice([True, False])
                notif.created_at = datetime.now() - timedelta(days=random.randint(1, 30))
                db.session.add(notif)
                db.session.commit()
            notifications.append(notif)
        
        print(f"已添加/确认 {len(notifications)} 条通知")
        
        # 14. 添加文章分类
        categories_data = [
            {"name": "公司新闻", "description": "公司最新动态和新闻"},
            {"name": "行业资讯", "description": "行业相关信息和资讯"},
            {"name": "政策法规", "description": "相关政策法规信息"},
            {"name": "技术分享", "description": "技术交流和分享"},
            {"name": "员工风采", "description": "员工活动和风采展示"}
        ]
        
        categories = []
        for cat_data in categories_data:
            cat = ArticleCategory.query.filter_by(name=cat_data["name"]).first()
            if not cat:
                cat = ArticleCategory(**cat_data)
                db.session.add(cat)
                db.session.commit()
            categories.append(cat)
        
        print(f"已添加/确认 {len(categories)} 个文章分类")
        
        # 15. 添加文章数据
        articles = []
        for i in range(10):
            article = Article.query.offset(i).first()
            if not article:
                article = Article()
                article.title = f"测试文章{i+1:02d}"
                article.content = f"<p>这是第{i+1}篇测试文章的内容。文章内容可以包含HTML标签，用于展示富文本格式。</p><p>文章可以包含多个段落，用于详细介绍相关内容。</p>"
                article.summary = f"第{i+1}篇测试文章摘要"
                article.category_id = random.choice(categories).id
                article.author_id = random.choice(users).id
                article.status = random.choice(["draft", "published", "archived"])
                article.is_featured = random.choice([True, False])
                article.view_count = random.randint(0, 1000)
                article.created_at = datetime.now() - timedelta(days=random.randint(1, 30))
                article.updated_at = article.created_at
                if article.status == "published":
                    article.published_at = article.created_at
                db.session.add(article)
                db.session.commit()
            articles.append(article)
        
        print(f"已添加/确认 {len(articles)} 篇文章")
        
        # 提交所有更改
        db.session.commit()
        
        print("测试数据添加完成！")
        print("\n登录信息:")
        print("- 管理员账号: admin / admin123")
        print("- 普通用户账号: user001 / 123456 (到 user010)")
        print("\n数据统计:")
        print(f"- 部门: {len(departments)} 个")
        print(f"- 用户: {len(users)} 个")
        print(f"- 员工: {len(employees)} 个")
        print(f"- 物料: {len(materials)} 种")
        print(f"- 客户: {len(customers)} 个")
        print(f"- 合同: {len(contracts)} 份")
        print(f"- 车辆: {len(vehicles)} 辆")
        print(f"- 车辆使用记录: {len(usage_records)} 条")
        print(f"- 化验数据: {len(assay_data)} 条")
        print(f"- 金属价格: {len(metal_prices)} 条")
        print(f"- 物料交易记录: {len(transactions)} 条")
        print(f"- 生产记录: {len(production_records)} 条")
        print(f"- 通知: {len(notifications)} 条")
        print(f"- 文章分类: {len(categories)} 个")
        print(f"- 文章: {len(articles)} 篇")

if __name__ == '__main__':
    add_test_data()