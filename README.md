# 因子数据更新模块

自动化更新因子暴露度、收益率、协方差等数据，支持 JY/Wind 多数据源切换。

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量

```bash
# Windows
set GLOBAL_TOOLSFUNC_new=D:\path\to\global_tools

# Linux/Mac
export GLOBAL_TOOLSFUNC_new=/path/to/global_tools
```

### 3. 配置数据库连接

```bash
cd config

# 复制配置模板
copy database.yaml.example database.yaml

# 编辑配置文件，填入实际的数据库连接信息
# Windows: notepad database.yaml
# Linux/Mac: vim database.yaml
```

**必须配置的文件:**
| 文件 | 用途 |
|------|------|
| `config/database.yaml` | 数据库连接配置 |
| `config/tables/dataUpdate_sql.yaml.local` | 数据表结构和连接（从示例复制） |

**注意**：敏感配置文件（包含密码）不会被提交到git。

### 4. 运行

```bash
python factor_update_main.py
```

---

## 集成使用

### 作为模块导入

```python
from factor_update_main import FactorData_update_main, FactorData_history_update

# 日常更新 (自动计算日期)
FactorData_update_main(is_sql=True)

# 历史数据更新
FactorData_history_update(
    start_date='2024-01-01',
    end_date='2024-12-31',
    is_sql=True,
    include_timeseries=True
)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| is_sql | bool | True | 是否写入数据库 |
| start_date | str | - | 起始日期 (YYYY-MM-DD) |
| end_date | str | - | 结束日期 (YYYY-MM-DD) |
| include_timeseries | bool | True | 是否更新时间序列 |

### 集成到调度系统

```python
# 示例：集成到定时任务
import schedule
from factor_update_main import FactorData_update_main

def daily_update():
    FactorData_update_main(is_sql=True)

schedule.every().day.at("18:30").do(daily_update)
```

### 集成到 Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def run_factor_update():
    from factor_update_main import FactorData_update_main
    FactorData_update_main(is_sql=True)

dag = DAG('factor_update', schedule_interval='30 18 * * 1-5')
task = PythonOperator(
    task_id='update_factors',
    python_callable=run_factor_update,
    dag=dag
)
```

---

## 项目结构

```
factor_update_model/
├── factor_update_main.py       # 主入口
├── requirements.txt            # 依赖清单
├── src/                        # 源代码目录
│   ├── factor_update/          # 因子更新核心
│   ├── timeseries_update/      # 时间序列更新
│   ├── time_tools/             # 时间工具
│   ├── global_setting/         # 全局配置
│   ├── setup_logger/           # 日志模块
│   └── config/                 # 配置管理
├── config/                     # 配置文件目录
│   ├── app_config.yaml         # 主配置文件
│   ├── database.yaml           # 数据库连接（本地）
│   ├── database.yaml.example   # 数据库连接示例
│   ├── tables/                 # 表定义
│   │   └── dataUpdate_sql.yaml.example
│   └── legacy/                 # 旧格式配置（兼容）
│       ├── data_source_priority_config.xlsx
│       ├── time_tools_config.xlsx
│       └── data_update_path_config.xlsx
├── docs/                       # 文档
│   ├── 部署指南.md
│   └── 数据需求清单.md
└── scripts/                    # 工具脚本
    ├── generate_test_data.py   # 生成测试数据
    └── run_test.py             # 运行测试
```

---

## 功能模块

| 模块 | 功能 | 输出文件 |
|------|------|----------|
| 因子暴露度 | 股票因子暴露度 | `factorExposure_YYYYMMDD.csv` |
| 因子收益率 | 因子日收益率 | `factorReturn_YYYYMMDD.csv` |
| 因子股票池 | 有效股票列表 | `factorStockPool_YYYYMMDD.csv` |
| 因子协方差 | 因子协方差矩阵 | `factorCov_YYYYMMDD.csv` |
| 特异性风险 | 股票特异性风险 | `factorSpecificRisk_YYYYMMDD.csv` |
| 指数暴露度 | 7大指数因子暴露 | `{index}IndexExposure_YYYYMMDD.csv` |

**支持的指数**: 上证50、沪深300、中证500、中证1000、中证2000、中证A500、国证2000

---

## 数据源配置

支持 JY (聚源) 和 Wind 两个数据源，通过优先级配置自动切换：

**配置文件位置**：`config/legacy/data_source_priority_config.xlsx`

或使用新的YAML配置：`config/app_config.yaml`

```yaml
data_source_priority:
  factor:
    - source_name: "jy"
      rank: 1
    - source_name: "wind"
      rank: 2
```

---

## 环境要求

- **Python**: 3.8+
- **依赖包**: pandas, numpy, scipy, pymysql, pyyaml, openpyxl, xlrd
- **外部模块**: `global_tools` (通过环境变量 `GLOBAL_TOOLSFUNC_new` 指定)

---

## 配置文件

### 数据库配置 (需要从模板创建)

| 模板文件 | 目标文件 | 说明 |
|----------|----------|------|
| `config/database.yaml.example` | `config/database.yaml` | 数据库连接配置 |
| `config/tables/dataUpdate_sql.yaml.example` | `config/tables/dataUpdate_sql.yaml.local` | 数据表结构定义 |

**`database.yaml` 配置示例:**
```yaml
database:
  host: "your-database-host"
  port: 3306
  user: "your-username"
  password: "your-password"
  database: "your-database-name"
```

### 其他配置文件

| 文件 | 位置 | 说明 |
|------|------|------|
| 主配置 | `config/app_config.yaml` | 路径、数据源、时间、因子等配置 |
| 路径配置 | `config/legacy/data_update_path_config.xlsx` | 数据输入输出路径（旧格式） |
| 数据源优先级 | `config/legacy/data_source_priority_config.xlsx` | JY/Wind 优先级（旧格式） |
| 时间配置 | `config/legacy/time_tools_config.xlsx` | 更新时间策略（旧格式） |

**注意**：legacy目录下的Excel配置文件保留用于向后兼容，推荐使用 `config/app_config.yaml`。

---

## 数据库表 (可选)

如果启用 SQL 写入，需要创建以下表：

- FactorExposrue
- FactorReturn
- FactorPool
- FactorCov
- FactorSpecificrisk
- FactorIndexExposure
- Indexygfactorexposure

建表语句: `config_project/MySQL数据库表结构.md`

---

## 测试验证

```bash
# 运行单元测试
pytest tests/ -v -m unit

# 运行集成测试
pytest tests/ -v -m integration

# 运行全部测试
pytest tests/ -v

# 生成测试数据 + 端到端测试
python scripts/generate_test_data.py
python scripts/run_test.py
```

---

## 工作流程

```
日常更新流程:
┌─────────────────────────────────────────────────────────┐
│ 1. 计算日期 → 回滚3个工作日 (因子) / 10个工作日 (时序) │
│ 2. 读取数据源优先级配置                                 │
│ 3. 按优先级尝试获取 JY/Wind 数据                        │
│ 4. 处理数据 (清洗、计算指数暴露度等)                    │
│ 5. 输出 CSV 文件                                        │
│ 6. (可选) 写入 MySQL 数据库                             │
│ 7. 记录日志                                             │
└─────────────────────────────────────────────────────────┘
```

---

## 常见问题

**Q: 环境变量未设置**
```
EnvironmentError: 环境变量 GLOBAL_TOOLSFUNC_new 未设置
```
→ 设置 `GLOBAL_TOOLSFUNC_new` 指向 `global_tools` 模块路径

**Q: 数据缺失警告**
```
WARNING: factor_data在20250120数据存在缺失
```
→ 检查数据源目录下是否有对应日期的 `.mat` 文件

**Q: 数据库连接失败**
→ 检查 `config/database.yaml` 配置，或设置 `is_sql=False` 跳过数据库写入

---

## 文档

- [部署指南](docs/部署指南.md) - 完整部署步骤
- [数据需求清单](docs/数据需求清单.md) - 输入数据格式说明
- [配置说明](docs/配置说明.md) - 数据库和路径配置详解

---

## 版本

- v1.0 - 从 Data_update 项目独立部署
