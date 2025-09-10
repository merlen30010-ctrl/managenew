# uni-app 管理系统

## 项目介绍
这是一个基于uni-app开发的管理系统，支持多端运行（H5、小程序、App）。

## 项目结构
```
uniapp/
├── pages/              # 页面目录
│   ├── index/          # 首页
│   ├── login/          # 登录页
│   ├── dashboard/      # 仪表盘
│   ├── profile/        # 个人中心
│   └── vehicle/        # 办公用车
├── components/         # 组件目录
├── api/                # API接口封装
├── utils/              # 工具类
├── static/             # 静态资源
├── App.vue             # 应用入口
├── main.js             # 主入口
├── pages.json          # 页面配置
├── manifest.json       # 应用配置
├── uni.scss            # 全局样式
└── vue.config.js       # webpack配置
```

## 运行项目

### 在HBuilderX中运行
1. 打开HBuilderX
2. 导入项目：`文件` -> `导入` -> `从本地目录导入`，选择 `uniapp` 目录
3. 点击工具栏的 `运行` 按钮（绿色三角形）
4. 选择运行到浏览器或模拟器

### 启动后端服务
确保Flask后端服务已启动：
```bash
cd ../backend
python run.py
```

## 项目特点
- 基于Vue3 + uni-app开发
- 支持多端运行
- 响应式设计
- 统一的API封装
- JWT token认证

## 注意事项
- 首次运行需要安装依赖：`npm install`
- 确保后端服务运行在 `http://localhost:5000`
- 如遇到编译问题，请检查HBuilderX是否支持Vue3