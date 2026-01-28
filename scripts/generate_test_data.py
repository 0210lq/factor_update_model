"""
测试数据生成脚本

此脚本生成模拟的因子数据，用于测试 factor_update_model 项目的完整运行流程。
生成的数据为随机数据，仅用于验证代码逻辑，不具有实际业务意义。

使用方法:
    python scripts/generate_test_data.py

生成的数据包括:
    1. .mat 因子数据文件 (JY和Wind数据源)
    2. 协方差矩阵 CSV 文件
    3. 特异性风险 CSV 文件
    4. 股票池 CSV 文件
    5. 指数成分股 CSV 文件
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy.io import savemat
from datetime import datetime, timedelta

# 设置项目路径
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

# 设置环境变量 (如果未设置)
path = os.getenv('GLOBAL_TOOLSFUNC_new')
if path:
    sys.path.append(path)

# ============= 配置参数 =============

# 测试数据目录 (在项目内创建)
TEST_DATA_DIR = os.path.join(PROJECT_DIR, 'test_data')

# 因子名称
BARRA_FACTORS = ['country', 'size', 'beta', 'momentum', 'resvola',
                 'nlsize', 'btop', 'liquidity', 'earningsyield', 'growth']

INDUSTRY_FACTORS = ['石油石化', '煤炭', '有色金属', '电力及公用事业', '钢铁',
                    '基础化工', '建筑', '建材', '轻工制造', '机械',
                    '电力设备及新能源', '国防军工', '汽车', '商贸零售', '消费者服务',
                    '家电', '纺织服装', '医药', '食品饮料', '农林牧渔',
                    '银行', '非银行金融', '房地产', '综合金融', '交通运输',
                    '电子', '通信', '计算机', '传媒', '综合']

ALL_FACTORS = BARRA_FACTORS + INDUSTRY_FACTORS

# 指数列表
INDEX_LIST = ['sz50', 'hs300', 'zz500', 'zz1000', 'zz2000', 'zzA500', 'gz2000']

# 股票数量
N_STOCKS = 100  # 使用较少的股票数量进行测试

# 测试日期范围
TEST_START_DATE = '2025-01-20'
TEST_END_DATE = '2025-01-24'


def create_directories():
    """创建测试数据目录结构"""
    dirs = [
        os.path.join(TEST_DATA_DIR, 'input', 'jy', 'FactorRet'),
        os.path.join(TEST_DATA_DIR, 'input', 'jy_old', 'FactorRet'),
        os.path.join(TEST_DATA_DIR, 'input', 'wind', 'FactorRet'),
        os.path.join(TEST_DATA_DIR, 'input', 'cov_jy'),
        os.path.join(TEST_DATA_DIR, 'input', 'cov_wind'),
        os.path.join(TEST_DATA_DIR, 'input', 'specific_jy'),
        os.path.join(TEST_DATA_DIR, 'input', 'specific_wind'),
        os.path.join(TEST_DATA_DIR, 'other'),
        os.path.join(TEST_DATA_DIR, 'output', 'factor_exposure'),
        os.path.join(TEST_DATA_DIR, 'output', 'factor_return'),
        os.path.join(TEST_DATA_DIR, 'output', 'factor_stockpool'),
        os.path.join(TEST_DATA_DIR, 'output', 'factor_cov'),
        os.path.join(TEST_DATA_DIR, 'output', 'factor_specific_risk'),
        os.path.join(TEST_DATA_DIR, 'output', 'indexexposure'),
        os.path.join(TEST_DATA_DIR, 'output', 'indexexposure_yg'),
        os.path.join(TEST_DATA_DIR, 'output', 'timeseries'),
    ]

    # 为每个指数创建目录
    for idx in INDEX_LIST:
        dirs.append(os.path.join(TEST_DATA_DIR, 'indexcomponent', idx))
        dirs.append(os.path.join(TEST_DATA_DIR, 'output', 'indexexposure', idx))

    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  [OK] {d}")


def generate_stock_codes(n_stocks):
    """生成模拟股票代码"""
    codes = []
    for i in range(n_stocks):
        if i < n_stocks // 2:
            # 深圳股票
            code = f"{str(i+1).zfill(6)}.SZ"
        else:
            # 上海股票
            code = f"{str(600000 + i - n_stocks//2).zfill(6)}.SH"
        codes.append(code)
    return codes


def generate_stock_universe():
    """生成股票池数据"""
    stock_codes = generate_stock_codes(N_STOCKS)

    df = pd.DataFrame({
        'S_INFO_WINDCODE': stock_codes,
        'type': ['stockuni_new'] * N_STOCKS,
        'S_INFO_LISTDATE': [19910101 + i * 100 for i in range(N_STOCKS)],
        'S_INFO_DELISTDATE': [np.nan] * N_STOCKS
    })

    # 保存新版
    output_path = os.path.join(TEST_DATA_DIR, 'other', 'StockUniverse_new.csv')
    df.to_csv(output_path, index=False, encoding='gbk')
    print(f"  [OK] StockUniverse_new.csv ({N_STOCKS} stocks)")

    # 保存旧版 (相同内容)
    output_path = os.path.join(TEST_DATA_DIR, 'other', 'StockUniverse.csv')
    df.to_csv(output_path, index=False, encoding='gbk')
    print(f"  [OK] StockUniverse.csv ({N_STOCKS} stocks)")

    return stock_codes


def generate_mat_file(date_str, output_dir, stock_codes):
    """生成 .mat 格式的因子数据文件"""
    n_stocks = len(stock_codes)
    n_factors = len(ALL_FACTORS)

    # 生成因子暴露度矩阵 (股票 x 因子)
    # Barra因子: 正态分布
    barra_exposure = np.random.randn(n_stocks, len(BARRA_FACTORS))

    # 行业因子: 独热编码 (每只股票属于一个行业)
    industry_exposure = np.zeros((n_stocks, len(INDUSTRY_FACTORS)))
    for i in range(n_stocks):
        industry_idx = i % len(INDUSTRY_FACTORS)
        industry_exposure[i, industry_idx] = 1.0

    factor_exposure = np.hstack([barra_exposure, industry_exposure])

    # 生成因子收益率 (1 x 因子)
    factor_return = np.random.randn(1, n_factors) * 0.01  # 约1%的日收益率

    # 构建 MATLAB 结构
    lnmodel_data = {
        'factorexposure': factor_exposure,
        'factorret': factor_return
    }

    # 创建嵌套结构 (匹配原始数据格式)
    mat_data = {
        'lnmodel_active_daily': {
            'factorexposure': factor_exposure,
            'factorret': factor_return
        }
    }

    # 保存文件
    date_formatted = date_str.replace('-', '')
    filename = f'LNMODELACTIVE-{date_formatted}.mat'
    filepath = os.path.join(output_dir, filename)
    savemat(filepath, mat_data)

    return filepath


def generate_covariance_file(date_str, output_dir):
    """生成协方差矩阵 CSV 文件"""
    n_factors = len(ALL_FACTORS)

    # 生成正定协方差矩阵
    A = np.random.randn(n_factors, n_factors)
    cov_matrix = np.dot(A, A.T) / n_factors * 0.0001  # 缩小数值

    # 创建 DataFrame
    df = pd.DataFrame(cov_matrix, columns=ALL_FACTORS)
    df.insert(0, 'Observations', range(1, n_factors + 1))

    # 保存文件
    date_formatted = date_str.replace('-', '')
    filename = f'CovarianceMatrix_{date_formatted}.csv'
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, encoding='gbk')

    return filepath


def generate_specific_risk_file(date_str, output_dir, stock_codes):
    """生成特异性风险 CSV 文件"""
    n_stocks = len(stock_codes)

    # 生成特异性风险 (正值)
    specific_risk = np.abs(np.random.randn(1, n_stocks)) * 0.02 + 0.01

    # 创建 DataFrame (无列名)
    df = pd.DataFrame(specific_risk)

    # 保存文件 (文件名长度为31字符)
    date_formatted = date_str.replace('-', '')
    filename = f'SpecificRisk_{date_formatted}.csv'
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, header=False, encoding='gbk')

    return filepath


def generate_index_component(date_str, index_name, stock_codes):
    """生成指数成分股数据"""
    # 随机选择一部分股票作为成分股
    n_components = min(30, len(stock_codes))
    selected_stocks = np.random.choice(stock_codes, n_components, replace=False)

    # 生成权重 (归一化)
    weights = np.random.rand(n_components)
    weights = weights / weights.sum()

    df = pd.DataFrame({
        'code': selected_stocks,
        'weight': weights,
        'status': [1] * n_components
    })

    # 保存文件
    date_formatted = date_str.replace('-', '')
    output_dir = os.path.join(TEST_DATA_DIR, 'indexcomponent', index_name)
    filename = f'{index_name}Component_{date_formatted}.csv'
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, encoding='gbk')

    return filepath


def get_working_days(start_date, end_date):
    """获取日期范围内的工作日 (简化版，排除周末)"""
    dates = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    while current <= end:
        # 排除周末
        if current.weekday() < 5:
            dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)

    return dates


def generate_path_config():
    """生成测试用的路径配置文件"""
    # main_folder 配置
    main_folder_data = {
        'folder_type': ['factor', 'timeseries', 'other', 'config'],
        'path': [
            os.path.join(TEST_DATA_DIR, 'output'),
            os.path.join(TEST_DATA_DIR, 'output', 'timeseries'),
            TEST_DATA_DIR,
            os.path.join(PROJECT_DIR, 'config')
        ]
    }
    df_main = pd.DataFrame(main_folder_data)

    # sub_folder 配置
    sub_folder_data = []

    # 输出路径
    output_mappings = [
        ('output_factor_exposure', 'factor', 'factor_exposure'),
        ('output_factor_return', 'factor', 'factor_return'),
        ('output_factor_stockpool', 'factor', 'factor_stockpool'),
        ('output_factor_cov', 'factor', 'factor_cov'),
        ('output_factor_specific_risk', 'factor', 'factor_specific_risk'),
        ('output_indexexposure', 'factor', 'indexexposure'),
        ('output_indexexposure_yg', 'factor', 'indexexposure_yg'),
        ('output_timeseries', 'timeseries', ''),
    ]

    for data_type, folder_type, folder_name in output_mappings:
        sub_folder_data.append({
            'data_type': data_type,
            'folder_type': folder_type,
            'folder_name': folder_name,
            'MPON': 0,
            'RON': 1
        })

    # 输入路径 (使用测试数据目录)
    input_mappings = [
        ('input_factor_jy', os.path.join(TEST_DATA_DIR, 'input', 'jy', 'FactorRet')),
        ('input_factor_jy_old', os.path.join(TEST_DATA_DIR, 'input', 'jy_old', 'FactorRet')),
        ('input_factor_wind', os.path.join(TEST_DATA_DIR, 'input', 'wind', 'FactorRet')),
        ('input_factor_cov_jy', os.path.join(TEST_DATA_DIR, 'input', 'cov_jy')),
        ('input_factor_cov_wind', os.path.join(TEST_DATA_DIR, 'input', 'cov_wind')),
        ('input_factor_specific_jy', os.path.join(TEST_DATA_DIR, 'input', 'specific_jy')),
        ('input_factor_specific_wind', os.path.join(TEST_DATA_DIR, 'input', 'specific_wind')),
        ('data_other', os.path.join(TEST_DATA_DIR, 'other')),
        ('output_indexcomponent', os.path.join(TEST_DATA_DIR, 'indexcomponent')),
    ]

    for data_type, path in input_mappings:
        sub_folder_data.append({
            'data_type': data_type,
            'folder_type': 'direct',  # 直接使用绝对路径
            'folder_name': path,
            'MPON': 0,
            'RON': 0
        })

    # 配置文件路径
    config_mappings = [
        ('data_source_priority', os.path.join(PROJECT_DIR, 'config', 'legacy', 'data_source_priority_config.xlsx')),
        ('config_sql', os.path.join(PROJECT_DIR, 'config', 'database.yaml')),
        ('time_tools_config', os.path.join(PROJECT_DIR, 'config', 'legacy', 'time_tools_config.xlsx')),
    ]

    for data_type, path in config_mappings:
        sub_folder_data.append({
            'data_type': data_type,
            'folder_type': 'direct',
            'folder_name': path,
            'MPON': 0,
            'RON': 0
        })

    df_sub = pd.DataFrame(sub_folder_data)

    # 保存配置文件
    config_path = os.path.join(PROJECT_DIR, 'config', 'legacy', 'data_update_path_config_test.xlsx')
    with pd.ExcelWriter(config_path, engine='openpyxl') as writer:
        df_main.to_excel(writer, sheet_name='main_folder', index=False)
        df_sub.to_excel(writer, sheet_name='sub_folder', index=False)

    print(f"  [OK] 测试路径配置: {config_path}")
    return config_path


def main():
    """主函数"""
    print("=" * 60)
    print("测试数据生成脚本")
    print("=" * 60)

    # 1. 创建目录结构
    print("\n1. 创建目录结构...")
    create_directories()

    # 2. 生成股票池
    print("\n2. 生成股票池数据...")
    stock_codes = generate_stock_universe()

    # 3. 获取工作日列表
    print("\n3. 获取测试日期...")
    working_days = get_working_days(TEST_START_DATE, TEST_END_DATE)
    print(f"  测试日期: {working_days}")

    # 4. 为每个工作日生成数据
    print("\n4. 生成因子数据...")
    for date_str in working_days:
        print(f"\n  日期: {date_str}")

        # 生成 JY .mat 文件
        mat_path = generate_mat_file(
            date_str,
            os.path.join(TEST_DATA_DIR, 'input', 'jy', 'FactorRet'),
            stock_codes
        )
        print(f"    [OK] JY MAT: {os.path.basename(mat_path)}")

        # 生成 Wind .mat 文件 (相同结构)
        mat_path = generate_mat_file(
            date_str,
            os.path.join(TEST_DATA_DIR, 'input', 'wind', 'FactorRet'),
            stock_codes
        )
        print(f"    [OK] Wind MAT: {os.path.basename(mat_path)}")

        # 生成协方差文件
        cov_path = generate_covariance_file(
            date_str,
            os.path.join(TEST_DATA_DIR, 'input', 'cov_jy')
        )
        print(f"    [OK] JY Cov: {os.path.basename(cov_path)}")

        cov_path = generate_covariance_file(
            date_str,
            os.path.join(TEST_DATA_DIR, 'input', 'cov_wind')
        )
        print(f"    [OK] Wind Cov: {os.path.basename(cov_path)}")

        # 生成特异性风险文件
        risk_path = generate_specific_risk_file(
            date_str,
            os.path.join(TEST_DATA_DIR, 'input', 'specific_jy'),
            stock_codes
        )
        print(f"    [OK] JY Risk: {os.path.basename(risk_path)}")

        risk_path = generate_specific_risk_file(
            date_str,
            os.path.join(TEST_DATA_DIR, 'input', 'specific_wind'),
            stock_codes
        )
        print(f"    [OK] Wind Risk: {os.path.basename(risk_path)}")

        # 生成指数成分股数据
        for idx in INDEX_LIST:
            comp_path = generate_index_component(date_str, idx, stock_codes)
        print(f"    [OK] Index Components: {len(INDEX_LIST)} indices")

    # 5. 生成路径配置
    print("\n5. 生成测试路径配置...")
    generate_path_config()

    # 完成
    print("\n" + "=" * 60)
    print("测试数据生成完成!")
    print("=" * 60)
    print(f"\n数据目录: {TEST_DATA_DIR}")
    print(f"测试日期: {TEST_START_DATE} ~ {TEST_END_DATE}")
    print(f"股票数量: {N_STOCKS}")
    print(f"\n下一步: 运行测试脚本验证项目")
    print("  python scripts/run_test.py")


if __name__ == '__main__':
    main()
