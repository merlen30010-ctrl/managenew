#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def check_db_config():
    """检查数据库配置"""
    app = create_app()
    
    with app.app_context():
        print(f"数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"实例目录: {app.instance_path}")
        print(f"项目根目录: {app.root_path}")
        
        # 检查环境变量
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            print(f"环境变量DATABASE_URL: {database_url}")
        else:
            print("环境变量DATABASE_URL未设置")
            
        # 检查实际数据库文件路径
        from app import db
        engine_url = str(db.engine.url)
        print(f"实际数据库引擎URL: {engine_url}")

if __name__ == '__main__':
    check_db_config()