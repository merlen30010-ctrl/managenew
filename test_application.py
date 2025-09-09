#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应聘功能测试程序
测试应聘信息提交和储备员工管理功能
"""

import requests
import json
from datetime import datetime, date
import time
import random

class ApplicationTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_application_page_access(self):
        """测试应聘页面访问"""
        print("\n=== 测试应聘页面访问 ===")
        try:
            response = self.session.get(f"{self.base_url}/application")
            if response.status_code == 200:
                print("✓ 应聘页面访问成功")
                return True
            else:
                print(f"✗ 应聘页面访问失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 应聘页面访问异常: {e}")
            return False
    
    def generate_test_data(self, index=1):
        """生成测试数据"""
        return {
            'name': f'测试应聘者{index}',
            'gender': random.choice(['男', '女']),
            'birth_date': '1995-06-15',
            'id_card': f'11010119950615{1000 + index:04d}',  # 生成唯一身份证号
            'phone': f'138{random.randint(10000000, 99999999)}',
            'education': random.choice(['高中', '中专', '大专', '本科']),
            'native_place': '北京市',
            'nationality': '汉族',
            'marital_status': random.choice(['未婚', '已婚']),
            'job_title': random.choice(['生产工人', '技术员', '质检员', '设备维修工', '仓库管理员']),
            'address': f'北京市朝阳区测试街道{index}号',
            'emergency_contact': f'紧急联系人{index}',
            'emergency_phone': f'139{random.randint(10000000, 99999999)}'
        }
    
    def submit_application(self, data):
        """提交应聘信息"""
        print(f"\n=== 提交应聘信息: {data['name']} ===")
        try:
            # 先访问应聘页面获取session
            self.session.get(f"{self.base_url}/application")
            
            # 提交应聘信息
            response = self.session.post(
                f"{self.base_url}/application/submit",
                data=data,
                allow_redirects=False
            )
            
            print(f"提交数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 302:  # 重定向表示成功
                print("✓ 应聘信息提交成功")
                return True
            elif response.status_code == 200:
                # 检查响应内容是否包含错误信息
                if '请填写所有必填项目' in response.text:
                    print("✗ 提交失败: 必填项目未填写完整")
                elif '该身份证号已存在' in response.text:
                    print("✗ 提交失败: 身份证号已存在")
                else:
                    print("✗ 提交失败: 未知错误")
                return False
            else:
                print(f"✗ 提交失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ 提交异常: {e}")
            return False
    
    def login_admin(self):
        """管理员登录"""
        print("\n=== 管理员登录 ===")
        try:
            # 获取登录页面
            response = self.session.get(f"{self.base_url}/auth/login")
            
            # 提交登录信息
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                allow_redirects=False
            )
            
            if response.status_code == 302:  # 重定向到dashboard
                print("✓ 管理员登录成功")
                return True
            else:
                print(f"✗ 管理员登录失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ 登录异常: {e}")
            return False
    
    def check_employee_list(self):
        """检查员工列表中的储备员工"""
        print("\n=== 检查员工列表 ===")
        try:
            response = self.session.get(f"{self.base_url}/employees")
            
            if response.status_code == 200:
                print("✓ 员工列表页面访问成功")
                
                # 检查页面内容
                if '储备' in response.text:
                    print("✓ 页面包含储备员工相关内容")
                    return True
                else:
                    print("? 页面未显示储备员工内容")
                    return False
            else:
                print(f"✗ 员工列表访问失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ 检查员工列表异常: {e}")
            return False
    
    def get_employee_api_data(self):
        """获取员工API数据"""
        print("\n=== 获取员工API数据 ===")
        try:
            response = self.session.get(f"{self.base_url}/api/employees")
            
            if response.status_code == 200:
                data = response.json()
                employee_data = data.get('data', {})
                total_count = employee_data.get('total', 0)
                items = employee_data.get('items', [])
                print(f"✓ 获取到 {total_count} 条员工记录")
                
                # 统计储备员工
                reserve_count = 0
                for employee in items:
                    if employee.get('employment_status') == '储备':
                        reserve_count += 1
                        print(f"  储备员工: {employee.get('name')} - 应聘职位: {employee.get('job_title')}")
                
                print(f"✓ 储备员工总数: {reserve_count}")
                return True
            else:
                print(f"✗ 获取员工数据失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ 获取员工数据异常: {e}")
            return False
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("\n" + "="*50)
        print("开始应聘功能综合测试")
        print("="*50)
        
        results = []
        
        # 1. 测试应聘页面访问
        results.append(self.test_application_page_access())
        
        # 2. 提交多个应聘信息
        for i in range(1, 4):  # 提交3个测试应聘
            test_data = self.generate_test_data(i)
            results.append(self.submit_application(test_data))
            time.sleep(1)  # 避免频率限制
        
        # 3. 管理员登录
        results.append(self.login_admin())
        
        # 4. 检查员工列表
        results.append(self.check_employee_list())
        
        # 5. 获取员工API数据
        results.append(self.get_employee_api_data())
        
        # 输出测试结果
        print("\n" + "="*50)
        print("测试结果汇总")
        print("="*50)
        
        success_count = sum(results)
        total_count = len(results)
        
        print(f"总测试项: {total_count}")
        print(f"成功项: {success_count}")
        print(f"失败项: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        if success_count == total_count:
            print("\n🎉 所有测试通过！应聘功能正常工作")
        else:
            print("\n⚠️  部分测试失败，请检查相关功能")
        
        return success_count == total_count

def main():
    """主函数"""
    print("应聘功能测试程序")
    print("确保服务器已启动在 http://127.0.0.1:5000")
    
    tester = ApplicationTester()
    
    try:
        tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生异常: {e}")

if __name__ == "__main__":
    main()