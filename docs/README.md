# 管理系统 (ManagePro)

一个基于Flask的企业级管理系统，提供用户管理、员工管理、物料管理、客户管理、部门管理等核心功能。

> **重要说明**: 项目的API文档存在编码问题，导致中文显示异常。我们已经创建了修正版本 `API文档_corrected.md`，建议查看该文档以获得准确的API接口信息。

## 📋 目录

- [系统概述](#系统概述)
- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [功能模块](#功能模块)
- [安装部署](#安装部署)
- [配置说明](#配置说明)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [测试](#测试)
- [部署](#部署)
- [维护](#维护)

## 🎯 系统概述

本系统是一个现代化的企业管理平台，采用前后端分离架构，支持多用户、多角色、权限控制等企业级功能。系统设计遵循RESTful API规范，具有良好的扩展性和维护性。

### 核心特性

- 🔐 **安全认证**: JWT Token + Session双重认证机制
- 👥 **权限管理**: 基于角色的权限控制(RBAC)
- 📊 **数据管理**: 完整的CRUD操作和数据统计
- 🔍 **搜索过滤**: 支持多条件搜索和分页
- 📱 **移动端支持**: 响应式设计，支持移动端访问
- 🛡️ **安全防护**: 防SQL注入、XSS攻击、CSRF保护
- 📈 **性能监控**: 查询监控、缓存服务、防刷机制
- 📄 **文档导出**: 支持Excel、PDF等格式导出

## 🛠️ 技术栈

### 后端技术

- **框架**: Flask 2.x
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.x
- **认证**: JWT (JSON Web Token)
- **权限**: 基于角色的访问控制 (RBAC)
- **缓存**: Redis (可选)
- **文件处理**: Werkzeug FileStorage
- **数据验证**: Flask-WTF
- **数据库迁移**: Flask-Migrate
- **跨域支持**: Flask-CORS
- **任务队列**: Celery (可选)
- **文档生成**: 支持Excel、PDF导出

## 🏗️ 系统架构

```
managepro/
├── backend/                 # 后端应用
│   ├── app/                # Flask应用主目录
│   │   ├── api/           # API接口层
│   │   ├── models/        # 数据模型层
│   │   ├── views/         # 视图层(Web页面)
│   │   ├── utils/         # 工具类
│   │   └── templates/     # 模板文件
│   ├── config.py          # 配置文件
│   ├── run.py            # 应用启动文件
│   └── init_db.py        # 数据库初始化
├── docs/                   # 文档目录
├── tests/                  # 测试文件
└── scripts/               # 部署脚本
```

### 分层架构

1. **API层** (`app/api/`): RESTful API接口，处理HTTP请求
2. **业务逻辑层** (`app/models/`): 数据模型和业务逻辑
3. **数据访问层** (`SQLAlchemy ORM`): 数据库操作抽象
4. **工具层** (`app/utils/`): 通用工具和服务

## 📦 功能模块

### 1. 用户管理模块
- ✅ 用户注册、登录、登出
- ✅ 用户信息管理(CRUD)
- ✅ 密码修改和重置
- ✅ 用户状态管理(激活/禁用)
- ✅ 超级管理员权限

### 2. 员工管理模块
- ✅ 员工档案管理
- ✅ 员工工号自动生成
- ✅ 部门关联管理
- ✅ 员工头像上传
- ✅ 在职状态管理
- ✅ 员工统计分析

### 3. 权限管理模块
- ✅ 角色定义和管理
- ✅ 权限分配和控制
- ✅ 基于装饰器的权限验证
- ✅ 动态权限检查

### 4. 部门管理模块
- ✅ 部门层级结构
- ✅ 部门信息维护
- ✅ 员工部门关联

### 5. 物料管理模块
- ✅ 物料基础信息管理
- ✅ 物料分类(原料/辅料/产品)
- ✅ 物料代码管理
- ✅ 物料事务记录

### 6. 客户管理模块
- ✅ 客户基础信息
- ✅ 客户联系方式
- ✅ 客户关系维护

### 7. 合同管理模块
- ✅ 合同基础信息
- ✅ 合同文件管理
- ✅ 合同状态跟踪

### 8. 生产管理模块
- ✅ 生产记录管理
- ✅ 生产数据统计
- ✅ 化验数据管理
- ✅ 质量控制记录

### 9. 车辆管理模块
- ✅ 车辆档案管理
- ✅ 车辆使用记录
- ✅ 保养记录管理
- ✅ 保险信息管理

### 10. 员工证件管理模块
- ✅ 证件信息管理
- ✅ 证件类型管理
- ✅ 证件到期提醒
- ✅ 证件文件上传

### 11. 员工奖惩管理模块
- ✅ 奖惩记录管理
- ✅ 奖惩类型管理
- ✅ 奖惩统计分析
- ✅ 奖惩审批流程

### 12. 化验数据模块
- ✅ 化验数据录入
- ✅ 化验报告管理
- ✅ 数据统计分析
- ✅ 化验标准管理

### 13. 附件管理模块
- ✅ 文件上传下载
- ✅ 文件类型验证
- ✅ 文件存储管理
- ✅ 文件关联管理

### 14. 金属价格管理模块
- ✅ 金属价格录入
- ✅ 价格历史记录
- ✅ 价格趋势分析
- ✅ 价格预警功能

### 15. 通知管理模块
- ✅ 系统通知发送
- ✅ 通知状态跟踪
- ✅ 通知分类管理
- ✅ 批量通知处理

### 16. 考试结果管理模块
- ✅ 考试结果录入
- ✅ 考试成绩统计
- ✅ 考试记录查询
- ✅ 成绩分析报告

### 17. 文章管理模块
- ✅ 文章发布和编辑
- ✅ 文章分类管理
- ✅ 文章附件处理
- ✅ 文章状态管理

### 18. 应用管理模块
- ✅ 应用配置管理
- ✅ 应用权限控制
- ✅ 应用状态监控
- ✅ 应用日志记录

### 19. 超级用户管理模块
- ✅ 超级用户权限
- ✅ 系统级操作
- ✅ 全局配置管理
- ✅ 系统维护功能

### 20. 数据导入导出模块
- ✅ Excel数据导入
- ✅ 多格式数据导出
- ✅ 批量数据处理
- ✅ 数据验证和清洗

### 21. 系统统计模块
- ✅ 概览统计信息
- ✅ 数据趋势分析
- ✅ 业务指标监控
- ✅ 报表生成功能

### 22. 系统配置模块
- ✅ 系统参数配置
- ✅ 配置项管理
- ✅ 配置历史记录
- ✅ 配置备份恢复

### 23. 系统日志模块
- ✅ 操作日志记录
- ✅ 日志查询分析
- ✅ 日志清理功能
- ✅ 日志导出功能

### 24. 数据备份恢复模块
- ✅ 数据库备份
- ✅ 数据恢复功能
- ✅ 备份任务调度
- ✅ 备份文件管理

## 🚀 安装部署

### 环境要求

- Python 3.8+
- pip 20.0+
- SQLite 3.0+ (开发环境)
- Redis 6.0+ (可选，用于缓存)

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd managepro
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息
```

5. **初始化数据库**
```bash
# 初始化数据库迁移
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 创建超级用户
flask create-superuser
```

6. **启动应用**
```bash
python run.py
```

应用将在 `http://localhost:5000` 启动

### Docker部署 (推荐)

```bash
# 构建镜像
docker build -t managepro .

# 运行容器
docker run -p 5000:5000 managepro
```

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件:

```env
# 基础配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///managepro.db
# 生产环境使用PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost/managepro

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24小时

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=10485760  # 10MB

# Redis配置(可选)
REDIS_URL=redis://localhost:6379/0

# 邮件配置(可选)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password

# 安全配置
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/managepro.log
```

### 配置类说明

- **DevelopmentConfig**: 开发环境配置
- **ProductionConfig**: 生产环境配置
- **Config**: 基础配置类

## 📚 API文档

详细的API文档请参考: [docs/API文档_corrected.md](docs/API文档_corrected.md)

**注意**: 原始API文档存在编码问题，建议使用修正后的版本以获得正确的接口信息。

### API概览

- **认证接口**: `/api/auth/login`, `/api/auth/logout`, `/api/auth/refresh`
- **用户管理**: `/api/users/*`
- **员工管理**: `/api/employees/*`
- **部门管理**: `/api/departments/*`
- **物料管理**: `/api/materials/*`
- **客户管理**: `/api/customers/*`
- **合同管理**: `/api/contracts/*`
- **物料事务**: `/api/material-transactions/*`
- **生产记录**: `/api/production-records/*`
- **车辆管理**: `/api/vehicles/*`
- **员工证件**: `/api/employee-certificates/*`
- **员工奖惩**: `/api/employee-rewards/*`
- **化验数据**: `/api/lab-data/*`
- **附件管理**: `/api/attachments/*`
- **金属价格**: `/api/metal-prices/*`
- **通知管理**: `/api/notifications/*`
- **考试结果**: `/api/exam-results/*`
- **文章管理**: `/api/articles/*`
- **文章分类**: `/api/article-categories/*`
- **文章附件**: `/api/article-attachments/*`
- **权限管理**: `/api/permissions/*`
- **角色管理**: `/api/roles/*`
- **应用管理**: `/api/applications/*`
- **超级用户**: `/api/superuser/*`
- **数据导入导出**: `/api/import-export/*`
- **系统统计**: `/api/statistics/*`
- **系统配置**: `/api/system-config/*`
- **系统日志**: `/api/system-logs/*`
- **数据备份**: `/api/backup/*`

### 认证方式

系统采用JWT Token认证方式:
1. **JWT Token认证**: 适用于所有API调用
2. **Token刷新机制**: 支持Token自动刷新
3. **权限验证**: 基于角色的权限控制
4. **安全保护**: 防止Token泄露和重放攻击

### 请求格式

所有API请求都需要在请求头中携带JWT Token：

```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

### 响应格式

统一的JSON响应格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## 👨‍💻 开发指南

### 代码规范

1. **Python代码规范**: 遵循PEP 8
2. **API设计**: 遵循RESTful规范
3. **数据库设计**: 遵循第三范式
4. **错误处理**: 统一错误响应格式

### 添加新功能

1. **创建数据模型** (`app/models/`)
2. **创建API接口** (`app/api/`)
3. **添加权限控制** (使用装饰器)
4. **编写测试用例** (`tests/`)
5. **更新API文档**

### 数据库迁移

```bash
# 生成迁移文件
flask db migrate -m "描述信息"

# 执行迁移
flask db upgrade
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_api.py

# 生成覆盖率报告
python -m pytest --cov=app tests/
```

### 测试覆盖

- ✅ API接口测试
- ✅ 数据模型测试
- ✅ 权限验证测试
- ✅ 安全性测试
- ✅ JWT认证测试

## 🚀 部署

### 生产环境部署

1. **配置生产环境变量**
2. **使用PostgreSQL数据库**
3. **配置Redis缓存**
4. **使用Gunicorn作为WSGI服务器**
5. **配置Nginx反向代理**

### 部署脚本

- `scripts/deploy_linux.sh`: Linux部署脚本
- `scripts/factory-manager.service`: systemd服务配置
- `scripts/backup_system.ps1`: 数据备份脚本
- `scripts/restore_system.ps1`: 数据恢复脚本

## 🔧 维护

### 日常维护

1. **数据库备份**: 定期备份数据库
2. **日志监控**: 监控应用日志和错误
3. **性能监控**: 监控查询性能和响应时间
4. **安全更新**: 定期更新依赖包

### 监控指标

- 响应时间
- 错误率
- 数据库查询性能
- 内存使用率
- 磁盘空间

### 故障排查

1. **查看日志文件**
2. **检查数据库连接**
3. **验证配置文件**
4. **检查权限设置**

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系:

- 项目Issues: [GitHub Issues]()
- 邮箱: [your-email@example.com]()

---

**注意**: 本系统设计用于中小型企业(用户数不超过200人)，无需考虑高并发和高可用问题。系统采用模块化设计，功能单一，避免模块间高耦合。