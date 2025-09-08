# 管理系统 API 接口文档

## 概述

本文档描述了管理系统的RESTful API接口，包括用户管理、物料管理、客户管理、部门管理、合同管理、化验数据、附件管理、金属价格、车辆管理等核心功能模块的API接口。

### 基础信息

- **基础URL**: `http://localhost:5000/api`
- **API版本**: v1.0
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: Session + Token

### 通用响应格式

#### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

#### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

### HTTP状态码

- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权/认证失败
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误

---

## 认证接口

### 用户登录

**接口地址**: `POST /api/login`

**请求参数**:
```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "dummy_token",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "name": "管理员"
    }
  }
}
```

### 用户注册

**接口地址**: `POST /api/register`

**请求参数**:
```json
{
  "username": "用户名",
  "email": "邮箱地址",
  "password": "密码",
  "name": "真实姓名（可选）"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 2,
      "username": "newuser",
      "email": "newuser@example.com",
      "name": "新用户"
    }
  }
}
```

### 用户登出

**接口地址**: `POST /api/logout`

**权限要求**: 需要登录

**响应示例**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

---

## 用户管理接口

### 获取当前用户信息

**接口地址**: `GET /api/users/me`

**权限要求**: 需要登录

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "name": "管理员",
    "roles": ["管理员"],
    "departments": ["总部"]
  }
}
```

### 获取用户列表

**接口地址**: `GET /api/users`

**权限要求**: `user_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "name": "管理员"
  },
  {
    "id": 2,
    "username": "user1",
    "email": "user1@example.com",
    "name": "用户1"
  }
]
```

### 获取单个用户信息

**接口地址**: `GET /api/users/{user_id}`

**权限要求**: `user_read`

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "name": "管理员"
}
```

### 创建用户

**接口地址**: `POST /api/users`

**权限要求**: `user_create`

**请求参数**:
```json
{
  "username": "用户名",
  "email": "邮箱地址",
  "name": "真实姓名（可选）",
  "phone": "电话号码（可选）",
  "password": "密码（可选）"
}
```

### 更新用户信息

**接口地址**: `PUT /api/users/{user_id}`

**权限要求**: `user_update`

**请求参数**:
```json
{
  "username": "新用户名（可选）",
  "email": "新邮箱（可选）",
  "name": "新姓名（可选）",
  "phone": "新电话（可选）",
  "password": "新密码（可选）"
}
```

### 删除用户

**接口地址**: `DELETE /api/users/{user_id}`

**权限要求**: `user_delete`

**响应示例**:
```json
{
  "message": "用户删除成功"
}
```

---

## 物料管理接口

### 获取物料列表

**接口地址**: `GET /api/materials`

**权限要求**: `material_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "锌精矿",
    "code": "ZN001",
    "full_name": "锌精矿原料",
    "purpose": "原料"
  }
]
```

### 获取单个物料信息

**接口地址**: `GET /api/materials/{material_id}`

**权限要求**: `material_read`

### 创建物料

**接口地址**: `POST /api/materials`

**权限要求**: `material_create`

**请求参数**:
```json
{
  "name": "物料名称",
  "code": "物料代码",
  "full_name": "物料全称（可选）",
  "purpose": "用途（原料/辅料/产品/其他）"
}
```

### 更新物料信息

**接口地址**: `PUT /api/materials/{material_id}`

**权限要求**: `material_update`

### 删除物料

**接口地址**: `DELETE /api/materials/{material_id}`

**权限要求**: `material_delete`

---

## 客户管理接口

### 获取客户列表

**接口地址**: `GET /api/customers`

**权限要求**: `customer_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "客户A",
    "code": "CUS001",
    "full_name": "客户A有限公司",
    "customer_type": "产品采购",
    "phone": "13800138000",
    "address": "北京市朝阳区"
  }
]
```

### 获取单个客户信息

**接口地址**: `GET /api/customers/{customer_id}`

**权限要求**: `customer_read`

### 创建客户

**接口地址**: `POST /api/customers`

**权限要求**: `customer_create`

**请求参数**:
```json
{
  "name": "客户名称",
  "code": "客户代码",
  "full_name": "客户全称（可选）",
  "customer_type": "客户类型（原料供应/产品采购/辅料供应/其他）",
  "phone": "联系电话（可选）",
  "address": "地址（可选）"
}
```

### 更新客户信息

**接口地址**: `PUT /api/customers/{customer_id}`

**权限要求**: `customer_update`

### 删除客户

**接口地址**: `DELETE /api/customers/{customer_id}`

**权限要求**: `customer_delete`

---

## 部门管理接口

### 获取部门列表

**接口地址**: `GET /api/departments`

**权限要求**: `department_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "一分厂",
    "short_name": "一厂",
    "full_name": "第一分厂",
    "level": 1,
    "parent_id": null,
    "phone": "010-12345678"
  }
]
```

### 获取单个部门信息

**接口地址**: `GET /api/departments/{department_id}`

**权限要求**: `department_read`

---

## 合同管理接口

### 获取合同列表

**接口地址**: `GET /api/contracts`

**权限要求**: `contract_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "contract_type": "产品销售",
    "contract_number": "CON2024001",
    "customer_id": 1,
    "material_id": 1,
    "factory_id": 1,
    "responsible_id": 1,
    "sign_date": "2024-01-01",
    "expiry_date": "2024-12-31",
    "tax_rate": 0.13,
    "pricing_method": "weight",
    "coefficient": 1.0,
    "status": "执行"
  }
]
```

---

## 化验数据接口

### 获取化验数据列表

**接口地址**: `GET /api/assay-data`

**权限要求**: `assay_data_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "sample_name": "锌精矿样品001",
    "factory_id": 1,
    "water_content": 8.5,
    "zinc_content": 55.2,
    "lead_content": 2.1,
    "chlorine_content": 0.05,
    "fluorine_content": 0.02,
    "iron_content": 6.8,
    "silicon_content": 3.2,
    "sulfur_content": 32.1,
    "high_heat": null,
    "low_heat": null,
    "silver_content": 120.5,
    "recovery_rate": 95.2,
    "remarks": "正常样品",
    "created_by": 1,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

---

## 附件管理接口

### 上传附件

**接口地址**: `POST /api/attachments`

**权限要求**: `attachment_create`

**请求类型**: `multipart/form-data`

**请求参数**:
- `file` (file): 要上传的文件
- `related_type` (string): 关联对象类型
- `related_id` (string): 关联对象ID
- `naming_rule` (string): 命名规则（可选，默认为default）

**响应示例**:
```json
{
  "success": true,
  "message": "文件上传成功",
  "data": {
    "id": 1,
    "file_path": "/uploads/contracts/contract_1_file.pdf",
    "original_name": "合同文件.pdf",
    "file_type": "pdf",
    "file_size": 1024000
  }
}
```

### 下载附件

**接口地址**: `GET /api/attachments/{attachment_id}/download`

**权限要求**: `attachment_read`

**响应**: 文件流

### 获取附件列表

**接口地址**: `GET /api/attachments/{related_type}/{related_id}`

**权限要求**: `attachment_read`

**路径参数**:
- `related_type` (string): 关联对象类型
- `related_id` (integer): 关联对象ID

**响应示例**:
```json
{
  "attachments": [
    {
      "id": 1,
      "related_type": "contract",
      "related_id": 1,
      "file_path": "/uploads/contracts/contract_1_file.pdf",
      "original_name": "合同文件.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## 金属价格接口

### 获取金属价格列表

**接口地址**: `GET /api/metal-prices`

**权限要求**: `metal_price_read`

**查询参数**:
- `metal_type` (string): 金属类型（可选）
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）

**响应示例**:
```json
{
  "prices": [
    {
      "id": 1,
      "metal_type": "1#锌",
      "quote_date": "2024-01-15",
      "high_price": 22500.0,
      "low_price": 22200.0,
      "average_price": 22350.0,
      "price_change": 150.0,
      "created_at": "2024-01-15 09:00:00",
      "updated_at": "2024-01-15 09:00:00"
    }
  ],
  "total": 100,
  "pages": 10,
  "current_page": 1
}
```



## 数据模型

### User（用户）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 用户ID | 主键，自增 |
| username | String(64) | 用户名 | 唯一，索引 |
| email | String(120) | 邮箱 | 唯一，索引 |
| password_hash | String(128) | 密码哈希 | 不可为空 |
| name | String(64) | 真实姓名 | 可为空 |
| phone | String(20) | 电话号码 | 可为空 |
| is_active | Boolean | 是否激活 | 默认True |
| created_at | DateTime | 创建时间 | 默认当前时间 |

### Material（物料）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 物料ID | 主键，自增 |
| name | String(100) | 物料名称 | 不可为空 |
| code | String(50) | 物料代码 | 唯一，不可为空 |
| full_name | String(200) | 物料全称 | 可为空 |
| purpose | String(20) | 用途 | 原料/辅料/产品/其他 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Customer（客户）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 客户ID | 主键，自增 |
| name | String(100) | 客户名称 | 不可为空 |
| code | String(50) | 客户代码 | 唯一，不可为空 |
| full_name | String(200) | 客户全称 | 可为空 |
| customer_type | String(20) | 客户类型 | 原料供应/产品采购/辅料供应/其他 |
| phone | String(20) | 联系电话 | 可为空 |
| address | String(200) | 地址 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Department（部门）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 部门ID | 主键，自增 |
| name | String(100) | 部门名称 | 不可为空 |
| short_name | String(50) | 部门简称 | 可为空 |
| full_name | String(200) | 部门全称 | 可为空 |
| level | Integer | 级别 | 1为分厂，2为部门 |
| parent_id | Integer | 父级部门ID | 外键，可为空 |
| phone | String(20) | 联系电话 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Contract（合同）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 合同ID | 主键，自增 |
| contract_type | String(20) | 合同类型 | 原料采购/辅料采购/产品销售/其他 |
| contract_number | String(50) | 合同编号 | 唯一，不可为空 |
| customer_id | Integer | 客户ID | 外键 |
| material_id | Integer | 物料ID | 外键 |
| factory_id | Integer | 分厂ID | 外键 |
| responsible_id | Integer | 负责人ID | 外键 |
| sign_date | Date | 签订日期 | 可为空 |
| expiry_date | Date | 到期日期 | 可为空 |
| tax_rate | Float | 税率 | 默认0.0 |
| pricing_method | String(20) | 计价方式 | weight/content/processing/gross_weight |
| coefficient | Float | 系数 | 可为空 |
| status | String(20) | 状态 | 执行/归档，默认执行 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### AssayData（化验数据）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 化验数据ID | 主键，自增 |
| sample_name | String(100) | 样品名称 | 不可为空 |
| factory_id | Integer | 分厂ID | 不可为空 |
| water_content | Float | 水含量 | 可为空 |
| zinc_content | Float | 锌含量 | 可为空 |
| lead_content | Float | 铅含量 | 可为空 |
| chlorine_content | Float | 氯含量 | 可为空 |
| fluorine_content | Float | 氟含量 | 可为空 |
| iron_content | Float | 铁含量 | 可为空 |
| silicon_content | Float | 硅含量 | 可为空 |
| sulfur_content | Float | 硫含量 | 可为空 |
| high_heat | Float | 高热值 | 可为空 |
| low_heat | Float | 低热值 | 可为空 |
| silver_content | Float | 银含量 | 可为空 |
| recovery_rate | Float | 回收率 | 可为空 |
| remarks | Text | 备注信息 | 可为空 |
| created_by | Integer | 创建人ID | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### MetalPrice（金属价格）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 价格ID | 主键，自增 |
| metal_type | String(50) | 金属种类 | 默认1#锌 |
| quote_date | Date | 报价日期 | 不可为空 |
| high_price | Float | 最高价 | 可为空 |
| low_price | Float | 最低价 | 可为空 |
| average_price | Float | 均价 | 不可为空 |
| price_change | Float | 涨跌 | 不可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

---

## 权限系统

### 权限列表

| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| user_read | 用户查看 | 查看用户信息 |
| user_create | 用户创建 | 创建新用户 |
| user_update | 用户更新 | 更新用户信息 |
| user_delete | 用户删除 | 删除用户 |
| material_read | 物料查看 | 查看物料信息 |
| material_create | 物料创建 | 创建新物料 |
| material_update | 物料更新 | 更新物料信息 |
| material_delete | 物料删除 | 删除物料 |
| customer_read | 客户查看 | 查看客户信息 |
| customer_create | 客户创建 | 创建新客户 |
| customer_update | 客户更新 | 更新客户信息 |
| customer_delete | 客户删除 | 删除客户 |
| department_read | 部门查看 | 查看部门信息 |
| contract_read | 合同查看 | 查看合同信息 |
| assay_data_read | 化验数据查看 | 查看化验数据 |
| attachment_read | 附件查看 | 查看和下载附件 |
| attachment_create | 附件上传 | 上传新附件 |
| metal_price_read | 金属价格查看 | 查看金属价格 |

### 角色系统

系统支持基于角色的权限管理（RBAC），用户可以拥有多个角色，每个角色包含多个权限。

---

## 错误代码

| 错误代码 | 说明 |
|----------|------|
| INVALID_CREDENTIALS | 用户名或密码错误 |
| USER_NOT_FOUND | 用户不存在 |
| PERMISSION_DENIED | 权限不足 |
| RESOURCE_NOT_FOUND | 资源不存在 |
| VALIDATION_ERROR | 参数验证失败 |
| DUPLICATE_RESOURCE | 资源重复 |
| FILE_UPLOAD_ERROR | 文件上传失败 |
| FILE_NOT_FOUND | 文件不存在 |
| DATABASE_ERROR | 数据库操作失败 |
| INTERNAL_ERROR | 服务器内部错误 |

---

## 开发说明

### 技术栈

- **后端框架**: Flask
- **数据库**: SQLite（开发环境）
- **ORM**: SQLAlchemy
- **认证**: Flask-Login
- **跨域**: Flask-CORS
- **文件上传**: Werkzeug

### 部署环境

- **开发环境**: `http://localhost:5000`
- **生产环境**: 根据实际部署配置

### 注意事项

1. 所有需要认证的接口都需要在请求头中包含有效的认证信息
2. 文件上传接口使用 `multipart/form-data` 格式
3. 日期格式统一使用 ISO 8601 格式（YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SS）
4. 所有接口都支持 CORS 跨域请求
5. 权限验证基于用户角色和权限系统
6. 移动端接口针对移动设备优化，返回更简洁的数据格式

---

## 更新日志

### v1.0.0 (2024-01-15)

- 初始版本发布
- 实现用户管理、物料管理、客户管理等核心功能
- 支持文件上传和下载
- 实现权限控制系统
- 提供移动端专用接口

---

*本文档最后更新时间：2024-01-15*