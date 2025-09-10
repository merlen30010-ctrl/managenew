@echo off
echo 正在启动管理系统项目...

echo.
echo 1. 启动Flask后端服务...
cd backend
start "Flask Backend" cmd /k "python run.py"

echo.
echo 2. 启动uni-app前端开发服务...
cd ..\uniapp
start "uni-app Frontend" cmd /k "echo 请在HBuilderX中打开项目并运行"

echo.
echo 项目启动完成！
echo Flask后端默认运行在: http://localhost:5000
echo 请在HBuilderX中运行uni-app项目
pause