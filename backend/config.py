import os

# 获取项目根目录
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    
    # 构建instance目录下的数据库路径
    INSTANCE_DIR = os.path.join(basedir, 'instance')
    
    # 确保instance目录存在
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(INSTANCE_DIR, "app.db")}'
    
    @staticmethod
    def init_app(app):
        pass
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'  # 添加上传目录配置
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = int(os.environ.get('JWT_EXPIRATION_DELTA', 3600))  # 默认1小时
    JWT_REFRESH_WINDOW = int(os.environ.get('JWT_REFRESH_WINDOW', 300))  # 默认5分钟刷新窗口
    
    # 会话超时配置
    SESSION_TIMEOUT_MINUTES = 30  # 30分钟无活动自动超时
    SESSION_CLEANUP_INTERVAL = 300  # 5分钟清理一次过期会话
    
    # Token黑名单配置
    JWT_BLACKLIST_FILE = 'token_blacklist.json'  # 黑名单文件名
    JWT_BLACKLIST_CLEANUP_DAYS = 7  # 黑名单条目保留天数
    
    # Redis缓存配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 查询监控配置
    ENABLE_QUERY_MONITORING = os.environ.get('ENABLE_QUERY_MONITORING', 'false').lower() == 'true'
    SLOW_QUERY_THRESHOLD = float(os.environ.get('SLOW_QUERY_THRESHOLD', '1.0'))

class DevelopmentConfig(Config):
    DEBUG = True
    ENABLE_QUERY_MONITORING = True
    SLOW_QUERY_THRESHOLD = 0.5  # 开发环境使用更严格的阈值

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}