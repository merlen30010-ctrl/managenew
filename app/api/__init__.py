from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 导入API路由
from app.api import routes
from app.api import excel
from app.api import vehicle
from app.api import auth
from app.api import user
from app.api import material
from app.api import customer
from app.api import department
from app.api import contract
from app.api import assay_data
from app.api import material_transaction
from app.api import employee_document
from app.api import employee_reward_punishment