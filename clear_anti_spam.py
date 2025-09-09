#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta

def clear_anti_spam_logs():
    """清理防刷机制日志"""
    
    # 日志文件路径
    log_file = 'instance/logs/submission_log.json'
    blacklist_file = 'instance/logs/ip_blacklist.json'
    
    print("=== 清理防刷机制日志 ===")
    
    # 清理提交日志
    if os.path.exists(log_file):
        print(f"删除提交日志文件: {log_file}")
        os.remove(log_file)
    else:
        print("提交日志文件不存在")
    
    # 清理黑名单
    if os.path.exists(blacklist_file):
        print(f"删除黑名单文件: {blacklist_file}")
        os.remove(blacklist_file)
    else:
        print("黑名单文件不存在")
    
    print("\n✅ 防刷机制日志已清理完成")
    print("现在可以重新提交应聘信息了")

if __name__ == '__main__':
    clear_anti_spam_logs()