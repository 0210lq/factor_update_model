# 因子数据更新模块

自动化更新因子暴露度、收益率、协方差等数据，支持 JY/Wind 多数据源切换。

---

## 1. 快速开始

### 环境要求

| 项目 | 要求 |
|------|------|
| Python | 3.8+ (推荐 3.11) |
| 操作系统 | Windows / Linux |
| 外部依赖 | `global_tools` 模块 |

### 安装步骤

```bash
# 1. 克隆项目
git clone <repo-url>
cd factor_update_model

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
# Windows
set GLOBAL_TOOLSFUNC_new=D:\path\to\global_tools
# Linux/Mac
export GLOBAL_TOOLSFUNC_new=/path/to/global_tools

# 4. 配置数据库（可选）
copy config\database.yaml.example config\database.yaml
# 编辑 database.yaml 填入实际连接信息

# 5. 运行
python factor_update_main.py
```

### 最小运行示例

```python
from factor_update_main import FactorData_update_main

# 日常更新（自动计算日期）
FactorData_update_main(is_sql=False)  # 不写入数据库
```

---

## 2. 文档索引

| 文档 | 说明 | 推荐阅读 |
|------|------|----------|
| [部署指南](docs/部署指南.md) | 完整部署步骤 | 首次部署 |
| [完整部署手册](docs/完整部署手册.md) | 详细部署文档 | 生产环境 |
| [配置说明](docs/配置说明.md) | 配置文件详解 | 配置修改 |
| [数据需求清单](docs/数据需求清单.md) | 输入数据格式 | 数据准备 |
| [MySQL数据库表结构](docs/MySQL数据库表结构.md) | 建表语句 | 数据库初始化 |
| [data_flow_documentation](docs/data_flow_documentation.md) | 数据流文档 | 理解架构 |

---

## 3. 项目结构

```
factor_update_model/
├── factor_update_main.py       # 主入口（命令行 + API）
├── requirements.txt            # 依赖清单
├── pytest.ini                  # 测试配置
│
├── src/                        # 源代码
│   ├── factor_update/          # 因子更新核心
│   │   ├── factor_update.py    # FactorData_update 主类
│   │   └── factor_preparing.py # FactorData_prepare 数据准备
│   ├── timeseries_update/      # 时间序列更新
│   │   └── time_series_data_update.py
│   ├── time_tools/             # 时间工具
│   │   └── time_tools.py       # 交易日计算
│   ├── global_setting/         # 全局路径配置
│   │   └── global_dic.py       # 路径字典（读取 Excel）
│   ├── setup_logger/           # 日志模块
│   │   └── logger_setup.py
│   └── config/                 # 配置管理
│       └── unified_config.py   # 统一配置加载器
│
├── config/                     # 配置文件
│   ├── app_config.yaml         # 主配置（日期、指数映射、因子）
│   ├── database.yaml           # 数据库连接（需本地创建）
│   ├── database.yaml.example   # 数据库配置模板
│   ├── tables/                 # 表结构定义
│   └── legacy/                 # 旧格式配置（Excel）
│       └── data_update_path_config.xlsx  # 路径配置
│
├── tests/                      # 测试
│   ├── test_unified_config.py  # 配置测试
│   ├── test_config_loader.py   # 加载器测试
│   └── ...
│
├── docs/                       # 文档
├── scripts/                    # 工具脚本
└── logs/                       # 日志输出
```

---

## 4. 架构设计

### 核心模块

```
┌─────────────────────────────────────────────────────────────┐
│                    factor_update_main.py                     │
│                        (主入口)                              │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ FactorData_     │  │ timeSeries_     │  │ time_tools      │
│ update          │  │ data_update     │  │                 │
│ (因子更新)      │  │ (时间序列)      │  │ (日期计算)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│ FactorData_     │
│ prepare         │
│ (数据准备)      │
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      global_tools (外部)                     │
│  - 交易日历  - 文件读写  - 数据库操作  - MAT文件解析        │
└─────────────────────────────────────────────────────────────┘
```

### 核心类与接口

| 类 | 文件 | 职责 |
|-----|------|------|
| `FactorData_update` | `src/factor_update/factor_update.py` | 因子更新主控制器 |
| `FactorData_prepare` | `src/factor_update/factor_preparing.py` | 数据读取与预处理 |
| `timeSeries_data_update` | `src/timeseries_update/time_series_data_update.py` | 时间序列聚合 |
| `time_tools` | `src/time_tools/time_tools.py` | 交易日期计算 |
| `UnifiedConfig` | `src/config/unified_config.py` | 配置统一访问 |
| `ConfigLoader` | `src/config_loader.py` | YAML 配置加载 |

### 模块依赖关系

```
factor_update_main
    ├── FactorData_update
    │       └── FactorData_prepare
    │               └── global_dic (路径)
    │               └── global_tools (外部)
    ├── timeSeries_data_update
    ├── time_tools
    └── ConfigLoader / UnifiedConfig
```

---

## 5. 核心逻辑与数据流

### 典型请求链路

```
用户调用 FactorData_update_main(is_sql=True)
    │
    ▼
[1] time_tools.target_date_decision_factor()
    └── 计算目标日期，回滚 N 个工作日
    │
    ▼
[2] FactorData_update(start_date, end_date, is_sql)
    └── 初始化更新器
    │
    ▼
[3] fu.factor_update_main()
    ├── 读取数据源优先级配置 (Excel)
    ├── 遍历工作日列表
    │   └── for date in working_days_list:
    │
    ▼
[4] FactorData_prepare(date)
    ├── jy_factor_exposure_update()   # 读取 JY 的 .mat 文件
    ├── jy_factor_return_update()
    ├── factor_jy_covariance_update()
    └── factor_jy_SpecificRisk_update()
    │
    ▼
[5] 输出
    ├── CSV 文件: factorExposure_YYYYMMDD.csv
    └── SQL 写入: gt.sqlSaving_main().df_to_sql()
```

### 数据流向

```
输入数据 (.mat 文件)                    输出数据
─────────────────────                   ─────────────────────
D:/Data_Original/                       D:/Data_prepared_new/
├── data_jy/                            ├── data_factor/
│   ├── output_new/FactorRet/           │   ├── exposure/
│   │   └── LNMODELACTIVE-YYYYMMDD.mat  │   │   └── factorExposure_*.csv
│   ├── covariance/                     │   ├── return/
│   └── specificrisk/                   │   ├── stockpool/
└── data_windDB/                        │   ├── covariance/
    └── (同结构，备用数据源)             │   └── specificrisk/
                                        └── data_index/
                                            └── index_exposure/
```

---

## 6. 生态与生命力

### 依赖分析

| 依赖包 | 版本要求 | 用途 | 风险评估 |
|--------|---------|------|----------|
| pandas | >=2.0.0 | 数据处理 | 低风险，活跃维护 |
| numpy | >=1.20.0 | 数值计算 | 低风险 |
| scipy | >=1.10.0 | MAT文件读取 | 低风险 |
| PyMySQL | >=1.0.0 | MySQL连接 | 低风险 |
| SQLAlchemy | >=1.4.0 | ORM | 注意 2.0 API 变更 |
| PyYAML | >=6.0 | YAML解析 | 低风险 |
| openpyxl | >=3.0.0 | Excel读取 | 低风险 |

**外部强依赖**: `global_tools` 模块（内部工具库，需通过环境变量指定）

### 维护状态

| 指标 | 数值 |
|------|------|
| 最近6个月提交数 | ~19 次 |
| 主要贡献者 | 个人项目 |
| Python版本 | 3.8+ (宽松) |
| 测试覆盖 | 38 个单元测试 |

### 版本兼容性

- **Python**: 3.8 - 3.12 均可运行
- **Breaking Changes**: 配置从 Excel 迁移到 YAML（保留向后兼容）
- **数据库**: MySQL 5.7+ / 8.0+

---

## 7. 使用指南

### 命令行

```bash
# 日常更新
python factor_update_main.py

# 不写入数据库
python factor_update_main.py --no-sql

# 指定日期
python factor_update_main.py --date 2025-01-20

# 历史更新
python factor_update_main.py --history --start-date 2024-01-01 --end-date 2024-12-31

# 详细输出
python factor_update_main.py -v
```

### 作为模块调用

```python
from factor_update_main import FactorData_update_main, FactorData_history_update

# 日常更新
FactorData_update_main(is_sql=True)

# 历史更新
FactorData_history_update('2024-01-01', '2024-12-31', is_sql=True)
```

### 集成到调度系统

```python
# Airflow DAG 示例
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG('factor_update', schedule_interval='30 18 * * 1-5')

task = PythonOperator(
    task_id='update_factors',
    python_callable=lambda: __import__('factor_update_main').FactorData_update_main(is_sql=True),
    dag=dag
)
```

---

## 8. 功能输出

| 模块 | 输出文件 | 说明 |
|------|----------|------|
| 因子暴露度 | `factorExposure_YYYYMMDD.csv` | 股票因子暴露度 |
| 因子收益率 | `factorReturn_YYYYMMDD.csv` | 因子日收益率 |
| 因子股票池 | `factorStockPool_YYYYMMDD.csv` | 有效股票列表 |
| 因子协方差 | `factorCov_YYYYMMDD.csv` | 因子协方差矩阵 |
| 特异性风险 | `factorSpecificRisk_YYYYMMDD.csv` | 股票特异性风险 |
| 指数暴露度 | `{index}IndexExposure_YYYYMMDD.csv` | 7大指数因子暴露 |

**支持的指数**: 上证50、沪深300、中证500、中证1000、中证2000、中证A500、国证2000

---

## 9. 测试

```bash
# 运行全部测试
pytest tests/ -v

# 单元测试
pytest tests/ -v -m unit

# 查看覆盖率
pytest tests/ --cov=src --cov-report=html
```

---

## 10. 常见问题

**Q: 环境变量未设置**
```
EnvironmentError: 环境变量 GLOBAL_TOOLSFUNC_new 未设置
```
→ 设置环境变量指向 `global_tools` 模块路径

**Q: 数据缺失警告**
```
WARNING: factor_data在20250120数据存在缺失
```
→ 检查 `D:/Data_Original/data_jy/output_new/FactorRet/` 是否有对应 `.mat` 文件

**Q: 数据库连接失败**
→ 检查 `config/database.yaml` 或设置 `is_sql=False`

---

## 版本历史

| 版本 | 说明 |
|------|------|
| v1.2 | 配置清理：删除未使用的 paths/logging/database_batch 配置 |
| v1.1 | 项目结构整理：统一到 src/config/docs/ |
| v1.0 | 从 Data_update 项目独立部署 |
