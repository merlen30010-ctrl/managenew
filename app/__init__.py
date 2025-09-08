from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
import os
from datetime import datetime

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
migrate = Migrate()

# 导入缓存服务和查询监控
from app.utils.cache_service import cache_service
from app.utils.query_monitor import query_monitor

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    cache_service.init_app(app)
    query_monitor.init_app(app)
    CORS(app)
    
    login_manager.login_view = 'auth.login'
    
    # 配置CORS
    CORS(app, origins=['http://localhost:3000'], supports_credentials=True)
    
    # 用户加载回调函数
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.material import material_bp
    from app.views.customer import customer_bp
    from app.views.department import department_bp
    from app.views.contract import contract_bp
    from app.views.permission import permission_bp
    from app.views.query_monitor import query_monitor_bp
    from app.views.attachment import attachment_bp
    from app.views.assay_data import assay_data_bp
    from app.views.assay_attachment import assay_attachment_bp
    from app.views.excel import excel_bp
    from app.views.material_transaction import material_transaction_bp
    from app.views.production_record import production_record_bp
    from app.views.metal_price import metal_price_bp
    from app.views.vehicle import vehicle_bp
    from app.views.employee import employee_view_bp
    from app.views.notification import notification_bp
    from app.api import api_bp
    from app.api.auth import api_auth_bp
    from app.api.user import api_user_bp
    from app.api.material import api_material_bp
    from app.api.customer import api_customer_bp
    from app.api.department import api_department_bp
    from app.api.contract import api_contract_bp
    from app.api.assay_data import api_assay_data_bp
    from app.api.material_transaction import api_material_transaction_bp
    from app.api.metal_price import api_metal_price_bp
    from app.api.employee import employee_bp
    from app.api.notification import notification_bp as api_notification_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(material_bp, url_prefix='/materials')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(department_bp, url_prefix='/departments')
    app.register_blueprint(contract_bp, url_prefix='/contracts')
    app.register_blueprint(permission_bp, url_prefix='/permissions')
    app.register_blueprint(query_monitor_bp, url_prefix='/query_monitor')
    app.register_blueprint(attachment_bp)
    app.register_blueprint(assay_data_bp)
    app.register_blueprint(assay_attachment_bp)
    app.register_blueprint(excel_bp)
    app.register_blueprint(material_transaction_bp, url_prefix='/material-transactions')
    app.register_blueprint(production_record_bp, url_prefix='/production-records')
    app.register_blueprint(metal_price_bp, url_prefix='/metal-prices')
    app.register_blueprint(vehicle_bp, url_prefix='/vehicles')
    app.register_blueprint(employee_view_bp, url_prefix='/employees')
    app.register_blueprint(notification_bp, url_prefix='/notification')
    # 注册API蓝图
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(api_user_bp)
    app.register_blueprint(api_material_bp)
    app.register_blueprint(api_customer_bp)
    app.register_blueprint(api_department_bp)
    app.register_blueprint(api_contract_bp)
    app.register_blueprint(api_assay_data_bp)
    app.register_blueprint(api_material_transaction_bp)
    app.register_blueprint(api_metal_price_bp)
    app.register_blueprint(employee_bp, url_prefix='/api')
    app.register_blueprint(api_notification_bp, url_prefix='/api')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 设置缓存失效钩子
    with app.app_context():
        from app.utils.cache_hooks import setup_cache_invalidation_hooks
        setup_cache_invalidation_hooks()
    
    # 初始化会话管理器和黑名单管理器
    from app.utils import init_session_manager, cleanup_session_manager
    from app.utils import init_blacklist_manager, cleanup_blacklist_manager
    
    init_session_manager(app)
    init_blacklist_manager(app)
    
    # 注册应用关闭时的清理函数
    import atexit
    atexit.register(cleanup_session_manager)
    atexit.register(cleanup_blacklist_manager)
    
    return app