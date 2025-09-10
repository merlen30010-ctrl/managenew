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

**接口地址**: `POST /api/auth/login`

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
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "name": "管理员",
      "is_superuser": true
    }
  }
}
```

### 用户注册

**接口地址**: `POST /api/auth/register`

**请求参数**:
```json
{
  "username": "用户名",
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
      "name": "新用户",
      "is_superuser": false
    }
  }
}
```

### 用户登出

**接口地址**: `POST /api/auth/logout`

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
    "name": "管理员",
    "is_active": true,
    "is_superuser": true
  }
}
```

### 获取用户列表

**接口地址**: `GET /api/users`

**权限要求**: `user_read`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "name": "管理员",
        "is_active": true,
        "is_superuser": true
      },
      {
        "id": 2,
        "username": "user1",
        "name": "用户1",
        "is_active": true,
        "is_superuser": false
      }
    ],
    "total": 2,
    "pages": 1,
    "current_page": 1,
    "per_page": 20
  }
}
```

### 获取单个用户信息

**接口地址**: `GET /api/users/{user_id}`

**权限要求**: `user_read`

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "name": "管理员",
    "is_active": true,
    "is_superuser": true
  }
}
```

### 创建用户

**接口地址**: `POST /api/users`

**权限要求**: `user_create`

**请求参数**:
```json
{
  "username": "用户名",
  "name": "真实姓名（可选）",
  "password": "密码",
  "is_active": true,
  "is_superuser": false
}
```

**字段说明**:
- `username`: 用户名，必填，唯一
- `name`: 真实姓名，可选
- `password`: 登录密码，必填
- `is_active`: 用户状态，默认为true（激活）
- `is_superuser`: 是否为超级管理员，默认为false

**响应示例**:
```json
{
  "success": true,
  "message": "用户创建成功",
  "data": {
    "id": 3,
    "username": "newuser",
    "name": "新用户",
    "is_active": true,
    "is_superuser": false
  }
}
```

### 更新用户信息

**接口地址**: `PUT /api/users/{user_id}`

**权限要求**: `user_update`

**路径参数**:
- `user_id` (integer): 用户ID

**请求参数**:
```json
{
  "username": "新用户名（可选）",
  "name": "新姓名（可选）",
  "password": "新密码（可选）",
  "is_active": true,
  "is_superuser": false
}
```

**字段说明**:
- `username`: 新用户名，可选，如果提供必须唯一
- `name`: 新真实姓名，可选
- `password`: 新密码，可选
- `is_active`: 用户状态，可选
- `is_superuser`: 超级管理员状态，可选（需要超级管理员权限）

**响应示例**:
```json
{
  "success": true,
  "message": "用户信息更新成功",
  "data": {
    "id": 2,
    "username": "updateduser",
    "name": "更新后的用户",
    "is_active": true,
    "is_superuser": false
  }
}
```

### 删除用户

**接口地址**: `DELETE /api/users/{user_id}`

**权限要求**: `user_delete`

**安全保护机制**:
- 不能删除当前登录用户
- 不能删除系统管理员admin用户
- 不能删除最后一个超级管理员

**响应示例**:
```json
{
  "success": true,
  "message": "用户删除成功"
}
```

**错误响应示例**:
```json
{
  "success": false,
  "message": "不能删除系统管理员admin用户"
}
```

---

## 员工管理接口

### 获取员工列表

**接口地址**: `GET /api/employees`

**权限要求**: `admin_required`

**查询参数**:
- `search` (string): 搜索关键词，支持员工工号、姓名、电话搜索（可选）
- `department_id` (integer): 部门ID过滤（可选）
- `employment_status` (string): 在职状态过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）
- `sort` (string): 排序字段（可选）
- `order` (string): 排序方向，asc或desc（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "user_id": 1,
        "employee_id": "EMP001",
        "name": "张三",
        "department_id": 1,
        "department_name": "技术部",
        "job_title": "工程师",
        "hire_date": "2024-01-01",
        "work_years": 1,
        "gender": "男",
        "birth_date": "1990-01-01",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "employment_status": "在职"
      }
    ],
    "total": 100,
    "pages": 5,
    "current_page": 1,
    "per_page": 20
  }
}
```

### 获取单个员工信息

**接口地址**: `GET /api/employees/{user_id}`

**权限要求**: 管理员或本人

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "employee_id": "EMP001",
    "name": "张三",
    "department_id": 1,
    "department_name": "技术部",
    "job_title": "工程师",
    "hire_date": "2024-01-01",
    "work_years": 1,
    "gender": "男",
    "birth_date": "1990-01-01",
    "id_card": "110101199001011234",
    "native_place": "北京市",
    "nationality": "汉族",
    "education": "本科",
    "marital_status": "未婚",
    "phone": "13800138000",
    "address": "北京市朝阳区",
    "employment_status": "在职",
    "emergency_contact": "李四",
    "emergency_phone": "13900139000",
    "avatar_path": "/uploads/avatars/emp001.jpg"
  }
}
```

### 创建员工信息

**接口地址**: `POST /api/employees`

**权限要求**: `admin_required`

**请求参数**:
```json
{
  "user_id": 1,
  "employee_id": "EMP001",
  "department_id": 1,
  "job_title": "工程师",
  "hire_date": "2024-01-01",
  "work_years": 1,
  "name": "张三",
  "gender": "男",
  "birth_date": "1990-01-01",
  "id_card": "110101199001011234",
  "native_place": "北京市",
  "nationality": "汉族",
  "education": "本科",
  "marital_status": "未婚",
  "phone": "13800138000",
  "address": "北京市朝阳区",
  "employment_status": "在职",
  "emergency_contact": "李四",
  "emergency_phone": "13900139000"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "员工信息创建成功",
  "data": {
    "user_id": 1,
    "employee_id": "EMP001",
    "name": "张三",
    "department_id": 1,
    "job_title": "工程师"
  }
}
```

### 更新员工信息

**接口地址**: `PUT /api/employees/{user_id}`

**权限要求**: 管理员或本人

**路径参数**:
- `user_id` (integer): 用户ID

**请求参数**:
```json
{
  "employee_id": "EMP002",
  "department_id": 2,
  "job_title": "高级工程师",
  "hire_date": "2024-01-01",
  "work_years": 2,
  "name": "张三",
  "gender": "男",
  "birth_date": "1990-01-01",
  "id_card": "110101199001011234",
  "native_place": "北京市",
  "nationality": "汉族",
  "education": "硕士",
  "marital_status": "已婚",
  "phone": "13800138001",
  "address": "北京市海淀区",
  "employment_status": "在职",
  "emergency_contact": "王五",
  "emergency_phone": "13900139001"
}
```

### 删除员工信息

**接口地址**: `DELETE /api/employees/{user_id}`

**权限要求**: `admin_required`

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "success": true,
  "message": "员工信息删除成功"
}
```

### 上传员工头像

**接口地址**: `POST /api/employees/{user_id}/avatar`

**权限要求**: 管理员或本人

**路径参数**:
- `user_id` (integer): 用户ID

**请求参数**: 
- `file` (file): 头像文件，支持PNG、JPG、JPEG、GIF格式

**响应示例**:
```json
{
  "success": true,
  "message": "头像上传成功",
  "data": {
    "avatar_path": "/uploads/avatars/emp001_20240101_120000_avatar.jpg"
  }
}
```

### 获取员工统计信息

**接口地址**: `GET /api/employees/statistics`

**权限要求**: `admin_required`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_count": 150,
    "active_count": 145,
    "department_stats": [
      {
        "name": "技术部",
        "count": 50
      },
      {
        "name": "销售部",
        "count": 30
      }
    ],
    "gender_stats": [
      {
        "gender": "男",
        "count": 90
      },
      {
        "gender": "女",
        "count": 60
      }
    ],
    "education_stats": [
      {
        "education": "本科",
        "count": 80
      },
      {
        "education": "硕士",
        "count": 50
      }
    ]
  }
}
```

---

## 员工证件管理接口

### 获取员工证件列表

**接口地址**: `GET /api/employee-documents`

**权限要求**: 需要登录

**查询参数**:
- `employee_id` (string): 员工工号过滤（可选）
- `document_type` (string): 证件类型过滤（可选）
- `status` (string): 证件状态过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "documents": [
      {
        "id": 1,
        "employee_id": "EMP001",
        "document_type": "身份证",
        "document_name": "居民身份证",
        "document_number": "110101199001011234",
        "issuing_authority": "北京市公安局",
        "issue_date": "2010-01-01",
        "expiry_date": "2030-01-01",
        "status": "有效",
        "is_original": true,
        "file_path": "/uploads/documents/emp001_idcard.jpg",
        "notes": "身份证正反面",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
      }
    ],
    "total": 50,
    "pages": 3,
    "current_page": 1,
    "per_page": 20
  }
}
```

### 获取单个员工证件详情

**接口地址**: `GET /api/employee-documents/{document_id}`

**权限要求**: 需要登录

**路径参数**:
- `document_id` (integer): 证件ID

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "employee_id": "EMP001",
    "document_type": "身份证",
    "document_name": "居民身份证",
    "document_number": "110101199001011234",
    "issuing_authority": "北京市公安局",
    "issue_date": "2010-01-01",
    "expiry_date": "2030-01-01",
    "status": "有效",
    "is_original": true,
    "file_path": "/uploads/documents/emp001_idcard.jpg",
    "file_name": "身份证.jpg",
    "file_size": 1024000,
    "notes": "身份证正反面",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 创建员工证件

**接口地址**: `POST /api/employee-documents`

**权限要求**: `admin_required`

**请求参数**:
```json
{
  "employee_id": "EMP001",
  "document_type": "身份证",
  "document_name": "居民身份证",
  "document_number": "110101199001011234",
  "issuing_authority": "北京市公安局",
  "issue_date": "2010-01-01",
  "expiry_date": "2030-01-01",
  "status": "有效",
  "is_original": true,
  "notes": "身份证正反面"
}
```

### 更新员工证件

**接口地址**: `PUT /api/employee-documents/{document_id}`

**权限要求**: `admin_required`

**路径参数**:
- `document_id` (integer): 证件ID

### 删除员工证件

**接口地址**: `DELETE /api/employee-documents/{document_id}`

**权限要求**: `admin_required`

**路径参数**:
- `document_id` (integer): 证件ID

### 获取证件类型列表

**接口地址**: `GET /api/document-types`

**权限要求**: 需要登录

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "type_code": "ID_CARD",
      "type_name": "身份证",
      "category": "身份证明",
      "is_required": true,
      "has_expiry": true,
      "reminder_days": 30,
      "description": "居民身份证",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 获取即将过期的证件

**接口地址**: `GET /api/employee-documents/expiring`

**权限要求**: 需要登录

**查询参数**:
- `days` (integer): 提前天数，默认为30天（可选）

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "employee_id": "EMP001",
      "document_type": "驾驶证",
      "document_name": "机动车驾驶证",
      "expiry_date": "2024-02-01",
      "days_to_expiry": 15,
      "is_expired": false,
      "status": "有效"
    }
  ]
}
```

---

## 员工奖惩管理接口

### 获取员工奖惩记录列表

**接口地址**: `GET /api/employee-reward-punishments`

**权限要求**: 需要登录

**查询参数**:
- `employee_id` (string): 员工工号过滤（可选）
- `type` (string): 奖惩类型过滤，奖励/惩罚（可选）
- `category` (string): 奖惩分类过滤（可选）
- `status` (string): 状态过滤（可选）
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "records": [
      {
        "id": 1,
        "employee_id": "EMP001",
        "type": "奖励",
        "category": "工作表现",
        "title": "优秀员工",
        "description": "工作认真负责，表现优秀",
        "reason": "月度考核第一名",
        "amount": 1000.00,
        "decision_date": "2024-01-15",
        "status": "已执行",
        "created_at": "2024-01-15T00:00:00",
        "updated_at": "2024-01-15T00:00:00"
      }
    ],
    "pagination": {
      "total": 100,
      "pages": 5,
      "page": 1,
      "per_page": 20
    }
  }
}
```

### 获取单个员工奖惩记录详情

**接口地址**: `GET /api/employee-reward-punishments/{record_id}`

**权限要求**: 需要登录

**路径参数**:
- `record_id` (integer): 奖惩记录ID

### 创建员工奖惩记录

**接口地址**: `POST /api/employee-reward-punishments`

**权限要求**: `admin_required`

**请求参数**:
```json
{
  "employee_id": "EMP001",
  "type": "奖励",
  "category": "工作表现",
  "title": "优秀员工",
  "description": "工作认真负责，表现优秀",
  "reason": "月度考核第一名",
  "amount": 1000.00,
  "decision_date": "2024-01-15"
}
```

### 更新员工奖惩记录

**接口地址**: `PUT /api/employee-reward-punishments/{record_id}`

**权限要求**: `admin_required`

### 删除员工奖惩记录

**接口地址**: `DELETE /api/employee-reward-punishments/{record_id}`

**权限要求**: `admin_required`

### 获取奖惩类型列表

**接口地址**: `GET /api/reward-punishment-types`

**权限要求**: 需要登录

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "type_name": "工作表现奖",
      "category": "奖励",
      "description": "工作表现优秀的奖励",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 获取员工奖惩统计摘要

**接口地址**: `GET /api/employee-reward-punishments/summary`

**权限要求**: 需要登录

**查询参数**:
- `employee_id` (string): 员工工号过滤（可选）
- `year` (integer): 年份过滤，默认为当前年份（可选）

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total_records": 10,
    "rewards": 8,
    "punishments": 2,
    "total_reward_amount": 5000.00,
    "total_punishment_amount": 500.00,
    "categories": {
      "工作表现": {
        "count": 6,
        "type": "奖励"
      },
      "迟到早退": {
        "count": 2,
        "type": "惩罚"
      }
    }
  }
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

**查询参数**:
- `search` (string): 搜索关键词（客户名称、代码）（可选）
- `customer_type` (string): 客户类型过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "customers": [
      {
        "id": 1,
        "name": "客户A",
        "code": "CUS001",
        "full_name": "客户A有限公司",
        "customer_type": "产品采购",
        "phone": "13800138000",
        "address": "北京市朝阳区",
        "contract_count": 5
      }
    ],
    "pagination": {
      "total": 50,
      "pages": 3,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 获取单个客户信息

**接口地址**: `GET /api/customers/{customer_id}`

**权限要求**: `customer_read`

**路径参数**:
- `customer_id` (integer): 客户ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "客户A",
    "code": "CUS001",
    "full_name": "客户A有限公司",
    "customer_type": "产品采购",
    "phone": "13800138000",
    "address": "北京市朝阳区",
    "contracts": [
      {
        "id": 1,
        "contract_number": "CON2024001",
        "contract_type": "产品销售",
        "status": "执行",
        "sign_date": "2024-01-01"
      }
    ]
  }
}
```

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

**响应示例**:
```json
{
  "success": true,
  "message": "客户创建成功",
  "data": {
    "id": 2,
    "name": "新客户",
    "code": "CUS002",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 更新客户信息

**接口地址**: `PUT /api/customers/{customer_id}`

**权限要求**: `customer_update`

**路径参数**:
- `customer_id` (integer): 客户ID

**请求参数**:
```json
{
  "name": "更新的客户名称",
  "full_name": "更新的客户全称",
  "customer_type": "原料供应",
  "phone": "13900139000",
  "address": "上海市浦东新区"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "客户信息更新成功",
  "data": {
    "id": 1,
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 删除客户

**接口地址**: `DELETE /api/customers/{customer_id}`

**权限要求**: `customer_delete`

**路径参数**:
- `customer_id` (integer): 客户ID

**响应示例**:
```json
{
  "success": true,
  "message": "客户删除成功"
}
```

### 获取客户类型列表

**接口地址**: `GET /api/customers/types`

**权限要求**: `customer_read`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "value": "原料供应",
      "label": "原料供应",
      "count": 15
    },
    {
      "value": "产品采购",
      "label": "产品采购",
      "count": 25
    },
    {
      "value": "辅料供应",
      "label": "辅料供应",
      "count": 8
    },
    {
      "value": "其他",
      "label": "其他",
      "count": 2
    }
  ]
}
```

---

## 文章管理接口

### 获取文章列表

**接口地址**: `GET /api/articles`

**权限要求**: `article_read`

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）
- `category_id` (integer): 分类ID过滤（可选）
- `status` (string): 状态过滤（draft/published）（可选）
- `search` (string): 搜索关键词（可选）

**响应示例**:
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "articles": [
      {
        "id": 1,
        "title": "文章标题",
        "content": "文章内容",
        "summary": "文章摘要",
        "category_id": 1,
        "category_name": "技术分享",
        "author_id": 1,
        "author_name": "张三",
        "status": "published",
        "view_count": 100,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "published_at": "2024-01-15T10:30:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 50,
      "pages": 5
    }
  }
}
```

### 获取单个文章信息

**接口地址**: `GET /api/articles/{article_id}`

**权限要求**: `article_read`

**响应示例**:
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "title": "文章标题",
    "content": "文章内容",
    "summary": "文章摘要",
    "category_id": 1,
    "category_name": "技术分享",
    "author_id": 1,
    "author_name": "张三",
    "status": "published",
    "view_count": 100,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "published_at": "2024-01-15T10:30:00",
    "attachments": [
      {
        "id": 1,
        "filename": "document.pdf",
        "original_filename": "原始文档.pdf",
        "file_size": 1024000,
        "file_type": "application/pdf",
        "upload_time": "2024-01-15T10:30:00"
      }
    ]
  }
}
```

### 创建文章

**接口地址**: `POST /api/articles`

**权限要求**: `article_create`

**请求参数**:
```json
{
  "title": "文章标题",
  "content": "文章内容",
  "summary": "文章摘要（可选）",
  "category_id": 1,
  "status": "draft"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "创建成功",
  "data": {
    "id": 1,
    "title": "文章标题",
    "status": "draft"
  }
}
```

### 更新文章信息

**接口地址**: `PUT /api/articles/{article_id}`

**权限要求**: `article_update`

**请求参数**:
```json
{
  "title": "更新的文章标题",
  "content": "更新的文章内容",
  "summary": "更新的文章摘要",
  "category_id": 2,
  "status": "published"
}
```

### 删除文章

**接口地址**: `DELETE /api/articles/{article_id}`

**权限要求**: `article_delete`

### 发布文章

**接口地址**: `POST /api/articles/{article_id}/publish`

**权限要求**: `article_publish`

**响应示例**:
```json
{
  "success": true,
  "message": "发布成功",
  "data": {
    "id": 1,
    "status": "published",
    "published_at": "2024-01-15T10:30:00"
  }
}
```

---

## 文章分类管理接口

### 获取分类列表

**接口地址**: `GET /api/article-categories`

**权限要求**: `article_category_read`

**响应示例**:
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "技术分享",
      "description": "技术相关文章",
      "article_count": 10,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### 获取单个分类信息

**接口地址**: `GET /api/article-categories/{category_id}`

**权限要求**: `article_category_read`

### 创建分类

**接口地址**: `POST /api/article-categories`

**权限要求**: `article_category_create`

**请求参数**:
```json
{
  "name": "分类名称",
  "description": "分类描述（可选）"
}
```

### 更新分类信息

**接口地址**: `PUT /api/article-categories/{category_id}`

**权限要求**: `article_category_update`

### 删除分类

**接口地址**: `DELETE /api/article-categories/{category_id}`

**权限要求**: `article_category_delete`

---

## 部门管理接口

### 获取部门列表

**接口地址**: `GET /api/departments`

**权限要求**: `department_read`

**查询参数**:
- `level` (integer): 部门级别过滤（1为分厂，2为部门）（可选）
- `parent_id` (integer): 父级部门ID过滤（可选）
- `is_active` (boolean): 是否启用过滤（可选）
- `search` (string): 搜索关键词（部门名称）（可选）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "一分厂",
      "short_name": "一厂",
      "full_name": "第一分厂",
      "level": 1,
      "parent_id": null,
      "parent_name": null,
      "phone": "010-12345678",
      "is_active": true,
      "managers": [
        {
          "id": 1,
          "name": "张三",
          "username": "zhangsan"
        }
      ],
      "children_count": 3,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 获取单个部门信息

**接口地址**: `GET /api/departments/{department_id}`

**权限要求**: `department_read`

**路径参数**:
- `department_id` (integer): 部门ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "一分厂",
    "short_name": "一厂",
    "full_name": "第一分厂",
    "level": 1,
    "parent_id": null,
    "parent_name": null,
    "phone": "010-12345678",
    "is_active": true,
    "managers": [
      {
        "id": 1,
        "name": "张三",
        "username": "zhangsan"
      }
    ],
    "children": [
      {
        "id": 2,
        "name": "生产部",
        "level": 2
      }
    ],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 创建部门

**接口地址**: `POST /api/departments`

**权限要求**: `department_create`

**请求参数**:
```json
{
  "name": "部门名称",
  "short_name": "部门简称",
  "full_name": "部门全称",
  "level": 1,
  "parent_id": null,
  "phone": "010-12345678",
  "manager_ids": [1, 2]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "部门创建成功",
  "data": {
    "id": 3,
    "name": "二分厂",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 更新部门信息

**接口地址**: `PUT /api/departments/{department_id}`

**权限要求**: `department_update`

**路径参数**:
- `department_id` (integer): 部门ID

**请求参数**:
```json
{
  "name": "更新的部门名称",
  "short_name": "更新的简称",
  "full_name": "更新的全称",
  "phone": "010-87654321",
  "is_active": true,
  "manager_ids": [1, 3]
}
```

### 删除部门

**接口地址**: `DELETE /api/departments/{department_id}`

**权限要求**: `department_delete`

**路径参数**:
- `department_id` (integer): 部门ID

**响应示例**:
```json
{
  "success": true,
  "message": "部门删除成功"
}
```

### 获取部门树形结构

**接口地址**: `GET /api/departments/tree`

**权限要求**: `department_read`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "一分厂",
      "level": 1,
      "children": [
        {
          "id": 2,
          "name": "生产部",
          "level": 2,
          "children": []
        }
      ]
    }
  ]
}
```

---

## 合同管理接口

### 获取合同列表

**接口地址**: `GET /api/contracts`

**权限要求**: `contract_read`

**查询参数**:
- `search` (string): 搜索关键词（合同编号、客户名称）（可选）
- `contract_type` (string): 合同类型过滤（可选）
- `customer_id` (integer): 客户ID过滤（可选）
- `material_id` (integer): 物料ID过滤（可选）
- `factory_id` (integer): 分厂ID过滤（可选）
- `status` (string): 合同状态过滤（可选）
- `start_date` (string): 签订开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 签订结束日期，格式：YYYY-MM-DD（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "contracts": [
      {
        "id": 1,
        "contract_type": "产品销售",
        "contract_number": "CON2024001",
        "customer_id": 1,
        "customer_name": "客户A",
        "material_id": 1,
        "material_name": "锌锭",
        "factory_id": 1,
        "factory_name": "一分厂",
        "responsible_id": 1,
        "responsible_name": "张三",
        "sign_date": "2024-01-01",
        "expiry_date": "2024-12-31",
        "tax_rate": 0.13,
        "pricing_method": "weight",
        "pricing_method_display": "金吨计价",
        "coefficient": 1.0,
        "status": "执行",
        "file_count": 3,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
      }
    ],
    "pagination": {
      "total": 100,
      "pages": 5,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 获取单个合同信息

**接口地址**: `GET /api/contracts/{contract_id}`

**权限要求**: `contract_read`

**路径参数**:
- `contract_id` (integer): 合同ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "contract_type": "产品销售",
    "contract_number": "CON2024001",
    "customer_id": 1,
    "customer_name": "客户A",
    "customer_code": "CUS001",
    "material_id": 1,
    "material_name": "锌锭",
    "material_code": "ZN001",
    "factory_id": 1,
    "factory_name": "一分厂",
    "responsible_id": 1,
    "responsible_name": "张三",
    "sign_date": "2024-01-01",
    "expiry_date": "2024-12-31",
    "tax_rate": 0.13,
    "pricing_method": "weight",
    "pricing_method_display": "金吨计价",
    "coefficient": 1.0,
    "status": "执行",
    "files": [
      {
        "id": 1,
        "file_name": "合同文件.pdf",
        "file_path": "/uploads/contracts/contract_1.pdf",
        "file_type": "pdf",
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 创建合同

**接口地址**: `POST /api/contracts`

**权限要求**: `contract_create`

**请求参数**:
```json
{
  "contract_type": "产品销售",
  "contract_number": "CON2024002",
  "customer_id": 1,
  "material_id": 1,
  "factory_id": 1,
  "responsible_id": 1,
  "sign_date": "2024-01-15",
  "expiry_date": "2024-12-31",
  "tax_rate": 0.13,
  "pricing_method": "weight",
  "coefficient": 1.0,
  "status": "执行"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "合同创建成功",
  "data": {
    "id": 2,
    "contract_number": "CON2024002",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 更新合同信息

**接口地址**: `PUT /api/contracts/{contract_id}`

**权限要求**: `contract_update`

**路径参数**:
- `contract_id` (integer): 合同ID

**请求参数**:
```json
{
  "expiry_date": "2025-12-31",
  "tax_rate": 0.15,
  "coefficient": 1.1,
  "status": "归档"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "合同信息更新成功",
  "data": {
    "id": 1,
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 删除合同

**接口地址**: `DELETE /api/contracts/{contract_id}`

**权限要求**: `contract_delete`

**路径参数**:
- `contract_id` (integer): 合同ID

**响应示例**:
```json
{
  "success": true,
  "message": "合同删除成功"
}
```

### 获取合同类型列表

**接口地址**: `GET /api/contracts/types`

**权限要求**: `contract_read`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "value": "原料采购",
      "label": "原料采购",
      "count": 20
    },
    {
      "value": "产品销售",
      "label": "产品销售",
      "count": 35
    },
    {
      "value": "辅料采购",
      "label": "辅料采购",
      "count": 10
    },
    {
      "value": "其他",
      "label": "其他",
      "count": 5
    }
  ]
}
```

### 获取计价方式列表

**接口地址**: `GET /api/contracts/pricing-methods`

**权限要求**: `contract_read`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "value": "weight",
      "label": "金吨计价"
    },
    {
      "value": "content",
      "label": "含量加点"
    },
    {
      "value": "processing",
      "label": "加工费用"
    },
    {
      "value": "gross_weight",
      "label": "毛吨计价"
    }
  ]
}
```

### 合同价格计算

**接口地址**: `POST /api/contracts/{contract_id}/calculate-price`

**权限要求**: `contract_read`

**路径参数**:
- `contract_id` (integer): 合同ID

**请求参数**:
```json
{
  "base_price": 22000.0,
  "quantity": 100.0
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "base_price": 22000.0,
    "quantity": 100.0,
    "coefficient": 1.0,
    "calculated_price": 2200000.0,
    "tax_rate": 0.13,
    "tax_amount": 286000.0,
    "total_amount": 2486000.0
  }
}
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

---

## 通知管理接口

### 获取当前用户通知列表

**接口地址**: `GET /api/notifications`

**权限要求**: `notification_read`

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）
- `is_read` (boolean): 是否已读，true/false（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 1,
        "title": "系统维护通知",
        "content": "系统将于今晚22:00-24:00进行维护",
        "is_read": false,
        "created_at": "2024-01-15T10:00:00",
        "read_at": null
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 5,
      "per_page": 10,
      "total": 45
    }
  }
}
```

### 标记通知为已读

**接口地址**: `PUT /api/notifications/{notification_id}/read`

**权限要求**: `notification_read`

**路径参数**:
- `notification_id` (integer): 通知ID

**响应示例**:
```json
{
  "success": true,
  "message": "通知已标记为已读",
  "data": {
    "id": 1,
    "read_at": "2024-01-15T10:30:00"
  }
}
```

### 标记所有通知为已读

**接口地址**: `PUT /api/notifications/mark-all-read`

**权限要求**: `notification_read`

**响应示例**:
```json
{
  "success": true,
  "message": "所有通知已标记为已读",
  "data": {
    "updated_count": 5
  }
}
```

### 创建通知

**接口地址**: `POST /api/notifications`

**权限要求**: `notification_create`

**请求参数**:
```json
{
  "title": "通知标题",
  "content": "通知内容",
  "user_id": 1
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "通知创建成功",
  "data": {
    "id": 2,
    "title": "通知标题",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 删除通知

**接口地址**: `DELETE /api/notifications/{notification_id}`

**权限要求**: `notification_delete`

**路径参数**:
- `notification_id` (integer): 通知ID

**响应示例**:
```json
{
  "success": true,
  "message": "通知删除成功"
}
```

### 获取未读通知数量

**接口地址**: `GET /api/notifications/unread-count`

**权限要求**: `notification_read`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "unread_count": 3
  }
}
```

### 管理员获取所有通知

**接口地址**: `GET /api/admin/notifications`

**权限要求**: `notification_manage`

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）
- `user_id` (integer): 用户ID过滤（可选）
- `is_read` (boolean): 是否已读过滤（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 1,
        "title": "系统维护通知",
        "content": "系统将于今晚22:00-24:00进行维护",
        "user_id": 1,
        "user_name": "张三",
        "is_read": false,
        "created_at": "2024-01-15T10:00:00",
        "read_at": null
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 5,
      "per_page": 20,
      "total": 100
    }
  }
}
```

### 管理员创建通知

**接口地址**: `POST /api/admin/notifications`

**权限要求**: `notification_create`

**请求参数**:
```json
{
  "title": "通知标题",
  "content": "通知内容",
  "user_ids": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "通知创建成功",
  "data": {
    "created_count": 3,
    "notification_ids": [10, 11, 12]
  }
}
```

### 广播通知

**接口地址**: `POST /api/admin/notifications/broadcast`

**权限要求**: `notification_create`

**请求参数**:
```json
{
  "title": "系统公告",
  "content": "重要系统更新通知"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "广播通知发送成功",
  "data": {
    "sent_count": 50,
    "notification_ids": [13, 14, 15]
  }
}
```

---

## 考试结果管理接口

### 获取考试结果列表

**接口地址**: `GET /api/exam-results`

**权限要求**: `exam_result_read`

**查询参数**:
- `user_id` (integer): 用户ID过滤（可选）
- `exam_name` (string): 考试名称搜索（可选）
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "exam_results": [
      {
        "id": 1,
        "user_id": 1,
        "user_name": "张三",
        "exam_name": "安全知识考试",
        "score": 85.5,
        "total_score": 100.0,
        "percentage": 85.5,
        "exam_date": "2024-01-15T14:00:00",
        "created_at": "2024-01-15T14:30:00"
      }
    ],
    "pagination": {
      "total": 50,
      "pages": 3,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 创建考试结果

**接口地址**: `POST /api/exam-results`

**权限要求**: `exam_result_create`

**请求参数**:
```json
{
  "user_id": 1,
  "exam_name": "安全知识考试",
  "score": 85.5,
  "total_score": 100.0,
  "exam_date": "2024-01-15T14:00:00"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "考试结果创建成功",
  "data": {
    "id": 2,
    "percentage": 85.5,
    "created_at": "2024-01-15T14:30:00"
  }
}
```

### 获取单个考试结果

**接口地址**: `GET /api/exam-results/{result_id}`

**权限要求**: `exam_result_read`

**路径参数**:
- `result_id` (integer): 考试结果ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "user_name": "张三",
    "exam_name": "安全知识考试",
    "score": 85.5,
    "total_score": 100.0,
    "percentage": 85.5,
    "exam_date": "2024-01-15T14:00:00",
    "created_at": "2024-01-15T14:30:00"
  }
}
```

### 更新考试结果

**接口地址**: `PUT /api/exam-results/{result_id}`

**权限要求**: `exam_result_update`

**路径参数**:
- `result_id` (integer): 考试结果ID

**请求参数**:
```json
{
  "score": 90.0,
  "exam_date": "2024-01-15T15:00:00"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "考试结果更新成功",
  "data": {
    "id": 1,
    "percentage": 90.0,
    "updated_at": "2024-01-15T15:30:00"
  }
}
```

### 删除考试结果

**接口地址**: `DELETE /api/exam-results/{result_id}`

**权限要求**: `exam_result_delete`

**路径参数**:
- `result_id` (integer): 考试结果ID

**响应示例**:
```json
{
  "success": true,
  "message": "考试结果删除成功"
}
```

---

## 文章分类管理接口

### 获取文章分类列表

**接口地址**: `GET /api/article-categories`

**权限要求**: `article_read`

**查询参数**:
- `is_active` (boolean): 是否启用过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "公司新闻",
        "description": "公司相关新闻和动态",
        "sort_order": 1,
        "is_active": true,
        "article_count": 15,
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "pagination": {
      "total": 10,
      "pages": 1,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 获取启用的分类列表

**接口地址**: `GET /api/article-categories/active`

**权限要求**: `article_read`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "公司新闻",
      "description": "公司相关新闻和动态",
      "sort_order": 1,
      "article_count": 15
    }
  ]
}
```

### 创建文章分类

**接口地址**: `POST /api/article-categories`

**权限要求**: `article_category_create`

**请求参数**:
```json
{
  "name": "技术文档",
  "description": "技术相关文档和教程",
  "sort_order": 2,
  "is_active": true
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "文章分类创建成功",
  "data": {
    "id": 2,
    "name": "技术文档",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 更新文章分类

**接口地址**: `PUT /api/article-categories/{category_id}`

**权限要求**: `article_category_update`

**路径参数**:
- `category_id` (integer): 分类ID

**请求参数**:
```json
{
  "name": "技术文档更新",
  "description": "更新后的描述",
  "sort_order": 3,
  "is_active": false
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "文章分类更新成功",
  "data": {
    "id": 2,
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 删除文章分类

**接口地址**: `DELETE /api/article-categories/{category_id}`

**权限要求**: `article_category_delete`

**路径参数**:
- `category_id` (integer): 分类ID

**响应示例**:
```json
{
  "success": true,
  "message": "文章分类删除成功"
}
```

---

## 文章附件管理接口

### 上传文章附件

**接口地址**: `POST /api/article-attachments/upload`

**权限要求**: `article_create`

**请求类型**: `multipart/form-data`

**请求参数**:
- `file` (file): 要上传的文件
- `article_id` (integer): 文章ID（可选，可后续关联）

**响应示例**:
```json
{
  "success": true,
  "message": "文件上传成功",
  "data": {
    "id": 1,
    "file_path": "/uploads/articles/202401/article_1_file.pdf",
    "original_name": "技术文档.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 下载文章附件

**接口地址**: `GET /api/article-attachments/{attachment_id}/download`

**权限要求**: `article_read`

**路径参数**:
- `attachment_id` (integer): 附件ID

**响应**: 文件流

### 获取文章附件列表

**接口地址**: `GET /api/article-attachments/list`

**权限要求**: `article_read`

**查询参数**:
- `article_id` (integer): 文章ID过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "attachments": [
      {
        "id": 1,
        "related_type": "article",
        "related_id": 1,
        "file_path": "/uploads/articles/202401/article_1_file.pdf",
        "original_name": "技术文档.pdf",
        "file_type": "pdf",
        "file_size": 1024000,
        "created_at": "2024-01-15T10:00:00",
        "creator_name": "张三"
      }
    ],
    "pagination": {
      "total": 5,
      "pages": 1,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 删除文章附件

**接口地址**: `DELETE /api/article-attachments/{attachment_id}`

**权限要求**: `article_edit`

**路径参数**:
- `attachment_id` (integer): 附件ID

**响应示例**:
```json
{
  "success": true,
  "message": "附件删除成功"
}
```

### 更新附件关联文章

**接口地址**: `POST /api/article-attachments/update-article-id`

**权限要求**: `article_edit`

**请求参数**:
```json
{
  "attachment_id": 1,
  "article_id": 2
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "附件关联更新成功",
  "data": {
    "attachment_id": 1,
    "article_id": 2,
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

---

## 系统统计接口

### 获取系统概览统计

**接口地址**: `GET /api/statistics/overview`

**权限要求**: `statistics_read`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 150,
      "active": 120,
      "new_this_month": 5
    },
    "employees": {
      "total": 200,
      "active": 180
    },
    "contracts": {
      "total": 50,
      "active": 35,
      "expiring_soon": 3
    },
    "materials": {
      "total": 30,
      "transactions_this_month": 120
    },
    "notifications": {
      "total_unread": 25,
      "sent_today": 10
    }
  }
}
```

### 获取数据趋势统计

**接口地址**: `GET /api/statistics/trends`

**权限要求**: `statistics_read`

**查询参数**:
- `period` (string): 统计周期（daily/weekly/monthly），默认为monthly（可选）
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "period": "monthly",
    "material_transactions": [
      {
        "date": "2024-01",
        "in_count": 50,
        "out_count": 45,
        "total_quantity": 1000.5
      }
    ],
    "user_activity": [
      {
        "date": "2024-01",
        "login_count": 1200,
        "active_users": 80
      }
    ],
    "contract_status": [
      {
        "date": "2024-01",
        "new_contracts": 5,
        "expired_contracts": 2
      }
    ]
  }
}
```

---

## 系统配置接口

### 获取系统配置

**接口地址**: `GET /api/system/config`

**权限要求**: `system_config_read`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "system_name": "管理系统",
    "version": "1.0.0",
    "upload_max_size": 10485760,
    "allowed_file_types": ["pdf", "doc", "docx", "xls", "xlsx", "jpg", "png"],
    "session_timeout": 3600,
    "pagination_default_size": 20,
    "pagination_max_size": 100
  }
}
```

### 更新系统配置

**接口地址**: `PUT /api/system/config`

**权限要求**: `system_config_update`

**请求参数**:
```json
{
  "upload_max_size": 20971520,
  "session_timeout": 7200,
  "pagination_default_size": 25
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "系统配置更新成功",
  "data": {
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

---

## 系统日志接口

### 获取操作日志

**接口地址**: `GET /api/system/logs`

**权限要求**: `system_log_read`

**查询参数**:
- `user_id` (integer): 用户ID过滤（可选）
- `action` (string): 操作类型过滤（可选）
- `module` (string): 模块过滤（可选）
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "user_id": 1,
        "user_name": "张三",
        "action": "create",
        "module": "contract",
        "description": "创建合同：CON2024001",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2024-01-15T10:00:00"
      }
    ],
    "pagination": {
      "total": 1000,
      "pages": 50,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 清理历史日志

**接口地址**: `DELETE /api/system/logs/cleanup`

**权限要求**: `system_log_delete`

**请求参数**:
```json
{
  "before_date": "2023-12-31"
}
```

**响应示例**:
 ```json
 {
   "success": true,
   "message": "历史日志清理完成",
   "data": {
     "deleted_count": 500
   }
 }
 ```

---

## 数据备份与恢复接口

### 创建数据备份

**接口地址**: `POST /api/system/backup`

**权限要求**: `system_backup_create`

**请求参数**:
```json
{
  "backup_type": "full",
  "description": "定期备份"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "备份任务已启动",
  "data": {
    "backup_id": "backup_20240115_100000",
    "status": "processing",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 获取备份列表

**接口地址**: `GET /api/system/backups`

**权限要求**: `system_backup_read`

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "backups": [
      {
        "id": "backup_20240115_100000",
        "backup_type": "full",
        "description": "定期备份",
        "file_size": 1048576000,
        "status": "completed",
        "created_at": "2024-01-15T10:00:00",
        "completed_at": "2024-01-15T10:30:00"
      }
    ],
    "pagination": {
      "total": 10,
      "pages": 1,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 恢复数据备份

**接口地址**: `POST /api/system/restore`

**权限要求**: `system_backup_restore`

**请求参数**:
```json
{
  "backup_id": "backup_20240115_100000"
}
```

**响应示例**:
 ```json
 {
   "success": true,
   "message": "数据恢复任务已启动",
   "data": {
     "restore_id": "restore_20240115_110000",
     "status": "processing",
     "started_at": "2024-01-15T11:00:00"
   }
 }
 ```

---

## API版本控制

本API支持版本控制，当前版本为 v1.0。

### 版本说明

- **v1.0**: 初始版本，包含所有基础功能模块
- 后续版本将保持向后兼容性
- 重大变更将通过新版本号发布

### 版本使用

在请求头中添加版本信息（可选）：
```
API-Version: v1.0
```

如果不指定版本，默认使用最新稳定版本。

---

## 错误码说明

### HTTP状态码

- **200**: 请求成功
- **201**: 创建成功
- **400**: 请求参数错误
- **401**: 未授权（未登录或token无效）
- **403**: 权限不足
- **404**: 资源不存在
- **409**: 资源冲突（如重复创建）
- **422**: 数据验证失败
- **429**: 请求频率限制
- **500**: 服务器内部错误

### 业务错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 10001 | 用户名或密码错误 | 检查登录凭据 |
| 10002 | 账户已被禁用 | 联系管理员 |
| 10003 | 权限不足 | 联系管理员分配权限 |
| 20001 | 文件上传失败 | 检查文件格式和大小 |
| 20002 | 文件类型不支持 | 使用支持的文件类型 |
| 20003 | 文件大小超限 | 压缩文件或分割上传 |
| 30001 | 数据验证失败 | 检查请求参数格式 |
| 30002 | 必填字段缺失 | 补充必填字段 |
| 30003 | 数据格式错误 | 按照API文档格式提交 |
| 40001 | 资源不存在 | 检查资源ID是否正确 |
| 40002 | 资源已被删除 | 使用有效的资源 |
| 50001 | 数据库连接失败 | 稍后重试或联系技术支持 |
| 50002 | 服务暂时不可用 | 稍后重试 |

---

## 接口限流说明

为保证系统稳定性，API实施了请求频率限制：

### 限制规则

- **普通用户**: 每分钟最多100次请求
- **管理员用户**: 每分钟最多200次请求
- **系统级接口**: 每分钟最多50次请求

### 限流响应

当触发限流时，返回HTTP 429状态码：

```json
{
  "success": false,
  "message": "请求频率过高，请稍后重试",
  "error_code": 429,
  "retry_after": 60
}
```

### 响应头信息

每个API响应都包含限流相关的头信息：

- `X-RateLimit-Limit`: 限制总数
- `X-RateLimit-Remaining`: 剩余请求次数
- `X-RateLimit-Reset`: 限制重置时间（Unix时间戳）

---

## 数据导入导出格式说明

### Excel导入格式要求

1. **文件格式**: 支持.xls和.xlsx格式
2. **编码格式**: UTF-8
3. **第一行**: 必须为列标题
4. **日期格式**: YYYY-MM-DD
5. **时间格式**: YYYY-MM-DD HH:MM:SS
6. **数值格式**: 支持整数和小数
7. **文本长度**: 根据字段限制

### 导出文件说明

- **Excel导出**: 包含完整数据和格式
- **CSV导出**: 纯文本格式，适合数据处理
- **PDF导出**: 适合打印和存档
- **文件命名**: 模块名_导出时间.扩展名

---

## 安全说明

### 数据传输安全

- 所有API请求必须使用HTTPS协议
- 敏感数据在传输过程中进行加密
- 支持TLS 1.2及以上版本

### 身份认证安全

- JWT Token有效期为24小时
- 支持Token刷新机制
- 密码采用bcrypt加密存储
- 支持多因素认证（可选）

### 数据访问安全

- 基于角色的权限控制（RBAC）
- 数据访问日志记录
- 敏感操作需要二次确认
- 支持IP白名单限制

---

## 部署环境

### 开发环境
- **地址**: http://localhost:5000
- **数据库**: SQLite（开发测试）
- **缓存**: 内存缓存

### 测试环境
- **地址**: http://test.example.com
- **数据库**: PostgreSQL
- **缓存**: Redis

### 生产环境
- **地址**: https://api.example.com
- **数据库**: PostgreSQL集群
- **缓存**: Redis集群
- **负载均衡**: Nginx

---

## 注意事项

1. **认证要求**: 除登录接口外，所有接口都需要有效的JWT Token
2. **文件上传**: 单个文件最大10MB，支持的格式见系统配置
3. **日期格式**: 统一使用ISO 8601格式（YYYY-MM-DDTHH:MM:SS）
4. **分页参数**: page从1开始，per_page最大值为100
5. **搜索功能**: 支持模糊搜索，最少输入2个字符
6. **数据导出**: 大量数据导出采用异步处理，通过通知获取结果

---

## 更新日志

### v1.0.0 (2024-01-15)

**新增功能**:
- 用户管理模块
- 员工管理模块
- 部门管理模块
- 客户管理模块
- 物料管理模块
- 合同管理模块
- 物料事务管理模块
- 生产记录管理模块
- 车辆管理模块
- 员工证件管理模块
- 员工奖惩管理模块
- 化验数据管理模块
- 附件管理模块
- 金属价格管理模块
- 通知管理模块
- 考试结果管理模块
- 文章管理模块
- 文章分类管理模块
- 文章附件管理模块
- 权限管理模块
- 角色管理模块
- 应用管理模块
- 超级用户管理模块
- Excel导入导出功能
- 系统统计功能
- 系统配置管理
- 系统日志管理
- 数据备份与恢复

**技术特性**:
- RESTful API设计
- JWT身份认证
- 基于角色的权限控制
- 数据分页和搜索
- 文件上传下载
- 数据导入导出
- 接口限流保护
- 操作日志记录
- 错误处理机制
- API版本控制

---

**文档最后更新时间**: 2024-01-15 12:00:00

### 标记所有通知为已读

**接口地址**: `PUT /api/notifications/mark-all-read`

**权限要求**: `notification_read`

**响应示例**:
```json
{
  "success": true,
  "message": "成功标记 5 条通知为已读",
  "data": {
    "count": 5
  }
}
```

### 删除通知

**接口地址**: `DELETE /api/notifications/{notification_id}`

**权限要求**: `notification_delete`

**路径参数**:
- `notification_id` (integer): 通知ID

**响应示例**:
```json
{
  "success": true,
  "message": "通知删除成功"
}
```

### 获取未读通知数量

**接口地址**: `GET /api/notifications/unread-count`

**权限要求**: `notification_read`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "unread_count": 3
  }
}
```

### 管理员获取所有通知

**接口地址**: `GET /api/admin/notifications`

**权限要求**: `admin_required`

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）
- `user_id` (integer): 用户ID过滤（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 1,
        "user_id": 1,
        "title": "系统维护通知",
        "content": "系统将于今晚22:00-24:00进行维护",
        "is_read": false,
        "created_at": "2024-01-15T10:00:00",
        "read_at": null
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 5,
      "per_page": 10,
      "total": 45
    }
  }
}
```

---

## 物料事务管理接口

### 获取物料事务列表

**接口地址**: `GET /api/material-transactions`

**权限要求**: `material_transaction_read`

**查询参数**:
- `material_id` (integer): 物料ID过滤（可选）
- `transaction_type` (string): 事务类型过滤（入库/出库）（可选）
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": 1,
        "material_id": 1,
        "material_name": "锌精矿",
        "transaction_type": "入库",
        "quantity": 1000.0,
        "unit": "吨",
        "unit_price": 15000.0,
        "total_amount": 15000000.0,
        "transaction_date": "2024-01-15",
        "warehouse": "1号仓库",
        "operator": "张三",
        "remarks": "正常入库"
      }
    ],
    "pagination": {
      "total": 100,
      "pages": 5,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 创建物料事务

**接口地址**: `POST /api/material-transactions`

**权限要求**: `material_transaction_create`

**请求参数**:
```json
{
  "material_id": 1,
  "transaction_type": "入库",
  "quantity": 1000.0,
  "unit": "吨",
  "unit_price": 15000.0,
  "transaction_date": "2024-01-15",
  "warehouse": "1号仓库",
  "operator": "张三",
  "remarks": "正常入库"
}
```

### 获取物料库存统计

**接口地址**: `GET /api/material-transactions/inventory`

**权限要求**: `material_transaction_read`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "material_id": 1,
      "material_name": "锌精矿",
      "total_in": 5000.0,
      "total_out": 3000.0,
      "current_stock": 2000.0,
      "unit": "吨",
      "last_transaction_date": "2024-01-15"
    }
  ]
}
```

---

## 生产记录管理接口

### 获取生产记录列表

**接口地址**: `GET /api/production-records`

**权限要求**: `production_record_read`

**查询参数**:
- `product_name` (string): 产品名称过滤（可选）
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "id": 1,
        "production_date": "2024-01-15",
        "product_name": "锌锭",
        "batch_number": "ZD20240115001",
        "planned_quantity": 100.0,
        "actual_quantity": 98.5,
        "unit": "吨",
        "quality_grade": "一级品",
        "operator": "李四",
        "supervisor": "王五",
        "equipment": "1号生产线",
        "remarks": "正常生产",
        "created_at": "2024-01-15T16:00:00",
        "updated_at": "2024-01-15T16:00:00"
      }
    ],
    "pagination": {
      "total": 200,
      "pages": 10,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 创建生产记录

**接口地址**: `POST /api/production-records`

**权限要求**: `production_record_create`

**请求参数**:
```json
{
  "production_date": "2024-01-15",
  "product_name": "锌锭",
  "batch_number": "ZD20240115001",
  "planned_quantity": 100.0,
  "actual_quantity": 98.5,
  "unit": "吨",
  "quality_grade": "一级品",
  "operator": "李四",
  "supervisor": "王五",
  "equipment": "1号生产线",
  "remarks": "正常生产"
}
```

### 获取生产统计

**接口地址**: `GET /api/production-records/statistics`

**权限要求**: `production_record_read`

**查询参数**:
- `start_date` (string): 开始日期，格式：YYYY-MM-DD（可选）
- `end_date` (string): 结束日期，格式：YYYY-MM-DD（可选）
- `group_by` (string): 分组方式（day/month/year）（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_production": 2850.5,
    "total_planned": 3000.0,
    "completion_rate": 95.02,
    "daily_stats": [
      {
        "date": "2024-01-15",
        "planned": 100.0,
        "actual": 98.5,
        "completion_rate": 98.5
      }
    ]
  }
}
```

---

## 车辆管理接口

### 获取车辆列表

**接口地址**: `GET /api/vehicles`

**权限要求**: `vehicle_read`

**查询参数**:
- `search` (string): 搜索关键词（车牌号、车型等）（可选）
- `vehicle_type` (string): 车辆类型过滤（可选）
- `status` (string): 车辆状态过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "vehicles": [
      {
        "id": 1,
        "license_plate": "京A12345",
        "vehicle_type": "货车",
        "brand": "东风",
        "model": "天龙",
        "load_capacity": 30.0,
        "purchase_date": "2020-01-01",
        "purchase_price": 350000.0,
        "driver_name": "赵六",
        "driver_phone": "13800138000",
        "status": "正常",
        "last_maintenance": "2024-01-01",
        "next_maintenance": "2024-04-01",
        "insurance_expiry": "2024-12-31",
        "annual_inspection": "2024-06-30",
        "remarks": "车况良好"
      }
    ],
    "pagination": {
      "total": 50,
      "pages": 3,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

### 创建车辆

**接口地址**: `POST /api/vehicles`

**权限要求**: `vehicle_create`

**请求参数**:
```json
{
  "license_plate": "京A12345",
  "vehicle_type": "货车",
  "brand": "东风",
  "model": "天龙",
  "load_capacity": 30.0,
  "purchase_date": "2020-01-01",
  "purchase_price": 350000.0,
  "driver_name": "赵六",
  "driver_phone": "13800138000",
  "status": "正常",
  "insurance_expiry": "2024-12-31",
  "annual_inspection": "2024-06-30",
  "remarks": "车况良好"
}
```

### 获取车辆维护提醒

**接口地址**: `GET /api/vehicles/maintenance-reminders`

**权限要求**: `vehicle_read`

**查询参数**:
- `days` (integer): 提前天数，默认为30天（可选）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "vehicle_id": 1,
      "license_plate": "京A12345",
      "reminder_type": "保险到期",
      "expiry_date": "2024-02-15",
      "days_remaining": 15,
      "is_overdue": false
    }
  ]
}
```

---

## 文章管理接口

### 获取文章列表

**接口地址**: `GET /api/articles`

**权限要求**: `article_read`

**查询参数**:
- `category_id` (integer): 分类ID过滤（可选）
- `status` (string): 文章状态过滤（可选）
- `search` (string): 搜索关键词（标题、内容）（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "articles": [
      {
        "id": 1,
        "title": "公司新闻标题",
        "summary": "文章摘要内容",
        "content": "文章详细内容",
        "category_id": 1,
        "category_name": "公司新闻",
        "author_id": 1,
        "author_name": "管理员",
        "status": "已发布",
        "view_count": 100,
        "is_featured": false,
        "published_at": "2024-01-15T10:00:00",
        "created_at": "2024-01-15T09:00:00",
        "updated_at": "2024-01-15T10:00:00"
      }
    ],
    "pagination": {
      "total": 50,
      "pages": 5,
      "current_page": 1,
      "per_page": 10
    }
  }
}
```

### 获取文章详情

**接口地址**: `GET /api/articles/{article_id}`

**权限要求**: `article_read`

**路径参数**:
- `article_id` (integer): 文章ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "公司新闻标题",
    "summary": "文章摘要内容",
    "content": "文章详细内容",
    "category_id": 1,
    "category_name": "公司新闻",
    "author_id": 1,
    "author_name": "管理员",
    "status": "已发布",
    "view_count": 101,
    "is_featured": false,
    "published_at": "2024-01-15T10:00:00",
    "created_at": "2024-01-15T09:00:00",
    "updated_at": "2024-01-15T10:00:00",
    "attachments": [
      {
        "id": 1,
        "file_name": "附件.pdf",
        "file_path": "/uploads/articles/attachment.pdf",
        "file_size": 1024000
      }
    ]
  }
}
```

### 创建文章

**接口地址**: `POST /api/articles`

**权限要求**: `article_create`

**请求参数**:
```json
{
  "title": "文章标题",
  "summary": "文章摘要",
  "content": "文章内容",
  "category_id": 1,
  "status": "草稿",
  "is_featured": false
}
```

### 获取文章分类

**接口地址**: `GET /api/article-categories`

**权限要求**: `article_read`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "公司新闻",
      "description": "公司相关新闻",
      "sort_order": 1,
      "article_count": 25,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

---

## 超级用户管理接口

### 获取超级管理员列表

**接口地址**: `GET /api/superuser/list`

**权限要求**: `superuser_required`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "name": "系统管理员",
      "email": "admin@example.com",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 设置用户为超级管理员

**接口地址**: `POST /api/superuser/grant/{user_id}`

**权限要求**: `superuser_required`

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "success": true,
  "message": "用户已设置为超级管理员",
  "data": {
    "id": 2,
    "username": "user1",
    "is_superuser": true
  }
}
```

### 取消用户超级管理员权限

**接口地址**: `POST /api/superuser/revoke/{user_id}`

**权限要求**: `superuser_required`

**路径参数**:
- `user_id` (integer): 用户ID

**安全保护**:
- 不能取消最后一个超级管理员的权限
- 不能取消自己的超级管理员权限

**响应示例**:
```json
{
  "success": true,
  "message": "已取消用户的超级管理员权限",
  "data": {
    "id": 2,
    "username": "user1",
    "is_superuser": false
  }
}
```

**错误响应示例**:
```json
{
  "success": false,
  "message": "不能取消最后一个超级管理员的权限"
}
```

### 获取系统统计信息

**接口地址**: `GET /api/superuser/stats`

**权限要求**: `superuser_required`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_stats": {
      "total_users": 50,
      "active_users": 45,
      "new_users_today": 2
    },
    "employee_stats": {
      "total_employees": 100,
      "active_employees": 95,
      "new_employees_this_month": 5
    },
    "system_stats": {
      "database_size": "125.6 MB",
      "total_files": 1250,
      "storage_used": "2.3 GB"
    },
    "recent_activities": [
      {
        "action": "用户登录",
        "user": "张三",
        "timestamp": "2024-01-15T14:30:00"
      }
    ]
  }
}
```

### 获取系统日志

**接口地址**: `GET /api/superuser/logs`

**权限要求**: `superuser_required`

**查询参数**:
- `level` (string): 日志级别过滤（INFO/WARNING/ERROR）（可选）
- `start_date` (string): 开始日期（可选）
- `end_date` (string): 结束日期（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为50（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "level": "INFO",
        "message": "用户登录成功",
        "user_id": 1,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "timestamp": "2024-01-15T14:30:00"
      }
    ],
    "pagination": {
      "total": 1000,
      "pages": 20,
      "current_page": 1,
      "per_page": 50
    }
  }
}
```

### 系统备份

**接口地址**: `POST /api/superuser/backup`

**权限要求**: `superuser_required`

**请求参数**:
```json
{
  "backup_type": "full",
  "include_files": true,
  "description": "定期备份"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "备份任务已启动",
  "data": {
    "backup_id": "backup_20240115_143000",
    "estimated_time": "5-10分钟"
  }
}
```

### 获取备份列表

**接口地址**: `GET /api/superuser/backups`

**权限要求**: `superuser_required`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": "backup_20240115_143000",
      "type": "full",
      "size": "125.6 MB",
      "description": "定期备份",
      "status": "completed",
      "created_at": "2024-01-15T14:30:00",
      "file_path": "/backups/backup_20240115_143000.zip"
    }
  ]
}
```

---

## Excel导入导出接口

### 导出数据

**接口地址**: `POST /api/excel/export`

**权限要求**: 根据导出类型确定

**请求参数**:
```json
{
  "export_type": "employees",
  "filters": {
    "department_id": 1,
    "employment_status": "在职"
  },
  "columns": ["name", "employee_id", "department", "job_title"]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "导出任务已创建",
  "data": {
    "task_id": "export_20240115_143000",
    "download_url": "/api/excel/download/export_20240115_143000"
  }
}
```

### 导入数据

**接口地址**: `POST /api/excel/import`

**权限要求**: 根据导入类型确定

**请求类型**: `multipart/form-data`

**请求参数**:
- `file` (file): Excel文件
- `import_type` (string): 导入类型
- `options` (string): 导入选项（JSON格式）

**响应示例**:
```json
{
  "success": true,
  "message": "导入完成",
  "data": {
    "total_rows": 100,
    "success_rows": 95,
    "error_rows": 5,
    "errors": [
      {
        "row": 10,
        "error": "员工工号已存在"
      }
    ]
  }
}
```

### 下载模板

**接口地址**: `GET /api/excel/template/{template_type}`

**权限要求**: 根据模板类型确定

**路径参数**:
- `template_type` (string): 模板类型（employees/materials/customers等）

**响应**: Excel文件流

---

## 应用管理接口

### 获取应用信息

**接口地址**: `GET /api/application/info`

**权限要求**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "app_name": "管理系统",
    "version": "1.0.0",
    "build_time": "2024-01-15T10:00:00",
    "environment": "production",
    "database_status": "connected",
    "cache_status": "connected"
  }
}
```

### 健康检查

**接口地址**: `GET /api/application/health`

**权限要求**: 无

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "storage": "ok"
  }
}
```

---

## 错误码说明

### 通用错误码

- `AUTH_001`: 认证失败
- `AUTH_002`: Token已过期
- `AUTH_003`: 权限不足
- `PARAM_001`: 参数缺失
- `PARAM_002`: 参数格式错误
- `DATA_001`: 数据不存在
- `DATA_002`: 数据已存在
- `FILE_001`: 文件上传失败
- `FILE_002`: 文件格式不支持
- `SYS_001`: 系统内部错误

### 业务错误码

- `USER_001`: 用户名已存在
- `USER_002`: 密码格式错误
- `EMP_001`: 员工工号已存在
- `EMP_002`: 员工信息不完整
- `MAT_001`: 物料代码已存在
- `CONTRACT_001`: 合同编号已存在

---

## 接口版本控制

### 版本说明

- **v1.0**: 初始版本，包含基础功能
- **v1.1**: 增加移动端优化接口
- **v1.2**: 增加批量操作接口

### 版本使用

在请求头中添加版本信息：
```
API-Version: v1.0
```

或在URL中指定版本：
```
GET /api/v1/users
```

**接口地址**: `GET /api/admin/notifications`

**权限要求**: `notification_manage`

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）
- `user_id` (integer): 用户ID，筛选特定用户的通知（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 1,
        "title": "系统维护通知",
        "content": "系统将于今晚22:00-24:00进行维护",
        "user_id": 2,
        "username": "user1",
        "is_read": false,
        "created_at": "2024-01-15T10:00:00",
        "read_at": null
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 10,
      "per_page": 20,
      "total": 200
    }
  }
}
```

### 管理员创建通知

**接口地址**: `POST /api/admin/notifications`

**权限要求**: `notification_create`

**请求参数**:
```json
{
  "title": "通知标题",
  "content": "通知内容",
  "user_ids": [1, 2, 3],
  "send_to_all": false
}
```

**参数说明**:
- `title` (string): 通知标题，必填，最大200字符
- `content` (string): 通知内容，可选
- `user_ids` (array): 接收用户ID列表，当send_to_all为false时必填
- `send_to_all` (boolean): 是否发送给所有用户，默认false

**响应示例**:
```json
{
  "success": true,
  "message": "成功创建 3 条通知",
  "data": {
    "count": 3,
    "notification_ids": [10, 11, 12]
  }
}
```

### 管理员删除通知

**接口地址**: `DELETE /api/admin/notifications/{notification_id}`

**权限要求**: `notification_delete`

**路径参数**:
- `notification_id` (integer): 通知ID

**响应示例**:
```json
{
  "success": true,
  "message": "通知删除成功"
}
```

### 管理员广播通知

**接口地址**: `POST /api/admin/notifications/broadcast`

**权限要求**: `notification_create`

**请求参数**:
```json
{
  "title": "系统公告",
  "content": "重要系统更新通知"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "广播通知发送成功",
  "data": {
    "count": 50,
    "title": "系统公告"
  }
}
```

---

## 数据模型

### User（用户）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 用户ID | 主键，自增 |
| username | String(64) | 用户名 | 唯一，索引 |
| password_hash | String(128) | 密码哈希 | 不可为空 |
| name | String(50) | 真实姓名 | 可为空 |
| is_active | Boolean | 是否激活 | 默认True |
| is_superuser | Boolean | 超级管理员标识 | 默认False |
| created_at | DateTime | 创建时间 | 默认当前时间 |

### Material（物料）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 物料ID | 主键，自增 |
| name | String(100) | 物料名称 | 不可为空 |
| code | String(50) | 物料代码 | 唯一，不可为空 |
| full_name | String(200) | 物料全称 | 可为空 |
| purpose | String(20) | 用途 | 原料/辅料/产品/其他 |

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

### MaterialTransaction（物料交易记录）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 交易记录ID | 主键，自增 |
| date | Date | 交易日期 | 可为空 |
| customer | String(100) | 客户名称 | 可为空 |
| material_name | String(100) | 物料名称 | 可为空 |
| factory_id | Integer | 分厂ID | 可为空 |
| contract_number | String(50) | 合同编号 | 可为空 |
| transaction_type | String(20) | 交易类型 | 进厂/出厂 |
| packaging | String(50) | 包装方式 | 可为空 |
| vehicle_number | String(20) | 车牌号 | 可为空 |
| shipped_quantity | Float | 发货数量 | 可为空 |
| received_quantity | Float | 收货数量 | 可为空 |
| water_content | Float | 水含量 | 可为空 |
| zinc_content | Float | 锌含量 | 可为空 |
| lead_content | Float | 铅含量 | 可为空 |
| chlorine_content | Float | 氯含量 | 可为空 |
| fluorine_content | Float | 氟含量 | 可为空 |
| remarks | Text | 备注 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### ProductionRecord（生产记录）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 生产记录ID | 主键，自增 |
| date | Date | 生产日期 | 不可为空 |
| factory_id | Integer | 分厂ID | 外键 |
| shift | String(20) | 班次 | 可为空 |
| product_name | String(100) | 产品名称 | 可为空 |
| production_quantity | Float | 生产数量 | 可为空 |
| quality_grade | String(20) | 质量等级 | 可为空 |
| operator | String(50) | 操作员 | 可为空 |
| remarks | Text | 备注 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Employee（员工）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 员工ID | 主键，自增 |
| user_id | Integer | 用户ID | 外键，可为空 |
| employee_id | String(20) | 员工编号 | 唯一，不可为空 |
| name | String(50) | 姓名 | 不可为空 |
| gender | String(10) | 性别 | 可为空 |
| birth_date | Date | 出生日期 | 可为空 |
| id_card | String(18) | 身份证号 | 可为空 |
| phone | String(20) | 电话号码 | 可为空 |
| email | String(100) | 邮箱 | 可为空 |
| address | String(200) | 地址 | 可为空 |
| department_id | Integer | 部门ID | 外键 |
| position | String(50) | 职位 | 可为空 |
| hire_date | Date | 入职日期 | 可为空 |
| status | String(20) | 状态 | 在职/离职，默认在职 |
| avatar | String(200) | 头像路径 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Vehicle（车辆）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 车辆ID | 主键，自增 |
| plate_number | String(20) | 车牌号 | 唯一，不可为空 |
| brand | String(50) | 品牌 | 可为空 |
| model | String(50) | 型号 | 可为空 |
| vehicle_type | String(20) | 车辆类型 | 可为空 |
| load_capacity | Float | 载重量 | 可为空 |
| purchase_date | Date | 购买日期 | 可为空 |
| status | String(20) | 状态 | 正常/维修/报废，默认正常 |
| remarks | Text | 备注 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Role（角色）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 角色ID | 主键，自增 |
| name | String(64) | 角色名称 | 唯一，不可为空 |
| description | String(255) | 角色描述 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Permission（权限）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 权限ID | 主键，自增 |
| name | String(64) | 权限名称 | 唯一，不可为空 |
| description | String(255) | 权限描述 | 可为空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### Article（文章）

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 文章ID | 主键，自增 |
| title | String(200) | 文章标题 | 不可为空 |
| content | Text | 文章内容 | 可为空 |
| summary | Text | 文章摘要 | 可为空 |
| author_id | Integer | 作者ID | 外键 |
| category_id | Integer | 分类ID | 外键，可为空 |
| status | String(20) | 状态 | 草稿/已发布/已归档，默认草稿 |
| is_featured | Boolean | 是否推荐 | 默认False |
| view_count | Integer | 浏览次数 | 默认0 |
| published_at | DateTime | 发布时间 | 可为空 |
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
| article_read | 文章查看 | 查看文章信息 |
| article_create | 文章创建 | 创建新文章 |
| article_update | 文章更新 | 更新文章信息 |
| article_delete | 文章删除 | 删除文章 |
| article_publish | 文章发布 | 发布文章 |
| article_manage | 文章管理 | 管理所有文章 |
| article_category_read | 文章分类查看 | 查看文章分类 |
| article_category_create | 文章分类创建 | 创建文章分类 |
| article_category_update | 文章分类更新 | 更新文章分类 |
| article_category_delete | 文章分类删除 | 删除文章分类 |

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