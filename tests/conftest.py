"""
Pytest 配置和共享 fixtures

提供测试所需的模拟数据、路径配置和通用工具函数。
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from scipy.io import savemat
import tempfile
import shutil

# 添加项目路径
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

# 设置环境变量 (如果未设置则模拟)
if not os.getenv('GLOBAL_TOOLSFUNC_new'):
    os.environ['GLOBAL_TOOLSFUNC_new'] = PROJECT_DIR

# ============= 常量定义 =============

BARRA_FACTORS = ['country', 'size', 'beta', 'momentum', 'resvola',
                 'nlsize', 'btop', 'liquidity', 'earningsyield', 'growth']

INDUSTRY_FACTORS = ['石油石化', '煤炭', '有色金属', '电力及公用事业', '钢铁',
                    '基础化工', '建筑', '建材', '轻工制造', '机械',
                    '电力设备及新能源', '国防军工', '汽车', '商贸零售', '消费者服务',
                    '家电', '纺织服装', '医药', '食品饮料', '农林牧渔',
                    '银行', '非银行金融', '房地产', '综合金融', '交通运输',
                    '电子', '通信', '计算机', '传媒', '综合']

ALL_FACTORS = BARRA_FACTORS + INDUSTRY_FACTORS

TEST_STOCK_CODES = [f"{str(i).zfill(6)}.SZ" for i in range(1, 51)] + \
                   [f"{str(600000+i).zfill(6)}.SH" for i in range(50)]

TEST_DATE = '2025-01-20'
TEST_DATE_INT = '20250120'


# ============= Fixtures =============

@pytest.fixture(scope='session')
def project_dir():
    """项目根目录"""
    return PROJECT_DIR


@pytest.fixture(scope='session')
def test_data_dir(tmp_path_factory):
    """创建临时测试数据目录"""
    temp_dir = tmp_path_factory.mktemp('test_data')

    # 创建子目录结构
    dirs = [
        'input/jy/FactorRet',
        'input/wind/FactorRet',
        'input/cov_jy',
        'input/cov_wind',
        'input/specific_jy',
        'input/specific_wind',
        'other',
        'output/factor_exposure',
        'output/factor_return',
        'output/factor_stockpool',
        'indexcomponent/hs300',
        'indexcomponent/zz500',
    ]

    for d in dirs:
        (temp_dir / d).mkdir(parents=True, exist_ok=True)

    return temp_dir


@pytest.fixture
def sample_stock_codes():
    """示例股票代码列表"""
    return TEST_STOCK_CODES


@pytest.fixture
def sample_factor_names():
    """示例因子名称"""
    return {
        'barra': BARRA_FACTORS,
        'industry': INDUSTRY_FACTORS,
        'all': ALL_FACTORS
    }


@pytest.fixture
def sample_factor_exposure():
    """生成示例因子暴露度矩阵"""
    n_stocks = len(TEST_STOCK_CODES)
    n_factors = len(ALL_FACTORS)

    # Barra 因子: 正态分布
    barra_exposure = np.random.randn(n_stocks, len(BARRA_FACTORS))

    # 行业因子: 独热编码
    industry_exposure = np.zeros((n_stocks, len(INDUSTRY_FACTORS)))
    for i in range(n_stocks):
        industry_idx = i % len(INDUSTRY_FACTORS)
        industry_exposure[i, industry_idx] = 1.0

    return np.hstack([barra_exposure, industry_exposure])


@pytest.fixture
def sample_factor_return():
    """生成示例因子收益率"""
    n_factors = len(ALL_FACTORS)
    return np.random.randn(1, n_factors) * 0.01


@pytest.fixture
def sample_mat_data(sample_factor_exposure, sample_factor_return):
    """生成示例 .mat 文件数据结构"""
    return {
        'lnmodel_active_daily': {
            'factorexposure': sample_factor_exposure,
            'factorret': sample_factor_return
        }
    }


@pytest.fixture
def sample_covariance_matrix():
    """生成示例协方差矩阵"""
    n_factors = len(ALL_FACTORS)
    A = np.random.randn(n_factors, n_factors)
    cov_matrix = np.dot(A, A.T) / n_factors * 0.0001

    df = pd.DataFrame(cov_matrix, columns=ALL_FACTORS)
    df.insert(0, 'Observations', range(1, n_factors + 1))
    return df


@pytest.fixture
def sample_specific_risk():
    """生成示例特异性风险"""
    n_stocks = len(TEST_STOCK_CODES)
    return np.abs(np.random.randn(1, n_stocks)) * 0.02 + 0.01


@pytest.fixture
def sample_stock_universe():
    """生成示例股票池 DataFrame"""
    return pd.DataFrame({
        'S_INFO_WINDCODE': TEST_STOCK_CODES,
        'type': ['stockuni_new'] * len(TEST_STOCK_CODES),
        'S_INFO_LISTDATE': [19910101 + i * 100 for i in range(len(TEST_STOCK_CODES))],
        'S_INFO_DELISTDATE': [np.nan] * len(TEST_STOCK_CODES)
    })


@pytest.fixture
def sample_index_component():
    """生成示例指数成分股"""
    n_components = 30
    selected = np.random.choice(TEST_STOCK_CODES, n_components, replace=False)
    weights = np.random.rand(n_components)
    weights = weights / weights.sum()

    return pd.DataFrame({
        'code': selected,
        'weight': weights,
        'status': [1] * n_components
    })


@pytest.fixture
def mat_file(test_data_dir, sample_mat_data):
    """创建临时 .mat 文件"""
    mat_path = test_data_dir / 'input' / 'jy' / 'FactorRet' / f'LNMODELACTIVE-{TEST_DATE_INT}.mat'
    savemat(str(mat_path), sample_mat_data)
    return mat_path


@pytest.fixture
def stock_universe_file(test_data_dir, sample_stock_universe):
    """创建临时股票池文件"""
    csv_path = test_data_dir / 'other' / 'StockUniverse_new.csv'
    sample_stock_universe.to_csv(csv_path, index=False, encoding='gbk')
    return csv_path


@pytest.fixture
def covariance_file(test_data_dir, sample_covariance_matrix):
    """创建临时协方差文件"""
    csv_path = test_data_dir / 'input' / 'cov_jy' / f'CovarianceMatrix_{TEST_DATE_INT}.csv'
    sample_covariance_matrix.to_csv(csv_path, index=False, encoding='gbk')
    return csv_path


@pytest.fixture
def mock_global_tools():
    """模拟 global_tools 模块"""
    mock_gt = MagicMock()

    # 模拟常用函数
    mock_gt.intdate_transfer = lambda x: x.replace('-', '') if isinstance(x, str) and '-' in x else str(x)
    mock_gt.strdate_transfer = lambda x: f"{x[:4]}-{x[4:6]}-{x[6:8]}" if len(str(x)) == 8 else x
    mock_gt.is_workday_auto = lambda: True
    mock_gt.working_days_list = lambda start, end: [TEST_DATE]
    mock_gt.last_workday_calculate = lambda x: x
    mock_gt.next_workday_calculate = lambda x: x
    mock_gt.folder_creator2 = lambda x: os.makedirs(x, exist_ok=True)
    mock_gt.readcsv = lambda x: pd.read_csv(x, encoding='gbk')
    mock_gt.factor_name_new = lambda: (BARRA_FACTORS, INDUSTRY_FACTORS)
    mock_gt.factor_name = lambda x: (BARRA_FACTORS, INDUSTRY_FACTORS)
    mock_gt.factor_universe_withdraw = lambda: pd.DataFrame({
        'S_INFO_WINDCODE': TEST_STOCK_CODES
    })

    return mock_gt


@pytest.fixture
def mock_glv(test_data_dir):
    """模拟 global_dic 模块的 get 函数"""
    # 使用新的 config 目录结构
    config_project_dir = os.path.join(PROJECT_DIR, 'config', 'config_project')

    # 如果新目录不存在，使用旧目录
    if not os.path.exists(config_project_dir):
        config_project_dir = os.path.join(PROJECT_DIR, 'config_project')

    path_mapping = {
        'input_factor_jy': str(test_data_dir / 'input' / 'jy' / 'FactorRet'),
        'input_factor_jy_old': str(test_data_dir / 'input' / 'jy' / 'FactorRet'),
        'input_factor_wind': str(test_data_dir / 'input' / 'wind' / 'FactorRet'),
        'input_factor_cov_jy': str(test_data_dir / 'input' / 'cov_jy'),
        'input_factor_cov_wind': str(test_data_dir / 'input' / 'cov_wind'),
        'input_factor_specific_jy': str(test_data_dir / 'input' / 'specific_jy'),
        'input_factor_specific_wind': str(test_data_dir / 'input' / 'specific_wind'),
        'output_factor_exposure': str(test_data_dir / 'output' / 'factor_exposure'),
        'output_factor_return': str(test_data_dir / 'output' / 'factor_return'),
        'output_factor_stockpool': str(test_data_dir / 'output' / 'factor_stockpool'),
        'output_factor_cov': str(test_data_dir / 'output' / 'factor_cov'),
        'output_factor_specific_risk': str(test_data_dir / 'output' / 'factor_specific_risk'),
        'output_indexexposure': str(test_data_dir / 'output' / 'indexexposure'),
        'output_indexexposure_yg': str(test_data_dir / 'output' / 'indexexposure_yg'),
        'output_indexcomponent': str(test_data_dir / 'indexcomponent'),
        'data_other': str(test_data_dir / 'other'),
        'data_source_priority': os.path.join(config_project_dir, 'data_source_priority_config.xlsx'),
        'config_sql': os.path.join(config_project_dir, 'sql_connection.yaml'),
        'time_tools_config': os.path.join(config_project_dir, 'time_tools_config.xlsx'),
    }

    mock = MagicMock()
    mock.get = lambda key: path_mapping.get(key, '')
    return mock


# ============= 辅助函数 =============

def create_test_mat_file(path, n_stocks=100):
    """创建测试用 .mat 文件"""
    n_factors = len(ALL_FACTORS)

    barra = np.random.randn(n_stocks, len(BARRA_FACTORS))
    industry = np.zeros((n_stocks, len(INDUSTRY_FACTORS)))
    for i in range(n_stocks):
        industry[i, i % len(INDUSTRY_FACTORS)] = 1.0

    exposure = np.hstack([barra, industry])
    factor_ret = np.random.randn(1, n_factors) * 0.01

    mat_data = {
        'lnmodel_active_daily': {
            'factorexposure': exposure,
            'factorret': factor_ret
        }
    }

    savemat(str(path), mat_data)
    return mat_data
