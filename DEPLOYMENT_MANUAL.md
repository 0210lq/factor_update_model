# 因子数据更新项目完整部署手册

**创建时间**：2026-01-28
**适用版本**：v1.0
**预计完成时间**：1-2小时

---

## 目录

1. [环境准备](#1-环境准备)
2. [克隆项目](#2-克隆项目)
3. [配置数据库](#3-配置数据库)
4. [安装依赖](#4-安装依赖)
5. [测试数据库连接](#5-测试数据库连接)
6. [运行程序](#6-运行程序)
7. [验证数据](#7-验证数据)
8. [安全处理（可选）](#8-安全处理可选)
9. [配置文件整理（可选）](#9-配置文件整理可选)
10. [推送到GitHub](#10-推送到github)
11. [故障排除](#11-故障排除)

---

## 前置要求

### 必需条件

- Python 3.8+ 已安装
- Git 已安装
- 有权访问 MySQL 数据库
- 有权访问 `global_tools` 模块

### 数据库信息（示例）

```
Host: your-database-host
Port: 3306
User: your-username
Password: your-password
Database: your-database-name
```

### 环境变量

```bash
# global_tools 模块路径
GLOBAL_TOOLSFUNC_new=D:\globalToolsFunc_New  # Windows
# 或
GLOBAL_TOOLSFUNC_new=/path/to/globalToolsFunc_New  # Linux/Mac
```

---

## 1. 环境准备

### 1.1 检查 Python 版本

```bash
python --version
# 应该显示：Python 3.8 或更高版本
```

### 1.2 检查 Git

```bash
git --version
# 应该显示：git version 2.x.x
```

### 1.3 检查环境变量

```bash
# Windows
echo %GLOBAL_TOOLSFUNC_new%

# Linux/Mac
echo $GLOBAL_TOOLSFUNC_new
```

**预期输出**：应该显示 global_tools 的路径

如果未设置，请设置：

```bash
# Windows (临时)
set GLOBAL_TOOLSFUNC_new=D:\path\to\globalToolsFunc_New

# Windows (永久 - 系统环境变量)
# 在系统环境变量中添加 GLOBAL_TOOLSFUNC_new

# Linux/Mac (临时)
export GLOBAL_TOOLSFUNC_new=/path/to/globalToolsFunc_New

# Linux/Mac (永久 - 添加到 ~/.bashrc 或 ~/.zshrc)
echo 'export GLOBAL_TOOLSFUNC_new=/path/to/globalToolsFunc_New' >> ~/.bashrc
source ~/.bashrc
```

---

## 2. 克隆项目

### 2.1 克隆仓库

```bash
git clone https://github.com/0210lq/factor_update_model.git
cd factor_update_model
```

### 2.2 检查项目结构

```bash
ls -la
```

**预期输出**：应该看到以下目录和文件
```
config/
src/
factor_update_main.py
requirements.txt
README.md
...
```

---

## 3. 配置数据库

### 3.1 准备数据库信息

确保你有以下信息：
- 数据库主机地址（host）
- 端口号（port，通常是 3306）
- 用户名（user）
- 密码（password）
- 数据库名（database）

### 3.2 创建数据库配置文件

```bash
# 进入 config 目录
cd config

# 复制示例文件
cp database.yaml.example database.yaml
```

### 3.3 编辑配置文件

```bash
# Windows
notepad database.yaml

# Linux/Mac
vim database.yaml
# 或
nano database.yaml
```

**填入实际的数据库信息**：

```yaml
database:
  host: "your-actual-host"           # 替换为实际主机
  port: 3306
  user: "your-username"              # 替换为实际用户名
  password: "your-password"          # 替换为实际密码
  database: "your-database-name"     # 替换为实际数据库名
```

**示例**：
```yaml
database:
  host: "rm-cn-xxx.rds.aliyuncs.com"
  port: 3306
  user: "jzq"
  password: "Abcd1234#"
  database: "data_prepared_jzq"
```

### 3.4 返回项目根目录

```bash
cd ..
```

---

## 4. 安装依赖

### 4.1 查看依赖清单

```bash
cat requirements.txt
```

**预期内容**：
```
pandas>=2.0.0
numpy>=1.20.0
scipy>=1.10.0
PyMySQL>=1.0.0
SQLAlchemy>=1.4.0
PyYAML>=6.0
openpyxl>=3.0.0
xlrd>=2.0.0
python-dateutil>=2.8.0
pytest>=7.0.0
pytest-cov>=4.0.0
```

### 4.2 安装依赖包

```bash
pip install -r requirements.txt
```

**预期输出**：应该看到所有包成功安装

### 4.3 安装额外依赖（global_tools 需要）

```bash
pip install DBUtils
pip install reportlab
```

### 4.4 验证安装

```bash
pip list | grep -E "(pandas|PyMySQL|DBUtils|reportlab)"
```

**预期输出**：
```
DBUtils         3.1.2
pandas          2.1.4
PyMySQL         1.1.2
reportlab       4.4.9
```

---

## 5. 测试数据库连接

### 5.1 创建测试脚本

创建文件 `test_connection.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试数据库连接"""
import pymysql
import yaml

# 读取配置文件
with open('config/database.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    db_config = config['database']

print("=" * 60)
print("Testing Database Connection")
print("=" * 60)
print(f"Host: {db_config['host']}")
print(f"Port: {db_config['port']}")
print(f"User: {db_config['user']}")
print(f"Database: {db_config['database']}")
print("-" * 60)

try:
    # 连接数据库
    print("\nConnecting to database...")
    connection = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        connect_timeout=10
    )

    print("[OK] Connected successfully!")

    # 获取数据库信息
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"[OK] MySQL Version: {version[0]}")

        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()
        print(f"[OK] Current Database: {current_db[0]}")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"[OK] Found {len(tables)} tables")

        if len(tables) > 0:
            print("\nTables in database:")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table[0]}")

    connection.close()
    print("\n" + "=" * 60)
    print("[SUCCESS] Database connection test completed!")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] Connection failed!")
    print(f"Error: {str(e)}")
    print("=" * 60)
    exit(1)
```

### 5.2 运行测试

```bash
python test_connection.py
```

**预期输出**（成功）：
```
============================================================
Testing Database Connection
============================================================
Host: your-host
Port: 3306
User: your-username
Database: your-database
------------------------------------------------------------

Connecting to database...
[OK] Connected successfully!
[OK] MySQL Version: 8.0.36
[OK] Current Database: your-database
[OK] Found X tables

Tables in database:
  1. data_factorexposure
  2. data_factorreturn
  ...

============================================================
[SUCCESS] Database connection test completed!
============================================================
```

**如果失败**：检查数据库配置是否正确，参考 [故障排除](#11-故障排除)

---

## 6. 运行程序

### 6.1 查看帮助信息

```bash
python factor_update_main.py --help
```

**预期输出**：应该显示帮助信息，包括所有可用参数

### 6.2 测试运行（不写数据库）

```bash
python factor_update_main.py --no-sql --date 2025-01-20 --verbose
```

**说明**：
- `--no-sql`: 不写入数据库，仅生成 CSV 文件
- `--date 2025-01-20`: 指定日期
- `--verbose`: 显示详细输出

**预期输出**：
```
目标日期: 2025-01-20
保存到 SQL: False
因子更新开始日期: 2025-01-15
...
[完成] 因子数据更新完成
```

### 6.3 正式运行（写入数据库）

```bash
python factor_update_main.py --date 2025-01-20 --no-timeseries --verbose
```

**说明**：
- 移除 `--no-sql`：会写入数据库
- `--no-timeseries`：跳过时间序列更新（首次运行推荐）
- `--date 2025-01-20`: 指定日期

**预期输出**：
```
目标日期: 2025-01-20
保存到 SQL: True
Using lowercase table name: data_factorexposure
Using lowercase table name: data_factorreturn
...
2025-01-15
2025-01-16
2025-01-17
2025-01-20
[完成] 数据已写入数据库
```

**运行时间**：约 2-5 分钟（取决于数据量）

---

## 7. 验证数据

### 7.1 创建验证脚本

创建文件 `verify_data.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证数据库中的数据"""
import pymysql
import yaml

# 读取配置
with open('config/database.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    db_config = config['database']

# 要检查的表
tables = [
    'data_factorexposure',
    'data_factorreturn',
    'data_factorpool',
    'data_factorcov',
    'data_factorspecificrisk'
]

print("=" * 80)
print("Verifying Database Data")
print("=" * 80)

try:
    connection = pymysql.connect(**db_config)

    with connection.cursor() as cursor:
        for table in tables:
            # 获取记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]

            # 获取最新日期
            cursor.execute(f"SELECT DISTINCT valuation_date FROM {table} ORDER BY valuation_date DESC LIMIT 5")
            dates = [row[0] for row in cursor.fetchall()]

            print(f"\n{table}:")
            print(f"  Total records: {count:,}")
            print(f"  Latest dates: {', '.join(dates)}")

    connection.close()
    print("\n" + "=" * 80)
    print("[SUCCESS] Data verification completed!")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] Verification failed: {str(e)}")
    exit(1)
```

### 7.2 运行验证

```bash
python verify_data.py
```

**预期输出**：
```
================================================================================
Verifying Database Data
================================================================================

data_factorexposure:
  Total records: 45,208
  Latest dates: 2025-01-20, 2025-01-17, 2025-01-16, 2025-01-15

data_factorreturn:
  Total records: 8
  Latest dates: 2025-01-20, 2025-01-17, 2025-01-16, 2025-01-15

data_factorpool:
  Total records: 45,208
  Latest dates: 2025-01-20, 2025-01-17, 2025-01-16, 2025-01-15

data_factorcov:
  Total records: 320
  Latest dates: 2025-01-20, 2025-01-17, 2025-01-16, 2025-01-15

data_factorspecificrisk:
  Total records: 45,208
  Latest dates: 2025-01-20, 2025-01-17, 2025-01-16, 2025-01-15

================================================================================
[SUCCESS] Data verification completed!
================================================================================
```

### 7.3 数据量标准参考

| 表名 | 每日标准记录数 | 说明 |
|------|---------------|------|
| data_factorexposure | ~5,651 | 每只股票的因子暴露度 |
| data_factorreturn | 1 | 因子收益率（所有因子合并） |
| data_factorpool | ~5,651 | 有效股票列表 |
| data_factorcov | 40 | 因子协方差矩阵 |
| data_factorspecificrisk | ~5,651 | 每只股票的特异性风险 |

**注意**：股票数量会随市场变化略有波动，约 5,600-5,700 只。

---

## 8. 安全处理（可选）

**此步骤仅在需要将项目推送到 git 时执行**

### 8.1 检查敏感文件

```bash
git status
```

**应该看到**：
- `config/database.yaml` 不在列表中（已被忽略）
- 测试脚本不在列表中（已被忽略）

### 8.2 验证 .gitignore

```bash
git check-ignore -v config/database.yaml
git check-ignore -v test_connection.py
git check-ignore -v verify_data.py
```

**预期输出**：应该显示这些文件被 .gitignore 规则匹配

### 8.3 确认敏感信息已保护

```bash
# 搜索 git 跟踪的文件中是否包含密码
git grep -i "password" -- "*.yaml" "*.py"
```

**预期输出**：不应该显示包含真实密码的文件

---

## 9. 配置文件整理（可选）

**此步骤已经在最新版本中完成，新克隆的项目无需执行**

配置文件已统一到 `config/` 目录：

```
config/
├── app_config.yaml              # 主配置
├── database.yaml                # 数据库连接（本地）
├── database.yaml.example        # 示例
├── tables/                      # 表定义
│   └── dataUpdate_sql.yaml.example
└── legacy/                      # 旧格式配置
    ├── data_source_priority_config.xlsx
    ├── time_tools_config.xlsx
    └── data_update_path_config.xlsx
```

---

## 10. 推送到GitHub

### 10.1 检查 Git 状态

```bash
git status
```

**应该看到**：
- 只有新增的测试脚本（如果有）
- 敏感文件不在列表中

### 10.2 添加新文件（如果有）

```bash
# 如果你修改了代码或添加了文档
git add <your-files>
```

### 10.3 提交更改

```bash
git commit -m "chore: Setup project and verify functionality

- Configure database connection
- Test database connectivity
- Verify data writing functionality
- All tests passed"
```

### 10.4 推送到远程仓库

```bash
git push origin master
```

**如果需要身份验证**：
- 使用 GitHub Personal Access Token
- 或配置 SSH Key

---

## 11. 故障排除

### 11.1 数据库连接失败

**错误**：`OperationalError: (2013, 'Lost connection to MySQL server')`

**可能原因**：
1. 数据库主机地址错误
2. 端口不正确
3. 防火墙阻止连接
4. 数据库服务未启动

**解决方案**：
```bash
# 1. 检查配置文件
cat config/database.yaml

# 2. 测试网络连接
ping your-database-host

# 3. 测试端口
telnet your-database-host 3306

# 4. 检查数据库权限
# 联系数据库管理员确认用户权限
```

### 11.2 数据库名称错误

**错误**：`Access denied for user 'xxx'@'%' to database 'xxx'`

**解决方案**：
```bash
# 1. 连接数据库查看可用数据库
python -c "
import pymysql
conn = pymysql.connect(host='xxx', user='xxx', password='xxx')
cursor = conn.cursor()
cursor.execute('SHOW DATABASES')
print(cursor.fetchall())
"

# 2. 更新 config/database.yaml 使用正确的数据库名
```

### 11.3 环境变量未设置

**错误**：`EnvironmentError: 环境变量 GLOBAL_TOOLSFUNC_new 未设置`

**解决方案**：
```bash
# Windows
set GLOBAL_TOOLSFUNC_new=D:\path\to\globalToolsFunc_New

# Linux/Mac
export GLOBAL_TOOLSFUNC_new=/path/to/globalToolsFunc_New
```

### 11.4 缺少依赖包

**错误**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```bash
# 安装缺失的包
pip install xxx

# 或重新安装所有依赖
pip install -r requirements.txt
```

### 11.5 数据文件缺失

**错误**：`找不到数据源文件`

**解决方案**：
1. 确认数据文件存在于正确位置
2. 检查 `config/legacy/data_update_path_config.xlsx` 配置
3. 确认有访问数据目录的权限

### 11.6 程序运行慢

**可能原因**：
1. 数据量大
2. 网络连接慢
3. 数据库性能问题

**解决方案**：
```bash
# 1. 减少处理的日期范围
python factor_update_main.py --date 2025-01-20  # 只处理一天

# 2. 跳过时间序列更新
python factor_update_main.py --no-timeseries

# 3. 查看详细日志
python factor_update_main.py --verbose
```

---

## 12. 日常使用

### 12.1 日常更新

```bash
# 自动计算日期并更新
python factor_update_main.py

# 或指定日期
python factor_update_main.py --date 2025-01-21
```

### 12.2 历史数据补充

```bash
# 补充历史数据
python factor_update_main.py --history \
    --start-date 2024-01-01 \
    --end-date 2024-12-31
```

### 12.3 查看日志

```bash
# 查看处理日志
tail -f logs/processing_log/*.log

# 查看错误
grep ERROR logs/processing_log/*.log
```

### 12.4 定期任务设置

**Windows 任务计划程序**：
```batch
创建任务：
- 名称: Factor Update
- 触发器: 每天 18:30
- 操作: 运行程序
  程序: python
  参数: D:\path\to\factor_update_model\factor_update_main.py
  起始于: D:\path\to\factor_update_model
```

**Linux Cron**：
```bash
# 编辑 crontab
crontab -e

# 添加任务（每天 18:30 运行）
30 18 * * * cd /path/to/factor_update_model && /usr/bin/python3 factor_update_main.py >> /tmp/factor_update.log 2>&1
```

---

## 13. 验证清单

在完成部署后，请确认以下检查项：

- [ ] Python 版本 >= 3.8
- [ ] 环境变量 GLOBAL_TOOLSFUNC_new 已设置
- [ ] 所有依赖包已安装
- [ ] config/database.yaml 已配置
- [ ] 数据库连接测试通过
- [ ] 程序能够成功运行
- [ ] 数据已成功写入数据库
- [ ] 数据量符合预期标准
- [ ] 敏感文件已被 .gitignore 保护
- [ ] 文档已阅读理解

---

## 14. 参考文档

- `README.md` - 项目使用说明
- `SECURITY_SETUP.md` - 安全配置说明
- `CONFIG_REORGANIZATION_SUMMARY.md` - 配置文件整理报告
- `SESSION_SUMMARY.md` - 完整会话记录
- `DATABASE_COMPARISON_REPORT.md` - 数据验证报告

---

## 15. 联系方式

如遇到问题：
1. 查看本文档的故障排除部分
2. 查看项目 GitHub Issues
3. 查看项目文档目录

---

## 附录 A：完整命令清单

```bash
# 1. 克隆项目
git clone https://github.com/0210lq/factor_update_model.git
cd factor_update_model

# 2. 配置数据库
cp config/database.yaml.example config/database.yaml
# 编辑 config/database.yaml 填入实际值

# 3. 安装依赖
pip install -r requirements.txt
pip install DBUtils reportlab

# 4. 测试连接（创建并运行 test_connection.py）
python test_connection.py

# 5. 运行程序
python factor_update_main.py --date 2025-01-20 --no-timeseries --verbose

# 6. 验证数据（创建并运行 verify_data.py）
python verify_data.py

# 7. 提交更改
git add .
git commit -m "chore: Setup project"
git push origin master
```

---

## 附录 B：配置文件模板

### config/database.yaml

```yaml
database:
  host: "your-database-host"
  port: 3306
  user: "your-username"
  password: "your-password"
  database: "your-database-name"
```

---

## 附录 C：预期输出示例

### 成功运行的输出

```
目标日期: 2025-01-20
因子回滚天数: 3
时间序列回滚天数: 10
保存到 SQL: True
因子更新开始日期: 2025-01-15
时间序列更新开始日期: 2025-01-06

Using lowercase table name: data_factorexposure
Using lowercase table name: data_factorreturn
Using lowercase table name: data_factorpool
Using lowercase table name: data_factorcov
Using lowercase table name: data_factorspecificrisk

处理日期: 2025-01-15
处理日期: 2025-01-16
处理日期: 2025-01-17
处理日期: 2025-01-20

[完成] 因子数据更新完成
[完成] 数据已写入数据库
```

---

**文档版本**：v1.0
**最后更新**：2026-01-28
**维护者**：Claude Code
**状态**：✅ 完整可用
