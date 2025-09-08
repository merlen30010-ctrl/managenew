#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的文章功能测试
"""

import os
import sys
import requests
import json

# 测试服务器地址
BASE_URL = 'http://127.0.0.1:5000'

def test_article_system():
    """测试文章系统基本功能"""
    print("开始测试文章系统...")
    
    # 测试主页访问
    try:
        response = requests.get(f'{BASE_URL}/')
        print(f"主页访问: {response.status_code}")
    except Exception as e:
        print(f"主页访问失败: {e}")
    
    # 测试API端点
    api_endpoints = [
        '/api/articles',
        '/api/article-categories'
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}')
            print(f"API {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"API {endpoint} 访问失败: {e}")
    
    # 测试文章页面（需要登录）
    try:
        response = requests.get(f'{BASE_URL}/articles')
        print(f"文章页面: {response.status_code} (预期302重定向到登录页)")
    except Exception as e:
        print(f"文章页面访问失败: {e}")
    
    print("文章系统测试完成")

if __name__ == '__main__':
    test_article_system()