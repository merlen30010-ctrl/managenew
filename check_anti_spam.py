#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta

def check_anti_spam_status():
    """检查防刷机制状态"""
    
    # 日志文件路径
    log_file = 'instance/logs/submission_log.json'
    blacklist_file = 'instance/logs/ip_blacklist.json'
    
    print("=== 防刷机制状态检查 ===")
    
    # 检查提交日志
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        for ip, submissions in log_data.items():
            print(f"\nIP: {ip}")
            print(f"总提交次数: {len(submissions)}")
            
            # 计算1小时内的提交次数
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            recent_submissions = []
            for record in submissions:
                try:
                    timestamp = datetime.fromisoformat(record['timestamp'])
                    if timestamp > hour_ago:
                        recent_submissions.append(record)
                except ValueError:
                    continue
            
            print(f"1小时内提交次数: {len(recent_submissions)}")
            
            # 计算24小时内的提交次数
            day_ago = now - timedelta(hours=24)
            daily_submissions = []
            for record in submissions:
                try:
                    timestamp = datetime.fromisoformat(record['timestamp'])
                    if timestamp > day_ago:
                        daily_submissions.append(record)
                except ValueError:
                    continue
            
            print(f"24小时内提交次数: {len(daily_submissions)}")
            
            # 检查是否超过限制
            max_per_hour = 10
            max_per_day = 50
            
            if len(recent_submissions) >= max_per_hour:
                print(f"⚠️  1小时内提交次数已达上限({max_per_hour}次)")
            
            if len(daily_submissions) >= max_per_day:
                print(f"⚠️  24小时内提交次数已达上限({max_per_day}次)")
            
            # 显示最近的提交记录
            print("\n最近5次提交:")
            for record in submissions[-5:]:
                timestamp = record['timestamp']
                user_agent = record.get('user_agent', 'Unknown')
                print(f"  {timestamp} - {user_agent}")
    else:
        print("提交日志文件不存在")
    
    # 检查黑名单
    if os.path.exists(blacklist_file):
        with open(blacklist_file, 'r', encoding='utf-8') as f:
            blacklist_data = json.load(f)
        
        print(f"\n=== IP黑名单 ===")
        if blacklist_data:
            for ip, data in blacklist_data.items():
                print(f"IP: {ip}")
                print(f"原因: {data.get('reason', 'Unknown')}")
                print(f"添加时间: {data.get('added_at', 'Unknown')}")
                print(f"过期时间: {data.get('expires_at', 'Unknown')}")
        else:
            print("黑名单为空")
    else:
        print("\n=== IP黑名单 ===")
        print("黑名单文件不存在")

if __name__ == '__main__':
    check_anti_spam_status()