# MySQL 数据库表结构说明

## 数据库配置

数据库名称：`factor_data`（可自定义）

## 表结构

### 1. FactorExposrue - 因子暴露度表

存储每日股票的因子暴露度数据。

```sql
CREATE TABLE IF NOT EXISTS FactorExposrue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    valuation_date DATE NOT NULL COMMENT '估值日期',
    code VARCHAR(20) NOT NULL COMMENT '股票代码',
    -- Barra风险因子（具体因子根据实际使用的因子模型而定）
    Size DOUBLE COMMENT '市值因子',
    Beta DOUBLE COMMENT '贝塔因子',
    Momentum DOUBLE COMMENT '动量因子',
    ResidualVolatility DOUBLE COMMENT '残差波动率因子',
    NonLinearSize DOUBLE COMMENT '非线性市值因子',
    Liquidity DOUBLE COMMENT '流动性因子',
    BooktoPrice DOUBLE COMMENT '账面市值比因子',
    EarningsYield DOUBLE COMMENT '盈利收益率因子',
    Growth DOUBLE COMMENT '成长因子',
    Leverage DOUBLE COMMENT '杠杆因子',
    -- 行业因子（根据实际行业分类添加）
    -- 示例：
    -- Industry_Bank DOUBLE COMMENT '银行业',
    -- Industry_RealEstate DOUBLE COMMENT '房地产业',
    -- ... 其他行业
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_date (valuation_date),
    INDEX idx_code (code),
    INDEX idx_date_code (valuation_date, code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子暴露度表';
```

### 2. FactorReturn - 因子收益率表

存储每日因子的收益率。

```sql
CREATE TABLE IF NOT EXISTS FactorReturn (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    valuation_date DATE NOT NULL COMMENT '估值日期',
    Size DOUBLE COMMENT '市值因子收益率',
    Beta DOUBLE COMMENT '贝塔因子收益率',
    Momentum DOUBLE COMMENT '动量因子收益率',
    ResidualVolatility DOUBLE COMMENT '残差波动率因子收益率',
    NonLinearSize DOUBLE COMMENT '非线性市值因子收益率',
    Liquidity DOUBLE COMMENT '流动性因子收益率',
    BooktoPrice DOUBLE COMMENT '账面市值比因子收益率',
    EarningsYield DOUBLE COMMENT '盈利收益率因子收益率',
    Growth DOUBLE COMMENT '成长因子收益率',
    Leverage DOUBLE COMMENT '杠杆因子收益率',
    -- 行业因子收益率
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE INDEX idx_date (valuation_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子收益率表';
```

### 3. FactorPool - 因子股票池表

存储每日有效的股票池。

```sql
CREATE TABLE IF NOT EXISTS FactorPool (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    valuation_date DATE NOT NULL COMMENT '估值日期',
    code VARCHAR(20) NOT NULL COMMENT '股票代码',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_date (valuation_date),
    INDEX idx_code (code),
    UNIQUE INDEX idx_date_code (valuation_date, code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子股票池表';
```

### 4. FactorCov - 因子协方差矩阵表

存储因子间的协方差矩阵。

```sql
CREATE TABLE IF NOT EXISTS FactorCov (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    valuation_date DATE NOT NULL COMMENT '估值日期',
    factor_name VARCHAR(50) NOT NULL COMMENT '因子名称（行因子）',
    -- 列因子的协方差值（字段名与因子名对应）
    Size DOUBLE COMMENT '与Size因子的协方差',
    Beta DOUBLE COMMENT '与Beta因子的协方差',
    Momentum DOUBLE COMMENT '与Momentum因子的协方差',
    ResidualVolatility DOUBLE COMMENT '与ResidualVolatility因子的协方差',
    NonLinearSize DOUBLE COMMENT '与NonLinearSize因子的协方差',
    Liquidity DOUBLE COMMENT '与Liquidity因子的协方差',
    BooktoPrice DOUBLE COMMENT '与BooktoPrice因子的协方差',
    EarningsYield DOUBLE COMMENT '与EarningsYield因子的协方差',
    Growth DOUBLE COMMENT '与Growth因子的协方差',
    Leverage DOUBLE COMMENT '与Leverage因子的协方差',
    -- 行业因子协方差
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_date (valuation_date),
    INDEX idx_factor (factor_name),
    UNIQUE INDEX idx_date_factor (valuation_date, factor_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子协方差矩阵表';
```

### 5. FactorSpecificrisk - 因子特异性风险表

存储股票的特异性风险。

```sql
CREATE TABLE IF NOT EXISTS FactorSpecificrisk (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    valuation_date DATE NOT NULL COMMENT '估值日期',
    code VARCHAR(20) NOT NULL COMMENT '股票代码',
    specificrisk DOUBLE NOT NULL COMMENT '特异性风险',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_date (valuation_date),
    INDEX idx_code (code),
    UNIQUE INDEX idx_date_code (valuation_date, code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子特异性风险表';
```

### 6. FactorIndexExposure - 指数因子暴露度表

存储指数的因子暴露度。

```sql
CREATE TABLE IF NOT EXISTS FactorIndexExposure (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    valuation_date DATE NOT NULL COMMENT '估值日期',
    organization VARCHAR(20) NOT NULL COMMENT '指数简称（如sz50, hs300, zz500等）',
    -- Barra风险因子暴露度
    Size DOUBLE COMMENT '市值因子',
    Beta DOUBLE COMMENT '贝塔因子',
    Momentum DOUBLE COMMENT '动量因子',
    ResidualVolatility DOUBLE COMMENT '残差波动率因子',
    NonLinearSize DOUBLE COMMENT '非线性市值因子',
    Liquidity DOUBLE COMMENT '流动性因子',
    BooktoPrice DOUBLE COMMENT '账面市值比因子',
    EarningsYield DOUBLE COMMENT '盈利收益率因子',
    Growth DOUBLE COMMENT '成长因子',
    Leverage DOUBLE COMMENT '杠杆因子',
    -- 行业因子暴露度
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_date (valuation_date),
    INDEX idx_org (organization),
    UNIQUE INDEX idx_date_org (valuation_date, organization)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指数因子暴露度表';
```

### 7. Indexygfactorexposure - 指数YG因子暴露度表

存储指数的YG（收益增长）因子暴露度。

```sql
CREATE TABLE IF NOT EXISTS Indexygfactorexposure (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    valuation_date DATE NOT NULL COMMENT '估值日期',
    type VARCHAR(50) NOT NULL COMMENT '因子类型',
    value DOUBLE COMMENT '因子值',
    organization VARCHAR(20) NOT NULL COMMENT '指数简称',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_date (valuation_date),
    INDEX idx_org (organization),
    INDEX idx_date_org_type (valuation_date, organization, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指数YG因子暴露度表';
```

## 注意事项

1. **因子字段**：上述建表语句中的因子字段（如Size、Beta等）是示例，实际使用的因子应根据你的因子模型确定。可能需要添加或删除某些字段。

2. **行业因子**：行业分类因子的字段需要根据实际使用的行业分类标准（如申万行业、中信行业等）来添加。每个行业一个字段。

3. **索引优化**：根据实际查询需求，可能需要调整索引设置。

4. **字符集**：使用utf8mb4字符集以支持中文和特殊字符。

5. **数据类型**：因子值使用DOUBLE类型存储浮点数，如需更高精度可改用DECIMAL。

6. **主键设置**：使用自增ID作为主键，同时为业务字段（日期+代码）创建唯一索引。

## 初始化脚本

可以将上述所有CREATE TABLE语句保存为一个SQL文件（如`init_tables.sql`），然后在MySQL中执行：

```bash
mysql -u your_username -p factor_data < init_tables.sql
```

或者在MySQL命令行中：

```sql
USE factor_data;
SOURCE /path/to/init_tables.sql;
```
