from functools import wraps
from flask import request, flash, redirect, url_for, current_app
from datetime import datetime, timedelta
import hashlib
import json
import os

class AntiSpamManager:
    """防刷机制管理器"""
    
    def __init__(self, app=None):
        self.app = app
        self.submission_log_file = 'submission_log.json'
        self.ip_blacklist_file = 'ip_blacklist.json'
        
        # 配置参数
        self.max_submissions_per_hour = 10  # 每小时最大提交次数
        self.max_submissions_per_day = 50  # 每天最大提交次数
        self.blacklist_threshold = 100  # 触发黑名单的提交次数
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        self.app = app
        
        # 确保日志目录存在
        log_dir = os.path.join(app.instance_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        self.submission_log_file = os.path.join(log_dir, 'submission_log.json')
        self.ip_blacklist_file = os.path.join(log_dir, 'ip_blacklist.json')
    
    def get_client_ip(self):
        """获取客户端IP地址"""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            return request.environ['REMOTE_ADDR']
        else:
            return request.environ['HTTP_X_FORWARDED_FOR']
    
    def load_submission_log(self):
        """加载提交日志"""
        try:
            if os.path.exists(self.submission_log_file):
                with open(self.submission_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            current_app.logger.error(f'加载提交日志失败: {str(e)}')
        return {}
    
    def save_submission_log(self, log_data):
        """保存提交日志"""
        try:
            with open(self.submission_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            current_app.logger.error(f'保存提交日志失败: {str(e)}')
    
    def load_ip_blacklist(self):
        """加载IP黑名单"""
        try:
            if os.path.exists(self.ip_blacklist_file):
                with open(self.ip_blacklist_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            current_app.logger.error(f'加载IP黑名单失败: {str(e)}')
        return {}
    
    def save_ip_blacklist(self, blacklist_data):
        """保存IP黑名单"""
        try:
            with open(self.ip_blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(blacklist_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            current_app.logger.error(f'保存IP黑名单失败: {str(e)}')
    
    def is_ip_blacklisted(self, ip):
        """检查IP是否在黑名单中"""
        blacklist = self.load_ip_blacklist()
        return ip in blacklist
    
    def add_to_blacklist(self, ip, reason='频繁提交'):
        """将IP添加到黑名单"""
        blacklist = self.load_ip_blacklist()
        blacklist[ip] = {
            'reason': reason,
            'added_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()  # 24小时后自动解除
        }
        self.save_ip_blacklist(blacklist)
        current_app.logger.warning(f'IP {ip} 已被加入黑名单: {reason}')
    
    def clean_expired_blacklist(self):
        """清理过期的黑名单记录"""
        blacklist = self.load_ip_blacklist()
        now = datetime.now()
        
        expired_ips = []
        for ip, data in blacklist.items():
            try:
                expires_at = datetime.fromisoformat(data['expires_at'])
                if now > expires_at:
                    expired_ips.append(ip)
            except (KeyError, ValueError):
                expired_ips.append(ip)  # 无效记录也删除
        
        for ip in expired_ips:
            del blacklist[ip]
        
        if expired_ips:
            self.save_ip_blacklist(blacklist)
            current_app.logger.info(f'清理了 {len(expired_ips)} 个过期的黑名单记录')
    
    def record_submission(self, ip, form_data=None):
        """记录提交行为"""
        log_data = self.load_submission_log()
        now = datetime.now()
        
        if ip not in log_data:
            log_data[ip] = []
        
        # 添加提交记录
        submission_record = {
            'timestamp': now.isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'form_hash': self._hash_form_data(form_data) if form_data else None
        }
        
        log_data[ip].append(submission_record)
        
        # 清理旧记录（保留最近7天）
        cutoff_time = now - timedelta(days=7)
        log_data[ip] = [
            record for record in log_data[ip]
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]
        
        self.save_submission_log(log_data)
        
        # 检查是否需要加入黑名单
        if len(log_data[ip]) >= self.blacklist_threshold:
            self.add_to_blacklist(ip, f'24小时内提交次数过多({len(log_data[ip])}次)')
    
    def _hash_form_data(self, form_data):
        """对表单数据进行哈希，用于检测重复提交"""
        if not form_data:
            return None
        
        # 提取关键字段进行哈希
        key_fields = ['name', 'id_card', 'phone']
        hash_string = ''.join([str(form_data.get(field, '')) for field in key_fields])
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    def check_submission_limit(self, ip):
        """检查提交频率限制"""
        # 先清理过期黑名单
        self.clean_expired_blacklist()
        
        # 检查IP是否在黑名单中
        if self.is_ip_blacklisted(ip):
            return False, '您的IP地址已被暂时限制，请24小时后再试'
        
        log_data = self.load_submission_log()
        if ip not in log_data:
            return True, ''
        
        now = datetime.now()
        submissions = log_data[ip]
        
        # 检查1小时内的提交次数
        hour_ago = now - timedelta(hours=1)
        recent_submissions = [
            record for record in submissions
            if datetime.fromisoformat(record['timestamp']) > hour_ago
        ]
        
        if len(recent_submissions) >= self.max_submissions_per_hour:
            return False, f'您在1小时内的提交次数已达上限({self.max_submissions_per_hour}次)，请稍后再试'
        
        # 检查24小时内的提交次数
        day_ago = now - timedelta(hours=24)
        daily_submissions = [
            record for record in submissions
            if datetime.fromisoformat(record['timestamp']) > day_ago
        ]
        
        if len(daily_submissions) >= self.max_submissions_per_day:
            return False, f'您在24小时内的提交次数已达上限({self.max_submissions_per_day}次)，请明天再试'
        
        return True, ''
    
    def check_duplicate_submission(self, ip, form_data):
        """检查重复提交"""
        if not form_data:
            return True, ''
        
        form_hash = self._hash_form_data(form_data)
        if not form_hash:
            return True, ''
        
        log_data = self.load_submission_log()
        if ip not in log_data:
            return True, ''
        
        # 检查最近1小时内是否有相同的提交
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        for record in log_data[ip]:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if (record_time > hour_ago and 
                    record.get('form_hash') == form_hash):
                    return False, '检测到重复提交，请不要重复提交相同信息'
            except ValueError:
                continue
        
        return True, ''

# 全局实例
anti_spam = AntiSpamManager()

def anti_spam_required(f):
    """防刷装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = anti_spam.get_client_ip()
        
        # 检查提交频率限制
        is_allowed, message = anti_spam.check_submission_limit(ip)
        if not is_allowed:
            flash(message, 'error')
            return redirect(url_for('main.application'))
        
        # 对于POST请求，检查重复提交
        if request.method == 'POST':
            is_unique, message = anti_spam.check_duplicate_submission(ip, request.form.to_dict())
            if not is_unique:
                flash(message, 'error')
                return redirect(url_for('main.application'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def record_submission_attempt(ip, form_data=None):
    """记录提交尝试"""
    anti_spam.record_submission(ip, form_data)