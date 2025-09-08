#!/bin/bash

# Linux环境部署脚本
# 用于部署工厂管理系统到Linux服务器

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以root权限运行
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_info "检测到root权限"
    else
        log_warn "建议以root权限运行此脚本以确保安装所需软件包"
    fi
}

# 检查系统类型
check_system() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        log_info "检测到操作系统: $OS $VER"
    else
        log_error "无法检测操作系统类型"
        exit 1
    fi
}

# 安装依赖软件包
install_dependencies() {
    log_info "开始安装系统依赖"
    
    if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
        # Ubuntu/Debian系统
        apt-get update
        apt-get install -y python3 python3-pip python3-venv nodejs npm libreoffice
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]] || [[ $OS == *"Fedora"* ]]; then
        # CentOS/RHEL/Fedora系统
        if command -v dnf &> /dev/null; then
            dnf install -y python3 python3-pip nodejs npm libreoffice
        else
            yum install -y python3 python3-pip nodejs npm libreoffice
        fi
    else
        log_warn "未知的Linux发行版，请手动安装以下软件包："
        echo "  - Python 3.8+"
        echo "  - pip"
        echo "  - Node.js 14+"
        echo "  - npm"
        echo "  - LibreOffice"
        read -p "确认已安装所需软件包后按回车继续..." </dev/tty
    fi
    
    log_info "系统依赖安装完成"
}

# 设置Python虚拟环境
setup_python_venv() {
    log_info "设置Python虚拟环境"
    
    python3 -m venv venv
    source venv/bin/activate
    
    log_info "升级pip"
    pip install --upgrade pip
    
    log_info "安装Python依赖"
    pip install -r requirements.txt
    
    deactivate
    log_info "Python虚拟环境设置完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库"
    source venv/bin/activate
    python init_db.py
    deactivate
    log_info "数据库初始化完成"
}

# 构建前端应用
build_frontend() {
    log_info "构建前端应用"
    
    if [[ -d "frontend" ]]; then
        cd frontend
        npm install
        npm run build
        cd ..
        log_info "前端应用构建完成"
    else
        log_warn "未找到frontend目录，跳过前端构建"
    fi
}

# 设置系统服务
setup_systemd_service() {
    log_info "设置系统服务"
    
    SERVICE_FILE="/etc/systemd/system/factory-manager.service"
    
    if [[ $EUID -eq 0 ]]; then
        # 创建systemd服务文件
        cat > $SERVICE_FILE << EOF
[Unit]
Description=Factory Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        
        # 重新加载systemd配置
        systemctl daemon-reload
        
        # 启用服务
        systemctl enable factory-manager.service
        
        log_info "系统服务已创建: $SERVICE_FILE"
        log_info "使用以下命令管理服务："
        echo "  启动服务: sudo systemctl start factory-manager"
        echo "  停止服务: sudo systemctl stop factory-manager"
        echo "  重启服务: sudo systemctl restart factory-manager"
        echo "  查看状态: sudo systemctl status factory-manager"
    else
        log_warn "需要root权限才能创建系统服务"
        log_info "手动运行应用："
        echo "  cd $(pwd)"
        echo "  source venv/bin/activate"
        echo "  python run.py"
    fi
}

# 显示部署完成信息
show_completion_info() {
    log_info "部署完成！"
    echo ""
    echo "访问地址："
    echo "  后端: http://localhost:5000"
    echo ""
    echo "管理命令："
    echo "  激活虚拟环境: source venv/bin/activate"
    echo "  运行应用: python run.py"
    echo "  停止应用: 按Ctrl+C"
    echo ""
    log_info "请确保防火墙允许5000端口的访问"
}

# 主函数
main() {
    log_info "开始部署工厂管理系统"
    
    check_root
    check_system
    install_dependencies
    setup_python_venv
    init_database
    build_frontend
    setup_systemd_service
    show_completion_info
    
    log_info "部署脚本执行完成"
}

# 执行主函数
main "$@"