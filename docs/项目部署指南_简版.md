# Factor Update Model 部署指南

## 项目结构

```
factor_update_model/
├── factor_update_main.py          # 主入口（支持 --no-sql, --date）
├── src/                           # 源代码
│   ├── __init__.py
│   ├── config_loader.py           # 配置加载器
│   ├── factor_update/             # 因子数据更新
│   │   ├── __init__.py
│   │   ├── factor_update.py
│   │   └── factor_preparing.py
│   ├── timeseries_update/         # 时间序列更新
│   │   ├── __init__.py
│   │   └── time_series_data_update.py
│   ├── time_tools/                # 时间工具
│   │   ├── __init__.py
│   │   └── time_tools.py
│   ├── global_setting/            # 全局配置
│   │   ├── __init__.py
│   │   └── global_dic.py
│   └── setup_logger/              # 日志设置
│       ├── __init__.py
│       └── logger_setup.py
├── config/                        # 集中配置
│   ├── config.yaml                # 主配置（需创建）
│   ├── config.yaml.example        # 配置模板
│   ├── config_path/
│   │   └── data_update_path_config.xlsx
│   └── config_project/
│       ├── sql_connection.yaml.example
│       └── dataUpdate_sql.yaml.example
├── scripts/                       # 部署脚本
│   ├── run_factor_update.bat
│   └── setup_scheduled_task.bat
├── tests/                         # 测试
├── logs/                          # 日志
├── requirements.txt
├── pytest.ini
└── .gitignore
```

## 环境要求

- Python 3.8+
- Windows / Linux / macOS

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository_url>
cd factor_update_model
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 设置环境变量

**Windows:**
```cmd
set GLOBAL_TOOLSFUNC_new=D:\path\to\global_tools
```

**Linux/macOS:**
```bash
export GLOBAL_TOOLSFUNC_new=/path/to/global_tools
```

建议将此环境变量添加到系统环境变量中。

### 4. 配置文件

1. 复制主配置模板:
   ```bash
   cp config/config.yaml.example config/config.yaml
   ```

2. 复制 SQL 连接配置模板:
   ```bash
   cp config/config_project/sql_connection.yaml.example config/config_project/sql_connection.yaml
   ```

3. 编辑配置文件，填入实际的数据库连接信息。

## 使用方法

### 命令行参数

```bash
# 查看帮助
python factor_update_main.py --help

# 日常更新（自动计算日期，保存到数据库）
python factor_update_main.py

# 日常更新，不保存到数据库
python factor_update_main.py --no-sql

# 指定日期更新
python factor_update_main.py --date 2025-01-20

# 历史数据更新
python factor_update_main.py --history --start-date 2024-01-01 --end-date 2024-12-31

# 显示详细输出
python factor_update_main.py --verbose
```

### Windows 批处理脚本

```cmd
# 运行更新
scripts\run_factor_update.bat

# 带参数运行
scripts\run_factor_update.bat --no-sql
```

### 设置定时任务

以管理员权限运行:
```cmd
scripts\setup_scheduled_task.bat
```

这将创建一个每天 18:30 运行的定时任务。

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/ -v -m unit

# 运行集成测试
pytest tests/ -v -m integration
```

## 日志

日志文件位于 `logs/` 目录:
- `logs/processing_log/` - 处理日志
- `logs/DataCheck_log/` - 数据检查日志

## 配置说明

### config.yaml

主配置文件，包含:
- 数据库连接信息
- 更新参数（回滚天数等）
- 日志配置

环境变量优先级高于配置文件。环境变量命名规则:
- `FACTOR_UPDATE_DATABASE_HOST` 对应 `database.host`
- `FACTOR_UPDATE_UPDATE_FACTOR_ROLLBACK_DAYS` 对应 `update.factor_rollback_days`

### data_update_path_config.xlsx

路径配置文件，定义输入输出路径。

## 故障排除

### 1. 环境变量未设置

错误信息: `EnvironmentError: 环境变量 GLOBAL_TOOLSFUNC_new 未设置`

解决方案: 设置环境变量指向 global_tools 模块路径。

### 2. 配置文件未找到

错误信息: `配置文件未找到`

解决方案: 确保 `config/config_path/data_update_path_config.xlsx` 存在。

### 3. 数据库连接失败

检查 `config/config_project/sql_connection.yaml` 中的数据库连接信息。

## 迁移说明

如果从旧版本迁移，需要注意:

1. 源代码已移动到 `src/` 目录
2. 配置文件已移动到 `config/` 目录
3. import 路径已更改为 `src.xxx` 格式

旧目录仍保留，可在确认新版本正常工作后手动删除:
- `FactorData_update/`
- `TimeSeries_update/`
- `Time_tools/`
- `global_setting/`
- `setup_logger/`
- `config_project/`
- `config_path/`
