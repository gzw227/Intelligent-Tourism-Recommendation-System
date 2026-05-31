@echo off
chcp 65001 >nul
echo ============================================
echo   智能旅游推荐系统 - 启动脚本
echo ============================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/4] 安装后端依赖...
pip install -r requirements.txt -q

echo.
echo [3/4] 安装前端依赖...
cd frontend
if not exist node_modules (
    echo 正在安装前端依赖，请稍候...
    npm install
) else (
    echo 前端依赖已安装
)
cd ..

echo.
echo ============================================
echo   启动说明
echo ============================================
echo.
echo 请按以下步骤启动系统：
echo.
echo 步骤1: 确保MySQL已启动，并创建数据库
echo   mysql -u root -p123456 -e "CREATE DATABASE IF NOT EXISTS travel_recommend DEFAULT CHARSET utf8mb4;"
echo.
echo 步骤2: 初始化数据库（建表+导入数据）
echo   python -m backend.init_db
echo.
echo 步骤3: 训练推荐模型
echo   python -m algorithms.train
echo.
echo 步骤4: 启动后端服务（终端1）
echo   python -m backend.main
echo.
echo 步骤5: 启动前端服务（终端2）
echo   cd frontend ^&^& npm run dev
echo.
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:3000
echo API文档:  http://localhost:8000/docs
echo.
pause
