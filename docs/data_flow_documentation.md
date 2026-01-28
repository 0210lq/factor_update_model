# Factor Update Model 数据流文档

## 概述

本文档记录了 `factor_update_model` 项目的数据输入来源、数据库读取和数据库输出情况。

---

## 一、本地文件读取（输入）

### 1.1 因子数据文件（.mat 格式）

#### JY数据源
| 数据类型 | 本地路径 |
|---------|---------|
| JY因子数据(新) | `D:\Data_Original\data_jy\output_new\FactorRet\LNMODELACTIVE-{YYYYMMDD}.mat` |
| JY因子数据(旧) | `D:\Data_Original\data_jy\output_old\FactorRet\LNMODELACTIVE-{YYYYMMDD}.mat` |
| JY协方差矩阵(新) | `D:\Data_Original\data_jy\output_new\CovarianceMatrix\*.csv` |
| JY协方差矩阵(旧) | `D:\Data_Original\data_jy\output_old\CovarianceMatrix\*.csv` |
| JY特异风险(新) | `D:\Data_Original\data_jy\output_new\SpecificRisk\*.csv` |
| JY特异风险(旧) | `D:\Data_Original\data_jy\output_old\SpecificRisk\*.csv` |

#### Wind数据源
| 数据类型 | 本地路径 |
|---------|---------|
| Wind因子数据 | `D:\Data_Original\data_windDB\output_new\FactorRet\LNMODELACTIVE-{YYYYMMDD}.mat` |
| Wind协方差矩阵 | `D:\Data_Original\data_windDB\output_new\CovarianceMatrix\*.csv` |
| Wind特异风险 | `D:\Data_Original\data_windDB\output_new\SpecificRisk\*.csv` |

### 1.2 股票池文件

| 数据类型 | 本地路径 |
|---------|---------|
| 股票池(新) | `D:\Data_Original\data_other\StockUniverse_new.csv` |
| 股票池(旧) | `D:\Data_Original\data_other\StockUniverse.csv` |

### 1.3 配置文件

| 配置类型 | 本地路径 |
|---------|---------|
| 路径配置 | `config\legacy\data_update_path_config.xlsx` |
| 数据源优先级 | `config\legacy\data_source_priority_config.xlsx` |
| 时间工具配置 | `config\legacy\time_tools_config.xlsx` |
| SQL表配置 | `config\tables\dataUpdate_sql.yaml` |
| 数据库连接配置 | `config\database.yaml` |
| 应用配置 | `config\app_config.yaml` |

---

## 二、数据库读取（输入）

### 2.1 时间序列数据更新模块读取的数据库表

**数据库**: `data_prepared_new` (生产) / `data_prepared_jzq` (测试)

| 数据库表 | 读取字段 | 用途 |
|---------|---------|------|
| `data_index` | valuation_date, code, open/high/low/close/pct_chg/volume/amt/turn_over | 指数行情数据 |
| `data_stock` | valuation_date, code, close/pct_chg | 股票行情数据 |
| `data_indexother` | valuation_date, organization, type, value | 指数其他数据(期货基差/评分差异/大单流入/杠杆买入等) |
| `data_factorindexexposure` | valuation_date, organization, 因子暴露字段 | 指数因子暴露数据 |
| `data_macro` | valuation_date, type, name, value, organization | 宏观数据(M1M2/Shibor/CPI/PPI/PMI/国债/社融等) |
| `data_lhb` | valuation_date, LHBProportion | 龙虎榜数据 |
| `data_us` | valuation_date, type, name, value, organization | 美元数据 |
| `data_internationalindex` | valuation_date, code, pct_chg | 国际指数数据 |
| `data_vix` | valuation_date, organization, vix_type, ch_vix | VIX数据 |
| `data_factorreturn` | valuation_date, 因子收益字段 | 因子收益数据 |

### 2.2 因子数据模块读取的数据库

**通过 `global_tools.index_weight_withdraw()` 函数读取**:
- 指数成分权重数据

---

## 三、数据库写入（输出）

### 3.1 因子数据输出

**目标数据库**: `data_prepared_jzq` (测试)

| 数据库表 | 主键 | 写入字段 | 数据来源 |
|---------|------|---------|---------|
| `data_factorexposure` | valuation_date, code | 因子暴露(size/beta/momentum等 + 行业因子) | JY/Wind因子文件 |
| `data_factorreturn` | valuation_date | 因子收益率 | JY/Wind因子文件 |
| `data_factorpool` | valuation_date, code | 因子有效股票池 | JY/Wind因子文件 |
| `data_factorcov` | valuation_date, factor_name | 因子协方差矩阵 | JY/Wind协方差CSV |
| `data_factorspecificrisk` | valuation_date, code | 特异风险 | JY/Wind特异风险CSV |
| `data_factorindexexposure` | valuation_date, organization | 指数因子暴露 | 计算得出 |
| `data_indexother` | valuation_date, type, organization | 指数YG因子暴露 | 计算得出 |

### 3.2 数据库连接信息

#### 测试数据库（读写）
```
Host: rm-cn-fhh4gzo9900083vo.rwlb.rds.aliyuncs.com
Port: 3306
User: jzq
Database: data_prepared_jzq
```

#### 生产数据库（只读）
```
Host: rm-bp1o6we7s3o1h76x1to.mysql.rds.aliyuncs.com
Port: 3306
User: none
Database: data_prepared_new
```

---

## 四、数据处理流程

### 4.1 因子数据更新流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                     因子数据更新流程                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐     ┌──────────────────┐                      │
│  │ JY因子MAT文件    │     │ Wind因子MAT文件   │                      │
│  │ (优先级: 1)      │     │ (优先级: 2)       │                      │
│  └────────┬─────────┘     └────────┬─────────┘                      │
│           │                        │                                 │
│           └──────────┬─────────────┘                                 │
│                      ▼                                               │
│           ┌──────────────────────┐                                   │
│           │ FactorData_prepare   │                                   │
│           │ - 因子暴露提取        │                                   │
│           │ - 因子收益提取        │                                   │
│           │ - 股票池匹配          │                                   │
│           └──────────┬───────────┘                                   │
│                      │                                               │
│           ┌──────────┴───────────┐                                   │
│           ▼                      ▼                                   │
│  ┌─────────────────┐    ┌─────────────────────┐                     │
│  │ 数据库写入       │    │ 本地CSV输出(可选)   │                     │
│  │ data_prepared_jzq│    │ Data_prepared_new   │                     │
│  └─────────────────┘    └─────────────────────┘                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 时间序列数据更新流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                   时间序列数据更新流程                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────┐                           │
│  │          data_prepared_new           │                           │
│  │        (生产数据库 - 只读)            │                           │
│  │  ┌───────────┬───────────┬─────────┐ │                           │
│  │  │data_index │data_stock │data_vix │ │                           │
│  │  │data_macro │data_lhb   │data_us  │ │                           │
│  │  │data_indexother        │         │ │                           │
│  │  │data_factorindexexposure         │ │                           │
│  │  │data_internationalindex          │ │                           │
│  │  └───────────┴───────────┴─────────┘ │                           │
│  └──────────────────┬───────────────────┘                           │
│                     │                                                │
│                     ▼                                                │
│           ┌─────────────────────┐                                    │
│           │ timeSeries_data_update │                                 │
│           │ - 数据查询             │                                 │
│           │ - 数据透视转换         │                                 │
│           │ - 增量更新             │                                 │
│           └──────────┬──────────┘                                    │
│                      │                                               │
│                      ▼                                               │
│           ┌─────────────────────┐                                    │
│           │  本地CSV时间序列文件  │                                    │
│           │  Data_prepared_new/   │                                   │
│           │  data_timeSeries/     │                                   │
│           └─────────────────────┘                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 五、输出表结构详情

### 5.1 data_factorexposure（因子暴露）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| valuation_date | String(50) | 估值日期 |
| code | String(50) | 股票代码 |
| size | Float | 市值因子 |
| beta | Float | Beta因子 |
| momentum | Float | 动量因子 |
| resvola | Float | 残差波动率因子 |
| nlsize | Float | 非线性市值因子 |
| btop | Float | 账面市值比因子 |
| liquidity | Float | 流动性因子 |
| earningsyield | Float | 盈利因子 |
| growth | Float | 成长因子 |
| 石油石化...综合 | Float | 30个行业因子 |
| update_time | DateTime | 更新时间 |

### 5.2 data_factorreturn（因子收益）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| valuation_date | String(50) | 估值日期 |
| size...综合 | Float | 各因子收益率 |
| update_time | DateTime | 更新时间 |

### 5.3 data_factorcov（因子协方差）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| valuation_date | String(50) | 估值日期 |
| factor_name | String(50) | 因子名称 |
| country...综合 | Float | 协方差矩阵值 |
| update_time | DateTime | 更新时间 |

### 5.4 data_factorspecificrisk（特异风险）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| valuation_date | String(50) | 估值日期 |
| code | String(50) | 股票代码 |
| specificrisk | Float | 特异风险值 |
| update_time | DateTime | 更新时间 |

### 5.5 data_factorindexexposure（指数因子暴露）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| valuation_date | String(50) | 估值日期 |
| organization | String(50) | 指数简称(sz50/hs300/zz500等) |
| size...综合 | Float | 各因子暴露度 |
| update_time | DateTime | 更新时间 |

### 5.6 data_indexother（指数其他数据）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| valuation_date | String(50) | 估值日期 |
| type | String(50) | 数据类型(earningsyield/growth等) |
| organization | String(50) | 指数简称 |
| value | Float | 数值 |

---

## 六、数据源优先级

根据 `data_source_priority_config.xlsx` 配置：

| 数据类型 | 优先级1 | 优先级2 |
|---------|--------|--------|
| factor | JY | Wind |

当优先数据源数据缺失时，自动切换到次优先数据源。

---

## 七、指数列表

支持的指数类型：

| 指数全称 | 简称 | 月度名称 |
|---------|------|---------|
| 上证50 | sz50 | sz50Monthly |
| 沪深300 | hs300 | csi300Monthly |
| 中证500 | zz500 | zz500Monthly |
| 中证1000 | zz1000 | zz1000Monthly |
| 中证2000 | zz2000 | zz2000Monthly |
| 中证A500 | zzA500 | zzA500Monthly |
| 国证2000 | gz2000 | gz2000Monthly |

---

## 八、更新方式

### 8.1 命令行参数

```bash
# 日常更新（自动计算日期，保存到数据库）
python factor_update_main.py

# 日常更新，不保存到数据库
python factor_update_main.py --no-sql

# 指定日期更新
python factor_update_main.py --date 2025-01-20

# 历史数据更新
python factor_update_main.py --history --start-date 2024-01-01 --end-date 2024-12-31
```

---

*文档生成时间: 2026-01-28*
