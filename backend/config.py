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
    
    # 按业内习惯优先读取 SQLALCHEMY_DATABASE_URI，其次兼容 DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(INSTANCE_DIR, "app.db")}'
    
    @staticmethod
    def init_app(app):
        pass
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 连接池保持活跃，避免数据库空闲断链
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }
    # 上传目录使用绝对路径，默认放置在项目backend/uploads下
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'uploads')
    # 限制上传大小（默认16MB）
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = int(os.environ.get('JWT_EXPIRATION_DELTA', 3600))  # 默认1小时
    JWT_REFRESH_WINDOW = int(os.environ.get('JWT_REFRESH_WINDOW', 300))  # 默认5分钟刷新窗口
    
    # 会话与Cookie安全（生产环境建议置为True，并配合HTTPS）
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
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

    # CORS 允许的来源，逗号分隔，默认仅本地前端
    _cors_env = os.environ.get('CORS_ORIGINS', 'http://localhost:3000')
    CORS_ORIGINS = [o.strip() for o in _cors_env.split(',') if o.strip()]

    # JSON 输出配置
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

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