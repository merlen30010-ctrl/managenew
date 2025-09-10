# 系统备份与恢复指南

## 备份说明

### 自动备份
系统已创建完整的安全备份，包含以下内容：

#### 备份位置
- **备份目录**: `E:\backups\20250910-102054\`
- **压缩文件**: `E:\backups\20250910-102054.zip` (约50MB)

#### 备份内容
1. **代码文件** - 完整的项目代码（排除虚拟环境和缓存文件）
2. **数据库文件** - management.db（如果存在）
3. **配置文件** - .env, config.py, requirements.txt等
4. **Git信息** - 分支信息、提交历史、远程仓库配置

#### Git版本控制
- 创建了备份分支: `backup/stable-20250910-101912`
- 创建了稳定版本标签: `v1.0-stable`

## 备份脚本使用

### 创建新备份
```powershell
# 使用默认设置创建备份
.\backup_system.ps1

# 指定备份路径
.\backup_system.ps1 -BackupPath "D:\MyBackups"
```

### 恢复系统
```powershell
# 从备份目录恢复
.\restore_system.ps1 -BackupPath "E:\backups\20250910-102054"

# 从压缩文件恢复
.\restore_system.ps1 -BackupPath "E:\backups\20250910-102054.zip"

# 恢复到指定目录
.\restore_system.ps1 -BackupPath "E:\backups\20250910-102054" -RestorePath "D:\NewProject"
```

## 安全策略

### 多重保护
1. **Git版本控制** - 代码历史完整保存
2. **本地备份** - 完整系统快照
3. **分支隔离** - 实验性开发不影响主分支
4. **标签标记** - 重要版本节点标记

### 试错开发流程
1. **主分支保护** - main分支保持稳定状态
2. **实验分支** - 为移动端开发创建独立分支
3. **快速回滚** - 可随时回到v1.0-stable版本
4. **并行开发** - 可同时尝试多种技术方案

## 恢复步骤

### 完整恢复流程
1. 运行恢复脚本
2. 创建虚拟环境: `python -m venv venv_new`
3. 激活虚拟环境: `venv_new\Scripts\activate`
4. 安装依赖: `pip install -r requirements.txt`
5. 初始化数据库: `python init_db.py`
6. 启动应用: `python run.py`

### Git版本恢复
```bash
# 回到稳定版本
git checkout v1.0-stable

# 或切换到备份分支
git checkout backup/stable-20250910-101912

# 创建新的工作分支
git checkout -b mobile-development
```

## 注意事项

1. **备份文件安全** - 请妥善保存备份文件，建议额外备份到云存储
2. **环境变量** - 恢复后检查.env文件中的配置是否正确
3. **数据库** - 如果数据库有重要数据更新，请手动备份最新的management.db
4. **网络连接** - 当前GitHub连接有问题，建议稍后推送代码到远程仓库

## 移动端开发建议

基于当前备份，可以安全地进行以下实验：

1. **微信小程序开发** - 创建 `mobile/wechat-miniprogram` 分支
2. **Flutter应用开发** - 创建 `mobile/flutter-app` 分支
3. **React Native开发** - 创建 `mobile/react-native` 分支

每个方案都可以独立开发和测试，不会影响主系统的稳定性。