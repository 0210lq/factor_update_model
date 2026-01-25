@echo off
REM ============================================
REM Factor Update Model - Windows 启动脚本
REM ============================================
REM
REM 用法:
REM   run_factor_update.bat              # 日常更新
REM   run_factor_update.bat --no-sql     # 不保存到数据库
REM   run_factor_update.bat --date 2025-01-20  # 指定日期
REM
REM 请确保:
REM   1. 已安装 Python 3.8+
REM   2. 已安装所有依赖: pip install -r requirements.txt
REM   3. 已设置环境变量 GLOBAL_TOOLSFUNC_new
REM   4. 已配置 config/config.yaml
REM
REM ============================================

setlocal

REM 设置代码页为 UTF-8
chcp 65001 > nul

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
REM 获取项目根目录 (scripts 的上级目录)
for %%I in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fI

REM 切换到项目根目录
cd /d "%PROJECT_ROOT%"

REM 检查环境变量
if not defined GLOBAL_TOOLSFUNC_new (
    echo [ERROR] 环境变量 GLOBAL_TOOLSFUNC_new 未设置
    echo 请设置该环境变量指向 global_tools 模块路径
    echo 例如: set GLOBAL_TOOLSFUNC_new=D:\path\to\global_tools
    pause
    exit /b 1
)

REM 检查 Python
where python > nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请确保已安装 Python 并添加到 PATH
    pause
    exit /b 1
)

REM 显示运行信息
echo ============================================
echo Factor Update Model
echo ============================================
echo 项目路径: %PROJECT_ROOT%
echo Python:
python --version
echo 运行参数: %*
echo 开始时间: %date% %time%
echo ============================================

REM 运行主程序
python factor_update_main.py %*

REM 检查运行结果
if errorlevel 1 (
    echo ============================================
    echo [ERROR] 程序运行失败，错误码: %errorlevel%
    echo 请检查日志文件: %PROJECT_ROOT%\logs\
    echo ============================================
    pause
    exit /b %errorlevel%
) else (
    echo ============================================
    echo [SUCCESS] 程序运行完成
    echo 结束时间: %date% %time%
    echo ============================================
)

endlocal
