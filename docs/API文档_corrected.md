# 管理系统 API 接口文档

## 概述

本文档描述了管理系统的RESTful API接口，包括用户管理、员工管理、物料管理、客户管理、部门管理、合同管理、化验数据、附件管理、金属价格、车辆管理等核心功能模块的API接口。

### 基础信息

- **基础URL**: `http://localhost:5000/api`
- **API版本**: v1.0
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: JWT Token

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

**权限要求**: `employee_read`

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

**接口地址**: `GET /api/employees/{employee_id}`

**权限要求**: 管理员或本人

**路径参数**:
- `employee_id` (integer): 员工ID

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

**权限要求**: `employee_create`

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

**接口地址**: `PUT /api/employees/{employee_id}`

**权限要求**: 管理员或本人

**路径参数**:
- `employee_id` (integer): 员工ID

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

**接口地址**: `DELETE /api/employees/{employee_id}`

**权限要求**: `employee_delete`

**路径参数**:
- `employee_id` (integer): 员工ID

**响应示例**:
```json
{
  "success": true,
  "message": "员工信息删除成功"
}
```

### 上传员工头像

**接口地址**: `POST /api/employees/{employee_id}/avatar`

**权限要求**: 管理员或本人

**路径参数**:
- `employee_id` (integer): 员工ID

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

**权限要求**: `employee_read`

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

### 生成员工工号

**接口地址**: `GET /api/employee/generate-id`

**权限要求**: `employee_create`

**响应示例**:
```json
{
  "success": true,
  "employee_id": "240001"
}
```

### 员工转正

**接口地址**: `POST /api/employee/{employee_id}/promote`

**权限要求**: `employee_update`

**路径参数**:
- `employee_id` (integer): 员工ID

**请求参数**:
```json
{
  "employee_id": "员工工号",
  "name": "员工姓名",
  "gender": "性别",
  "birth_date": "出生日期（格式：YYYY-MM-DD）",
  "id_card": "身份证号",
  "phone": "联系电话",
  "department_id": 1,
  "job_title": "职位",
  "hire_date": "入职日期（格式：YYYY-MM-DD）",
  "username": "系统用户名",
  "password": "系统密码"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "员工转正成功",
  "data": {
    "id": 1,
    "employee_id": "EMP001",
    "name": "张三",
    "department_id": 1,
    "job_title": "工程师",
    "employment_status": "在职"
  }
}
```

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
    "name": "技术部",
    "short_name": "技术部",
    "full_name": "技术部",
    "level": 2,
    "parent_id": null,
    "phone": "010-12345678"
  }
]
```

### 获取单个部门信息

**接口地址**: `GET /api/departments/{department_id}`

**权限要求**: `department_read`

**路径参数**:
- `department_id` (integer): 部门ID

**响应示例**:
```json
{
  "id": 1,
  "name": "技术部",
  "short_name": "技术部",
  "full_name": "技术部",
  "level": 2,
  "parent_id": null,
  "phone": "010-12345678"
}
```

### 创建部门

**接口地址**: `POST /api/departments`

**权限要求**: `department_create`

**请求参数**:
```json
{
  "name": "部门名称",
  "short_name": "部门简称（可选）",
  "full_name": "部门全称（可选）",
  "level": 2,
  "parent_id": 1,
  "phone": "联系电话（可选）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "name": "研发部",
  "short_name": "研发部",
  "full_name": "研发部",
  "level": 2,
  "parent_id": 1,
  "phone": "010-87654321"
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
  "name": "新部门名称",
  "short_name": "新部门简称",
  "full_name": "新部门全称",
  "level": 2,
  "parent_id": 1,
  "phone": "新联系电话"
}
```

**响应示例**:
```json
{
  "id": 2,
  "name": "新产品研发部",
  "short_name": "新产品部",
  "full_name": "新产品研发部",
  "level": 2,
  "parent_id": 1,
  "phone": "010-87654322"
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
  "message": "部门删除成功"
}
```

### 获取部门树形结构

**接口地址**: `GET /api/departments/tree`

**权限要求**: `department_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "总部",
    "level": 1,
    "children": [
      {
        "id": 2,
        "name": "技术部",
        "level": 2,
        "children": []
      }
    ]
  }
]
```

### 设置部门管理员

**接口地址**: `POST /api/departments/{department_id}/managers`

**权限要求**: `department_update`

**路径参数**:
- `department_id` (integer): 部门ID

**请求参数**:
```json
{
  "manager_ids": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "部门管理员设置成功"
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

**路径参数**:
- `material_id` (integer): 物料ID

**响应示例**:
```json
{
  "id": 1,
  "name": "锌精矿",
  "code": "ZN001",
  "full_name": "锌精矿原料",
  "purpose": "原料"
}
```

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

**响应示例**:
```json
{
  "id": 2,
  "name": "硫酸",
  "code": "H2SO4",
  "full_name": "98%浓硫酸",
  "purpose": "辅料"
}
```

### 更新物料信息

**接口地址**: `PUT /api/materials/{material_id}`

**权限要求**: `material_update`

**路径参数**:
- `material_id` (integer): 物料ID

**请求参数**:
```json
{
  "name": "新物料名称",
  "code": "新物料代码",
  "full_name": "新物料全称",
  "purpose": "新用途"
}
```

**响应示例**:
```json
{
  "id": 2,
  "name": "98%浓硫酸",
  "code": "H2SO4-98",
  "full_name": "98%浓硫酸",
  "purpose": "辅料"
}
```

### 删除物料

**接口地址**: `DELETE /api/materials/{material_id}`

**权限要求**: `material_delete`

**路径参数**:
- `material_id` (integer): 物料ID

**响应示例**:
```json
{
  "message": "物料删除成功"
}
```

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
  "id": 1,
  "name": "客户A",
  "code": "CUS001",
  "full_name": "客户A有限公司",
  "customer_type": "产品采购",
  "phone": "13800138000",
  "address": "北京市朝阳区"
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
  "customer_type": "客户类型（产品采购/原料供应/辅料供应/其他）",
  "phone": "联系电话（可选）",
  "address": "地址（可选）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "name": "客户B",
  "code": "CUS002",
  "full_name": "客户B有限公司",
  "customer_type": "原料供应",
  "phone": "13900139000",
  "address": "上海市浦东新区"
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
  "name": "新客户名称",
  "code": "新客户代码",
  "full_name": "新客户全称",
  "customer_type": "新客户类型",
  "phone": "新联系电话",
  "address": "新地址"
}
```

**响应示例**:
```json
{
  "id": 2,
  "name": "客户B有限公司",
  "code": "CUS002-B",
  "full_name": "客户B有限公司",
  "customer_type": "原料供应",
  "phone": "13900139001",
  "address": "上海市浦东新区陆家嘴"
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
  "message": "客户删除成功"
}
```

---

## 合同管理接口

### 获取合同列表

**接口地址**: `GET /api/contracts`

**权限要求**: `contract_read`

**查询参数**:
- `search` (string): 搜索关键词（合同编号、客户名称）（可选）
- `status` (string): 合同状态过滤（可选）
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
        "material_id": 1,
        "factory_id": 1,
        "responsible_id": 1,
        "sign_date": "2024-01-01",
        "expiry_date": "2024-12-31",
        "tax_rate": 13.0,
        "pricing_method": "固定价格",
        "coefficient": 1.0,
        "status": "执行"
      }
    ],
    "pagination": {
      "total": 20,
      "pages": 1,
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
  "id": 1,
  "contract_type": "产品销售",
  "contract_number": "CON2024001",
  "customer_id": 1,
  "material_id": 1,
  "factory_id": 1,
  "responsible_id": 1,
  "sign_date": "2024-01-01",
  "expiry_date": "2024-12-31",
  "tax_rate": 13.0,
  "pricing_method": "固定价格",
  "coefficient": 1.0,
  "status": "执行"
}
```

### 创建合同

**接口地址**: `POST /api/contracts`

**权限要求**: `contract_create`

**请求参数**:
```json
{
  "contract_type": "合同类型（产品销售/原料采购/辅料采购/其他）",
  "contract_number": "合同编号",
  "customer_id": 1,
  "material_id": 1,
  "factory_id": 1,
  "responsible_id": 1,
  "sign_date": "2024-01-01",
  "expiry_date": "2024-12-31",
  "tax_rate": 13.0,
  "pricing_method": "定价方式（固定价格/浮动价格）",
  "coefficient": 1.0,
  "status": "合同状态（执行/完成/终止）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "contract_type": "原料采购",
  "contract_number": "CON2024002",
  "customer_id": 2,
  "material_id": 1,
  "factory_id": 1,
  "responsible_id": 1,
  "sign_date": "2024-01-15",
  "expiry_date": "2024-12-31",
  "tax_rate": 13.0,
  "pricing_method": "浮动价格",
  "coefficient": 0.95,
  "status": "执行"
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
  "contract_type": "新合同类型",
  "contract_number": "新合同编号",
  "customer_id": 2,
  "material_id": 2,
  "factory_id": 2,
  "responsible_id": 2,
  "sign_date": "2024-02-01",
  "expiry_date": "2025-01-31",
  "tax_rate": 13.0,
  "pricing_method": "新定价方式",
  "coefficient": 1.0,
  "status": "新合同状态"
}
```

**响应示例**:
```json
{
  "id": 2,
  "contract_type": "原料采购",
  "contract_number": "CON2024002-A",
  "customer_id": 2,
  "material_id": 1,
  "factory_id": 1,
  "responsible_id": 1,
  "sign_date": "2024-01-15",
  "expiry_date": "2025-01-31",
  "tax_rate": 13.0,
  "pricing_method": "浮动价格",
  "coefficient": 0.95,
  "status": "执行"
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
  "message": "合同删除成功"
}
```

---

## 化验数据管理接口

### 获取化验数据列表

**接口地址**: `GET /api/assay-data`

**权限要求**: `assay_data_read`

**查询参数**:
- `search` (string): 搜索关键词（样品名称）（可选）
- `factory_id` (integer): 分厂ID过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
[
  {
    "id": 1,
    "sample_name": "样品A",
    "factory_id": 1,
    "water_content": 10.5,
    "zinc_content": 45.2,
    "lead_content": 0.8,
    "chlorine_content": 0.2,
    "fluorine_content": 0.1,
    "iron_content": 8.5,
    "silicon_content": 3.2,
    "sulfur_content": 1.8,
    "high_heat": 4500,
    "low_heat": 4200,
    "silver_content": 0.005,
    "recovery_rate": 95.5,
    "remarks": "正常样品",
    "created_by": 1,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

### 获取单个化验数据

**接口地址**: `GET /api/assay-data/{data_id}`

**权限要求**: `assay_data_read`

**路径参数**:
- `data_id` (integer): 化验数据ID

**响应示例**:
```json
{
  "id": 1,
  "sample_name": "样品A",
  "factory_id": 1,
  "water_content": 10.5,
  "zinc_content": 45.2,
  "lead_content": 0.8,
  "chlorine_content": 0.2,
  "fluorine_content": 0.1,
  "iron_content": 8.5,
  "silicon_content": 3.2,
  "sulfur_content": 1.8,
  "high_heat": 4500,
  "low_heat": 4200,
  "silver_content": 0.005,
  "recovery_rate": 95.5,
  "remarks": "正常样品",
  "created_by": 1,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### 创建化验数据

**接口地址**: `POST /api/assay-data`

**权限要求**: `assay_data_create`

**请求参数**:
```json
{
  "sample_name": "样品名称",
  "factory_id": 1,
  "water_content": 10.5,
  "zinc_content": 45.2,
  "lead_content": 0.8,
  "chlorine_content": 0.2,
  "fluorine_content": 0.1,
  "iron_content": 8.5,
  "silicon_content": 3.2,
  "sulfur_content": 1.8,
  "high_heat": 4500,
  "low_heat": 4200,
  "silver_content": 0.005,
  "recovery_rate": 95.5,
  "remarks": "备注信息（可选）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "sample_name": "样品B",
  "factory_id": 1,
  "water_content": 11.2,
  "zinc_content": 44.8,
  "lead_content": 0.9,
  "chlorine_content": 0.3,
  "fluorine_content": 0.1,
  "iron_content": 8.2,
  "silicon_content": 3.1,
  "sulfur_content": 1.9,
  "high_heat": 4480,
  "low_heat": 4180,
  "silver_content": 0.006,
  "recovery_rate": 95.2,
  "remarks": "样品B备注",
  "created_by": 1,
  "created_at": "2024-01-02T10:00:00",
  "updated_at": "2024-01-02T10:00:00"
}
```

### 更新化验数据

**接口地址**: `PUT /api/assay-data/{data_id}`

**权限要求**: `assay_data_update`

**路径参数**:
- `data_id` (integer): 化验数据ID

**请求参数**:
```json
{
  "sample_name": "新样品名称",
  "factory_id": 2,
  "water_content": 11.5,
  "zinc_content": 45.0,
  "lead_content": 0.85,
  "chlorine_content": 0.25,
  "fluorine_content": 0.12,
  "iron_content": 8.3,
  "silicon_content": 3.15,
  "sulfur_content": 1.85,
  "high_heat": 4490,
  "low_heat": 4190,
  "silver_content": 0.0055,
  "recovery_rate": 95.3,
  "remarks": "更新后的备注"
}
```

**响应示例**:
```json
{
  "id": 2,
  "sample_name": "样品B-更新",
  "factory_id": 1,
  "water_content": 11.5,
  "zinc_content": 45.0,
  "lead_content": 0.85,
  "chlorine_content": 0.25,
  "fluorine_content": 0.12,
  "iron_content": 8.3,
  "silicon_content": 3.15,
  "sulfur_content": 1.85,
  "high_heat": 4490,
  "low_heat": 4190,
  "silver_content": 0.0055,
  "recovery_rate": 95.3,
  "remarks": "更新后的备注",
  "created_by": 1,
  "created_at": "2024-01-02T10:00:00",
  "updated_at": "2024-01-02T11:00:00"
}
```

### 删除化验数据

**接口地址**: `DELETE /api/assay-data/{data_id}`

**权限要求**: `assay_data_delete`

**路径参数**:
- `data_id` (integer): 化验数据ID

**响应示例**:
```json
{
  "message": "化验数据删除成功"
}
```

---

## 物料进出厂管理接口

### 获取物料进出厂记录列表

**接口地址**: `GET /api/material-transactions`

**权限要求**: `material_transaction_read`

**查询参数**:
- `search` (string): 搜索关键词（客户、物料名称）（可选）
- `factory_id` (integer): 分厂ID过滤（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为20（可选）

**响应示例**:
```json
[
  {
    "id": 1,
    "date": "2024-01-01",
    "customer": "客户A",
    "material_name": "锌精矿",
    "factory_id": 1,
    "contract_number": "CON2024001",
    "transaction_type": "原料入库",
    "packaging": "吨袋",
    "vehicle_number": "京A12345",
    "shipped_quantity": 100.0,
    "received_quantity": 98.5,
    "water_content": 10.5,
    "zinc_content": 45.2,
    "lead_content": 0.8,
    "chlorine_content": 0.2,
    "fluorine_content": 0.1,
    "remarks": "正常入库",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

### 获取单个物料进出厂记录

**接口地址**: `GET /api/material-transactions/{transaction_id}`

**权限要求**: `material_transaction_read`

**路径参数**:
- `transaction_id` (integer): 记录ID

**响应示例**:
```json
{
  "id": 1,
  "date": "2024-01-01",
  "customer": "客户A",
  "material_name": "锌精矿",
  "factory_id": 1,
  "contract_number": "CON2024001",
  "transaction_type": "原料入库",
  "packaging": "吨袋",
  "vehicle_number": "京A12345",
  "shipped_quantity": 100.0,
  "received_quantity": 98.5,
  "water_content": 10.5,
  "zinc_content": 45.2,
  "lead_content": 0.8,
  "chlorine_content": 0.2,
  "fluorine_content": 0.1,
  "remarks": "正常入库",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### 创建物料进出厂记录

**接口地址**: `POST /api/material-transactions`

**权限要求**: `material_transaction_create`

**请求参数**:
```json
{
  "date": "2024-01-01",
  "customer": "客户名称",
  "material_name": "物料名称",
  "factory_id": 1,
  "contract_number": "合同编号（可选）",
  "transaction_type": "交易类型（原料入库/产品出库等）",
  "packaging": "包装方式（可选）",
  "vehicle_number": "车号（可选）",
  "shipped_quantity": 100.0,
  "received_quantity": 98.5,
  "water_content": 10.5,
  "zinc_content": 45.2,
  "lead_content": 0.8,
  "chlorine_content": 0.2,
  "fluorine_content": 0.1,
  "remarks": "备注信息（可选）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "date": "2024-01-02",
  "customer": "客户B",
  "material_name": "硫酸",
  "factory_id": 1,
  "contract_number": "CON2024002",
  "transaction_type": "辅料入库",
  "packaging": "桶装",
  "vehicle_number": "京B67890",
  "shipped_quantity": 50.0,
  "received_quantity": 49.8,
  "water_content": null,
  "zinc_content": null,
  "lead_content": null,
  "chlorine_content": null,
  "fluorine_content": null,
  "remarks": "辅料入库",
  "created_at": "2024-01-02T10:00:00",
  "updated_at": "2024-01-02T10:00:00"
}
```

### 更新物料进出厂记录

**接口地址**: `PUT /api/material-transactions/{transaction_id}`

**权限要求**: `material_transaction_update`

**路径参数**:
- `transaction_id` (integer): 记录ID

**请求参数**:
```json
{
  "date": "2024-01-02",
  "customer": "新客户名称",
  "material_name": "新物料名称",
  "factory_id": 2,
  "contract_number": "新合同编号",
  "transaction_type": "新交易类型",
  "packaging": "新包装方式",
  "vehicle_number": "新车号",
  "shipped_quantity": 105.0,
  "received_quantity": 103.2,
  "water_content": 11.0,
  "zinc_content": 45.0,
  "lead_content": 0.85,
  "chlorine_content": 0.25,
  "fluorine_content": 0.12,
  "remarks": "更新后的备注"
}
```

**响应示例**:
```json
{
  "id": 2,
  "date": "2024-01-02",
  "customer": "客户B-更新",
  "material_name": "98%浓硫酸",
  "factory_id": 1,
  "contract_number": "CON2024002-A",
  "transaction_type": "辅料入库",
  "packaging": "桶装",
  "vehicle_number": "京B67890",
  "shipped_quantity": 105.0,
  "received_quantity": 103.2,
  "water_content": 11.0,
  "zinc_content": 45.0,
  "lead_content": 0.85,
  "chlorine_content": 0.25,
  "fluorine_content": 0.12,
  "remarks": "更新后的备注",
  "created_at": "2024-01-02T10:00:00",
  "updated_at": "2024-01-02T11:00:00"
}
```

### 删除物料进出厂记录

**接口地址**: `DELETE /api/material-transactions/{transaction_id}`

**权限要求**: `material_transaction_delete`

**路径参数**:
- `transaction_id` (integer): 记录ID

**响应示例**:
```json
{
  "message": "物料进出厂记录删除成功"
}
```

---

## 金属价格管理接口

### 获取金属价格列表

**接口地址**: `GET /api/metal-prices`

**权限要求**: `metal_price_read`

**查询参数**:
- `metal_type` (string): 金属类型过滤（可选）
- `start_date` (string): 开始日期（格式：YYYY-MM-DD）（可选）
- `end_date` (string): 结束日期（格式：YYYY-MM-DD）（可选）
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）

**响应示例**:
```json
{
  "prices": [
    {
      "id": 1,
      "metal_type": "1#锌",
      "quote_date": "2024-01-01",
      "high_price": 22000,
      "low_price": 21500,
      "average_price": 21750,
      "price_change": 150
    }
  ],
  "total": 50,
  "pages": 5,
  "current_page": 1
}
```

### 获取单个金属价格记录

**接口地址**: `GET /api/metal-prices/{price_id}`

**权限要求**: `metal_price_read`

**路径参数**:
- `price_id` (integer): 价格记录ID

**响应示例**:
```json
{
  "id": 1,
  "metal_type": "1#锌",
  "quote_date": "2024-01-01",
  "high_price": 22000,
  "low_price": 21500,
  "average_price": 21750,
  "price_change": 150
}
```

### 创建金属价格记录

**接口地址**: `POST /api/metal-prices`

**权限要求**: `metal_price_create`

**请求参数**:
```json
{
  "metal_type": "金属类型（1#锌/0#锌等）",
  "quote_date": "2024-01-01",
  "high_price": 22000,
  "low_price": 21500,
  "average_price": 21750,
  "price_change": 150
}
```

**响应示例**:
```json
{
  "id": 2,
  "metal_type": "0#锌",
  "quote_date": "2024-01-01",
  "high_price": 23000,
  "low_price": 22500,
  "average_price": 22750,
  "price_change": 200
}
```

### 更新金属价格记录

**接口地址**: `PUT /api/metal-prices/{price_id}`

**权限要求**: `metal_price_update`

**路径参数**:
- `price_id` (integer): 价格记录ID

**请求参数**:
```json
{
  "metal_type": "新金属类型",
  "quote_date": "2024-01-02",
  "high_price": 22100,
  "low_price": 21600,
  "average_price": 21850,
  "price_change": 100
}
```

**响应示例**:
```json
{
  "id": 2,
  "metal_type": "0#锌",
  "quote_date": "2024-01-01",
  "high_price": 22100,
  "low_price": 21600,
  "average_price": 21850,
  "price_change": 100
}
```

### 删除金属价格记录

**接口地址**: `DELETE /api/metal-prices/{price_id}`

**权限要求**: `metal_price_delete`

**路径参数**:
- `price_id` (integer): 价格记录ID

**响应示例**:
```json
{
  "message": "金属价格记录删除成功"
}
```

---

## 文章管理接口

### 获取文章分类列表

**接口地址**: `GET /api/article-categories`

**权限要求**: 需要登录

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "公司新闻",
      "description": "公司最新动态",
      "sort_order": 1,
      "is_active": true
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
  "name": "分类名称",
  "description": "分类描述（可选）",
  "sort_order": 1,
  "is_active": true
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "分类创建成功",
  "data": {
    "id": 2,
    "name": "技术文章",
    "description": "技术分享",
    "sort_order": 2,
    "is_active": true
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
  "name": "新分类名称",
  "description": "新分类描述",
  "sort_order": 2,
  "is_active": true
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "分类更新成功",
  "data": {
    "id": 2,
    "name": "技术分享",
    "description": "技术经验分享",
    "sort_order": 2,
    "is_active": true
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
  "message": "分类删除成功"
}
```

### 获取文章列表

**接口地址**: `GET /api/articles`

**权限要求**: 需要登录

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）
- `category_id` (integer): 分类ID过滤（可选）
- `status` (string): 文章状态过滤（draft/published）（可选）
- `keyword` (string): 关键词搜索（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "articles": [
      {
        "id": 1,
        "title": "公司成立十周年庆典",
        "summary": "热烈庆祝公司成立十周年",
        "category_id": 1,
        "category_name": "公司新闻",
        "author": "管理员",
        "view_count": 150,
        "is_featured": false,
        "status": "published",
        "created_at": "2024-01-01T10:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 1,
      "per_page": 10,
      "total": 1,
      "has_prev": false,
      "has_next": false
    }
  }
}
```

### 获取文章详情

**接口地址**: `GET /api/articles/{article_id}`

**权限要求**: 需要登录

**路径参数**:
- `article_id` (integer): 文章ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "公司成立十周年庆典",
    "content": "文章正文内容...",
    "summary": "热烈庆祝公司成立十周年",
    "category_id": 1,
    "category_name": "公司新闻",
    "author": "管理员",
    "view_count": 151,
    "is_featured": false,
    "status": "published",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
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
  "content": "文章正文",
  "summary": "文章摘要（可选）",
  "category_id": 1,
  "is_featured": false,
  "status": "draft"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "文章创建成功",
  "data": {
    "id": 2,
    "title": "新技术应用分享",
    "summary": "分享新技术的应用经验",
    "category_id": 2,
    "category_name": "技术文章",
    "author": "管理员",
    "view_count": 0,
    "is_featured": false,
    "status": "draft",
    "created_at": "2024-01-02T10:00:00"
  }
}
```

### 更新文章

**接口地址**: `PUT /api/articles/{article_id}`

**权限要求**: `article_update`

**路径参数**:
- `article_id` (integer): 文章ID

**请求参数**:
```json
{
  "title": "新文章标题",
  "content": "新文章正文",
  "summary": "新文章摘要",
  "category_id": 2,
  "is_featured": true,
  "status": "published"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "文章更新成功",
  "data": {
    "id": 2,
    "title": "新技术应用实践",
    "content": "更新后的文章正文...",
    "summary": "分享新技术的实践应用经验",
    "category_id": 2,
    "category_name": "技术文章",
    "author": "管理员",
    "view_count": 0,
    "is_featured": true,
    "status": "published",
    "created_at": "2024-01-02T10:00:00",
    "updated_at": "2024-01-02T11:00:00"
  }
}
```

### 删除文章

**接口地址**: `DELETE /api/articles/{article_id}`

**权限要求**: `article_delete`

**路径参数**:
- `article_id` (integer): 文章ID

**响应示例**:
```json
{
  "success": true,
  "message": "文章删除成功"
}
```

---

## 车辆管理接口

### 获取车辆列表

**接口地址**: `GET /api/vehicles`

**权限要求**: `vehicle_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "plate_number": "京A12345",
    "brand": "东风",
    "model": "天龙",
    "color": "白色",
    "purchase_date": "2020-01-01",
    "status": "可用"
  }
]
```

### 获取单个车辆信息

**接口地址**: `GET /api/vehicles/{vehicle_id}`

**权限要求**: `vehicle_read`

**路径参数**:
- `vehicle_id` (integer): 车辆ID

**响应示例**:
```json
{
  "id": 1,
  "plate_number": "京A12345",
  "brand": "东风",
  "model": "天龙",
  "color": "白色",
  "purchase_date": "2020-01-01",
  "status": "可用"
}
```

### 创建车辆

**接口地址**: `POST /api/vehicles`

**权限要求**: `vehicle_create`

**请求参数**:
```json
{
  "license_plate": "车牌号",
  "brand": "品牌（可选）",
  "model": "型号（可选）",
  "color": "颜色（可选）",
  "purchase_date": "购买日期（格式：YYYY-MM-DD）（可选）",
  "status": "状态（可用/维修中/报废等）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "plate_number": "京B67890",
  "brand": "解放",
  "model": "J6",
  "color": "蓝色",
  "purchase_date": "2021-01-01",
  "status": "可用"
}
```

### 更新车辆信息

**接口地址**: `PUT /api/vehicles/{vehicle_id}`

**权限要求**: `vehicle_update`

**路径参数**:
- `vehicle_id` (integer): 车辆ID

**请求参数**:
```json
{
  "license_plate": "新车牌号",
  "brand": "新品牌",
  "model": "新型号",
  "color": "新颜色",
  "purchase_date": "新购买日期",
  "status": "新状态"
}
```

**响应示例**:
```json
{
  "id": 2,
  "plate_number": "京B67890-A",
  "brand": "一汽解放",
  "model": "J6P",
  "color": "天蓝色",
  "purchase_date": "2021-01-01",
  "status": "维修中"
}
```

### 删除车辆

**接口地址**: `DELETE /api/vehicles/{vehicle_id}`

**权限要求**: `vehicle_delete`

**路径参数**:
- `vehicle_id` (integer): 车辆ID

**响应示例**:
```json
{
  "message": "车辆删除成功"
}
```

### 获取车辆借还记录列表

**接口地址**: `GET /api/vehicle-usage-records`

**权限要求**: `vehicle_usage_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "borrower_id": 1,
    "borrow_time": "2024-01-01T08:00:00",
    "return_time": "2024-01-01T17:00:00",
    "borrow_mileage": 10000,
    "return_mileage": 10150,
    "purpose": "送货",
    "remarks": "正常归还"
  }
]
```

### 获取单个车辆借还记录

**接口地址**: `GET /api/vehicle-usage-records/{record_id}`

**权限要求**: `vehicle_usage_read`

**路径参数**:
- `record_id` (integer): 记录ID

**响应示例**:
```json
{
  "id": 1,
  "vehicle_id": 1,
  "borrower_id": 1,
  "borrow_time": "2024-01-01T08:00:00",
  "return_time": "2024-01-01T17:00:00",
  "borrow_mileage": 10000,
  "return_mileage": 10150,
  "purpose": "送货",
  "remarks": "正常归还"
}
```

### 创建车辆借还记录

**接口地址**: `POST /api/vehicle-usage-records`

**权限要求**: `vehicle_usage_create`

**请求参数**:
```json
{
  "vehicle_id": 1,
  "borrow_time": "2024-01-01T08:00:00",
  "borrow_mileage": 10000,
  "purpose": "用车目的",
  "remarks": "备注信息（可选）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "vehicle_id": 1,
  "borrower_id": 1,
  "borrow_time": "2024-01-02T08:00:00",
  "borrow_mileage": 10150,
  "purpose": "送货",
  "remarks": "新借车记录"
}
```

### 更新车辆借还记录

**接口地址**: `PUT /api/vehicle-usage-records/{record_id}`

**权限要求**: `vehicle_usage_update`

**路径参数**:
- `record_id` (integer): 记录ID

**请求参数**:
```json
{
  "return_time": "2024-01-02T17:00:00",
  "return_mileage": 10300,
  "remarks": "更新后的备注"
}
```

**响应示例**:
```json
{
  "id": 2,
  "vehicle_id": 1,
  "borrower_id": 1,
  "borrow_time": "2024-01-02T08:00:00",
  "return_time": "2024-01-02T17:00:00",
  "borrow_mileage": 10150,
  "return_mileage": 10300,
  "purpose": "送货",
  "remarks": "更新后的备注"
}
```

### 删除车辆借还记录

**接口地址**: `DELETE /api/vehicle-usage-records/{record_id}`

**权限要求**: `vehicle_usage_delete`

**路径参数**:
- `record_id` (integer): 记录ID

**响应示例**:
```json
{
  "message": "车辆借还记录删除成功"
}
```

### 获取车辆保养记录列表

**接口地址**: `GET /api/vehicle-maintenance-records`

**权限要求**: `vehicle_maintenance_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "maintenance_date": "2024-01-01",
    "maintenance_type": "定期保养",
    "cost": 1500.0,
    "service_provider": "4S店",
    "mileage": 10000,
    "next_maintenance_date": "2024-07-01",
    "remarks": "更换机油和滤芯"
  }
]
```

### 获取单个车辆保养记录

**接口地址**: `GET /api/vehicle-maintenance-records/{record_id}`

**权限要求**: `vehicle_maintenance_read`

**路径参数**:
- `record_id` (integer): 记录ID

**响应示例**:
```json
{
  "id": 1,
  "vehicle_id": 1,
  "maintenance_date": "2024-01-01",
  "maintenance_type": "定期保养",
  "cost": 1500.0,
  "service_provider": "4S店",
  "mileage": 10000,
  "next_maintenance_date": "2024-07-01",
  "remarks": "更换机油和滤芯"
}
```

### 创建车辆保养记录

**接口地址**: `POST /api/vehicle-maintenance-records`

**权限要求**: `vehicle_maintenance_create`

**请求参数**:
```json
{
  "vehicle_id": 1,
  "maintenance_date": "2024-01-01",
  "maintenance_type": "保养类型",
  "cost": 1500.0,
  "service_provider": "服务商",
  "mileage": 10000,
  "next_maintenance_date": "2024-07-01",
  "remarks": "备注信息（可选）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "vehicle_id": 1,
  "maintenance_date": "2024-01-02",
  "maintenance_type": "定期保养",
  "cost": 1600.0,
  "service_provider": "新4S店",
  "mileage": 10150,
  "next_maintenance_date": "2024-07-02",
  "remarks": "新保养记录"
}
```

### 更新车辆保养记录

**接口地址**: `PUT /api/vehicle-maintenance-records/{record_id}`

**权限要求**: `vehicle_maintenance_update`

**路径参数**:
- `record_id` (integer): 记录ID

**请求参数**:
```json
{
  "maintenance_date": "2024-01-03",
  "maintenance_type": "新保养类型",
  "cost": 1700.0,
  "service_provider": "新服务商",
  "mileage": 10200,
  "next_maintenance_date": "2024-07-03",
  "remarks": "更新后的备注"
}
```

**响应示例**:
```json
{
  "id": 2,
  "vehicle_id": 1,
  "maintenance_date": "2024-01-03",
  "maintenance_type": "新保养类型",
  "cost": 1700.0,
  "service_provider": "新服务商",
  "mileage": 10200,
  "next_maintenance_date": "2024-07-03",
  "remarks": "更新后的备注"
}
```

### 删除车辆保养记录

**接口地址**: `DELETE /api/vehicle-maintenance-records/{record_id}`

**权限要求**: `vehicle_maintenance_delete`

**路径参数**:
- `record_id` (integer): 记录ID

**响应示例**:
```json
{
  "message": "车辆保养记录删除成功"
}
```

### 获取车辆保险记录列表

**接口地址**: `GET /api/vehicle-insurance-records`

**权限要求**: `vehicle_insurance_read`

**响应示例**:
```json
[
  {
    "id": 1,
    "vehicle_id": 1,
    "insurance_company": "中国人保",
    "policy_number": "P123456789",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "premium": 5000.0,
    "coverage": "全险",
    "remarks": "年度保险"
  }
]
```

### 获取单个车辆保险记录

**接口地址**: `GET /api/vehicle-insurance-records/{record_id}`

**权限要求**: `vehicle_insurance_read`

**路径参数**:
- `record_id` (integer): 记录ID

**响应示例**:
```json
{
  "id": 1,
  "vehicle_id": 1,
  "insurance_company": "中国人保",
  "policy_number": "P123456789",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "premium": 5000.0,
  "coverage": "全险",
  "remarks": "年度保险"
}
```

### 创建车辆保险记录

**接口地址**: `POST /api/vehicle-insurance-records`

**权限要求**: `vehicle_insurance_create`

**请求参数**:
```json
{
  "vehicle_id": 1,
  "insurance_company": "保险公司",
  "policy_number": "保单号",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "premium": 5000.0,
  "coverage": "保险范围",
  "remarks": "备注信息（可选）"
}
```

**响应示例**:
```json
{
  "id": 2,
  "vehicle_id": 1,
  "insurance_company": "平安保险",
  "policy_number": "P987654321",
  "start_date": "2024-01-02",
  "end_date": "2025-01-01",
  "premium": 5200.0,
  "coverage": "全险",
  "remarks": "新保险记录"
}
```

### 更新车辆保险记录

**接口地址**: `PUT /api/vehicle-insurance-records/{record_id}`

**权限要求**: `vehicle_insurance_update`

**路径参数**:
- `record_id` (integer): 记录ID

**请求参数**:
```json
{
  "insurance_company": "新保险公司",
  "policy_number": "新保单号",
  "start_date": "2024-01-03",
  "end_date": "2025-01-02",
  "premium": 5300.0,
  "coverage": "新保险范围",
  "remarks": "更新后的备注"
}
```

**响应示例**:
```json
{
  "id": 2,
  "vehicle_id": 1,
  "insurance_company": "太平洋保险",
  "policy_number": "P112233445",
  "start_date": "2024-01-03",
  "end_date": "2025-01-02",
  "premium": 5300.0,
  "coverage": "全险+涉水险",
  "remarks": "更新后的备注"
}
```

### 删除车辆保险记录

**接口地址**: `DELETE /api/vehicle-insurance-records/{record_id}`

**权限要求**: `vehicle_insurance_delete`

**路径参数**:
- `record_id` (integer): 记录ID

**响应示例**:
```json
{
  "message": "车辆保险记录删除成功"
}
```

---

## 通知管理接口

### 获取通知列表

**接口地址**: `GET /api/notifications`

**权限要求**: `notification_read`

**查询参数**:
- `page` (integer): 页码，默认为1（可选）
- `per_page` (integer): 每页数量，默认为10（可选）
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
        "content": "系统将于今晚00:00-02:00进行维护",
        "is_read": false,
        "created_at": "2024-01-01T10:00:00",
        "read_at": null
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 1,
      "per_page": 10,
      "total": 1
    }
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
  "user_ids": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "成功创建 3 条通知",
  "data": {
    "count": 3
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
    "is_read": true,
    "read_at": "2024-01-01T11:00:00"
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

---

## Excel导入导出接口

### 下载Excel模板

**接口地址**: `GET /excel/template/{module_name}`

**权限要求**: 需要登录

**路径参数**:
- `module_name` (string): 模块名称（material_transaction/assay_data）

**响应示例**:
直接返回Excel文件下载

### 导入Excel数据

**接口地址**: `POST /excel/import/{module_name}`

**权限要求**: `excel_import`

**路径参数**:
- `module_name` (string): 模块名称（material_transaction/assay_data）

**请求参数**:
- `file` (file): Excel文件

**响应示例**:
```json
{
  "message": "数据导入成功",
  "imported_rows": 100
}
```

### 导出Excel数据

**接口地址**: `GET /excel/export/{module_name}`

**权限要求**: `excel_export`

**路径参数**:
- `module_name` (string): 模块名称（material_transaction/assay_data）

**响应示例**:
直接返回Excel文件下载

---

## 超级用户管理接口

### 获取超级管理员列表

**接口地址**: `GET /api/superuser/list`

**权限要求**: 超级管理员

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1
}
```

### 设置超级管理员

**接口地址**: `POST /api/superuser/set/{user_id}`

**权限要求**: 超级管理员

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "success": true,
  "message": "用户 admin 已设置为超级管理员",
  "data": {
    "id": 1,
    "username": "admin",
    "is_superuser": true
  }
}
```

### 取消超级管理员

**接口地址**: `POST /api/superuser/unset/{user_id}`

**权限要求**: 超级管理员

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "success": true,
  "message": "用户 test 的超级管理员权限已取消",
  "data": {
    "id": 2,
    "username": "test",
    "is_superuser": false
  }
}
```

### 检查用户超级管理员状态

**接口地址**: `GET /api/superuser/status/{user_id}`

**权限要求**: 超级管理员

**路径参数**:
- `user_id` (integer): 用户ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "is_superuser": true,
    "is_active": true,
    "roles": ["管理员"],
    "permission_count": 50
  }
}
```