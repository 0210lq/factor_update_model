@echo off
REM ============================================
REM Factor Update Model - Windows 定时任务配置
REM ============================================
REM
REM 此脚本用于创建 Windows 定时任务
REM 需要以管理员权限运行
REM
REM 默认配置:
REM   - 任务名称: FactorDataUpdate
REM   - 运行时间: 每天 18:30 (工作日收盘后)
REM   - 运行账户: 当前用户
REM
REM ============================================

setlocal EnableDelayedExpansion

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 请以管理员权限运行此脚本
    echo 右键点击脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

REM 设置代码页为 UTF-8
chcp 65001 > nul

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
REM 获取项目根目录
for %%I in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fI

REM 任务配置
set TASK_NAME=FactorDataUpdate
set RUN_TIME=18:30
set RUN_SCRIPT=%SCRIPT_DIR%run_factor_update.bat

echo ============================================
echo Factor Update Model - 定时任务配置
echo ============================================
echo 项目路径: %PROJECT_ROOT%
echo 任务名称: %TASK_NAME%
echo 运行时间: 每天 %RUN_TIME%
echo 运行脚本: %RUN_SCRIPT%
echo ============================================
echo.

REM 检查是否已存在同名任务
schtasks /query /tn "%TASK_NAME%" > nul 2>&1
if not errorlevel 1 (
    echo [WARNING] 任务 "%TASK_NAME%" 已存在
    set /p CONFIRM="是否删除并重新创建? (Y/N): "
    if /i "!CONFIRM!"=="Y" (
        schtasks /delete /tn "%TASK_NAME%" /f
        echo [INFO] 已删除旧任务
    ) else (
        echo [INFO] 取消操作
        pause
        exit /b 0
    )
)

REM 创建定时任务
echo [INFO] 正在创建定时任务...
schtasks /create /tn "%TASK_NAME%" /tr "\"%RUN_SCRIPT%\"" /sc daily /st %RUN_TIME% /ru "%USERNAME%" /rl HIGHEST /f

if errorlevel 1 (
    echo [ERROR] 创建定时任务失败
    pause
    exit /b 1
)

echo.
echo ============================================
echo [SUCCESS] 定时任务创建成功!
echo ============================================
echo.
echo 任务详情:
schtasks /query /tn "%TASK_NAME%" /v /fo list | findstr /i "TaskName Status"
echo.
echo 管理命令:
echo   查看任务: schtasks /query /tn "%TASK_NAME%"
echo   运行任务: schtasks /run /tn "%TASK_NAME%"
echo   停止任务: schtasks /end /tn "%TASK_NAME%"
echo   删除任务: schtasks /delete /tn "%TASK_NAME%" /f
echo ============================================

pause
endlocal
