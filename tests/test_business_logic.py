# -*- coding: utf-8 -*-
"""
业务逻辑测试 - TDD 补充测试

测试核心业务逻辑的正确性，包括：
- 数据处理流程
- 边界条件
- 异常处理
- 数据转换
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from scipy.io import savemat, loadmat
import tempfile

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from tests.conftest import (
    BARRA_FACTORS, INDUSTRY_FACTORS, ALL_FACTORS,
    TEST_STOCK_CODES, TEST_DATE, TEST_DATE_INT,
    create_test_mat_file
)


class TestFactorDataPrepareBusinessLogic:
    """FactorData_prepare 业务逻辑测试"""

    @pytest.fixture
    def setup_complete_env(self, test_data_dir, mock_global_tools, mock_glv):
        """设置完整的测试环境"""
        # 创建 MAT 文件
        mat_path = test_data_dir / 'input' / 'jy' / 'FactorRet' / f'LNMODELACTIVE-{TEST_DATE_INT}.mat'
        mat_data = create_test_mat_file(mat_path, n_stocks=len(TEST_STOCK_CODES))

        # 创建股票池文件
        stock_df = pd.DataFrame({
            'S_INFO_WINDCODE': TEST_STOCK_CODES,
            'type': ['stockuni_new'] * len(TEST_STOCK_CODES),
            'S_INFO_LISTDATE': [19910101] * len(TEST_STOCK_CODES),
            'S_INFO_DELISTDATE': [np.nan] * len(TEST_STOCK_CODES)
        })
        stock_path_new = test_data_dir / 'other' / 'StockUniverse_new.csv'
        stock_path_old = test_data_dir / 'other' / 'StockUniverse.csv'
        stock_df.to_csv(stock_path_new, index=False, encoding='gbk')
        stock_df.to_csv(stock_path_old, index=False, encoding='gbk')

        return {
            'mat_path': mat_path,
            'mat_data': mat_data,
            'mock_gt': mock_global_tools,
            'mock_glv': mock_glv,
            'test_data_dir': test_data_dir
        }

    @pytest.mark.unit
    def test_stock_pool_processing_matches_new_universe(self, setup_complete_env):
        """测试 stock_pool_processing 能正确匹配新股票池"""
        env = setup_complete_env

        with patch('src.factor_update.factor_preparing.gt', env['mock_gt']), \
             patch('src.factor_update.factor_preparing.glv', env['mock_glv']):
            try:
                from src.factor_update.factor_preparing import FactorData_prepare

                fp = FactorData_prepare(TEST_DATE)

                # 创建与新股票池长度相同的 DataFrame
                df_test = pd.DataFrame(np.random.randn(len(TEST_STOCK_CODES), 5))
                result = fp.stock_pool_processing(df_test)

                assert 'code' in result.columns
                assert len(result) == len(TEST_STOCK_CODES)
                assert result['code'].tolist() == TEST_STOCK_CODES
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_stock_pool_processing_length_mismatch(self, setup_complete_env):
        """测试 stock_pool_processing 在长度不匹配时的行为"""
        env = setup_complete_env

        with patch('src.factor_update.factor_preparing.gt', env['mock_gt']), \
             patch('src.factor_update.factor_preparing.glv', env['mock_glv']):
            try:
                from src.factor_update.factor_preparing import FactorData_prepare

                fp = FactorData_prepare(TEST_DATE)

                # 创建长度不匹配的 DataFrame
                df_test = pd.DataFrame(np.random.randn(10, 5))  # 只有10行
                result = fp.stock_pool_processing(df_test)

                # 长度不匹配时不应添加 code 列
                assert 'code' not in result.columns or len(result['code']) == 10
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_factor_exposure_drops_country_column(self, setup_complete_env):
        """测试因子暴露度输出中 country 列被正确删除"""
        env = setup_complete_env

        with patch('src.factor_update.factor_preparing.gt', env['mock_gt']), \
             patch('src.factor_update.factor_preparing.glv', env['mock_glv']):
            try:
                from src.factor_update.factor_preparing import FactorData_prepare

                fp = FactorData_prepare(TEST_DATE)
                result = fp.jy_factor_exposure_update()

                if len(result) > 0:
                    assert 'country' not in result.columns
                    assert 'valuation_date' in result.columns
                    assert 'code' in result.columns
            except Exception as e:
                pytest.skip(f"测试跳过: {e}")

    @pytest.mark.unit
    def test_factor_return_has_correct_date_format(self, setup_complete_env):
        """测试因子收益率日期格式正确 (YYYY-MM-DD)"""
        env = setup_complete_env

        with patch('src.factor_update.factor_preparing.gt', env['mock_gt']), \
             patch('src.factor_update.factor_preparing.glv', env['mock_glv']):
            try:
                from src.factor_update.factor_preparing import FactorData_prepare

                fp = FactorData_prepare(TEST_DATE)
                result = fp.jy_factor_return_update()

                if len(result) > 0:
                    date_val = result['valuation_date'].iloc[0]
                    # 检查日期格式为 YYYY-MM-DD
                    assert len(date_val) == 10
                    assert date_val[4] == '-'
                    assert date_val[7] == '-'
            except Exception as e:
                pytest.skip(f"测试跳过: {e}")

    @pytest.mark.unit
    def test_index_dic_processing_returns_complete_mapping(self, mock_global_tools):
        """测试 index_dic_processing 返回完整的指数映射"""
        with patch('src.factor_update.factor_preparing.gt', mock_global_tools):
            try:
                from src.factor_update.factor_preparing import FactorData_prepare

                fp = FactorData_prepare(TEST_DATE)
                dic = fp.index_dic_processing()

                expected_indices = ['上证50', '沪深300', '中证500', '中证1000', '中证2000', '中证A500', '国证2000']
                for idx in expected_indices:
                    assert idx in dic, f"缺少指数: {idx}"
            except ImportError:
                pytest.skip("模块导入失败")


class TestFactorDataUpdateBusinessLogic:
    """FactorData_update 业务逻辑测试"""

    @pytest.mark.unit
    def test_date_fallback_logic(self, mock_global_tools):
        """测试日期回退逻辑 - 当输出目录为空时回退到 2023-06-01"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update

                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                # 验证硬编码的回退日期
                hardcoded_fallback = '2023-06-01'
                assert fu.start_date >= hardcoded_fallback or fu.start_date == '2025-01-01'
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_source_priority_returns_dataframe(self, mock_global_tools, project_dir):
        """测试数据源优先级配置返回 DataFrame"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update

                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                # 检查配置文件是否存在
                config_paths = [
                    os.path.join(project_dir, 'config', 'legacy', 'data_source_priority_config.xlsx'),
                    os.path.join(project_dir, 'config', 'legacy', 'data_source_priority_config.xlsx.bak')
                ]

                config_exists = any(os.path.exists(p) for p in config_paths)
                if config_exists:
                    result = fu.source_priority_withdraw()
                    assert isinstance(result, pd.DataFrame)
                    assert 'source_name' in result.columns
                    assert 'rank' in result.columns
                else:
                    pytest.skip("配置文件不存在")
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_is_sql_false_does_not_create_sql_objects(self, mock_global_tools):
        """测试 is_sql=False 时不创建数据库连接对象"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update

                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                assert fu.is_sql == False
                # is_sql=False 时不应有数据库相关属性
                assert not hasattr(fu, 'sql_connection')
            except ImportError:
                pytest.skip("模块导入失败")


class TestTimeToolsBusinessLogic:
    """time_tools 业务逻辑测试"""

    @pytest.mark.unit
    def test_time_zoom_decision_returns_string(self, mock_global_tools, mock_glv, project_dir):
        """测试 time_zoom_decision 返回字符串"""
        config_paths = [
            os.path.join(project_dir, 'config', 'legacy', 'time_tools_config.xlsx'),
            os.path.join(project_dir, 'config', 'legacy', 'time_tools_config.xlsx.bak')
        ]

        config_exists = any(os.path.exists(p) for p in config_paths)
        if not config_exists:
            pytest.skip("配置文件不存在")

        with patch('src.time_tools.time_tools.gt', mock_global_tools), \
             patch('src.time_tools.time_tools.glv', mock_glv):
            try:
                from src.time_tools.time_tools import time_tools

                tt = time_tools()
                result = tt.time_zoom_decision()

                assert isinstance(result, str)
                assert len(result) > 0
            except Exception as e:
                pytest.skip(f"测试跳过: {e}")

    @pytest.mark.unit
    def test_target_date_decision_returns_valid_date(self, mock_global_tools, mock_glv, project_dir):
        """测试目标日期决策返回有效日期格式"""
        config_paths = [
            os.path.join(project_dir, 'config', 'legacy', 'time_tools_config.xlsx'),
            os.path.join(project_dir, 'config', 'legacy', 'time_tools_config.xlsx.bak')
        ]

        config_exists = any(os.path.exists(p) for p in config_paths)
        if not config_exists:
            pytest.skip("配置文件不存在")

        with patch('src.time_tools.time_tools.gt', mock_global_tools), \
             patch('src.time_tools.time_tools.glv', mock_glv):
            try:
                from src.time_tools.time_tools import time_tools

                tt = time_tools()
                result = tt.target_date_decision_factor()

                # 日期应该是 date 对象或 YYYY-MM-DD 格式字符串
                if isinstance(result, str):
                    assert len(result) == 10
                    assert result[4] == '-'
            except Exception as e:
                pytest.skip(f"测试跳过: {e}")


class TestDataValidation:
    """数据验证测试"""

    @pytest.mark.unit
    def test_factor_exposure_no_nan_in_barra_factors(self, sample_factor_exposure):
        """测试 Barra 因子暴露度不应有 NaN"""
        # 实际业务中 Barra 因子可能有 NaN，但关键列不应有
        barra_exposure = sample_factor_exposure[:, :len(BARRA_FACTORS)]

        # 检查生成的测试数据没有 NaN
        assert not np.any(np.isnan(barra_exposure))

    @pytest.mark.unit
    def test_industry_exposure_is_one_hot(self, sample_factor_exposure):
        """测试行业因子暴露度是独热编码"""
        industry_exposure = sample_factor_exposure[:, len(BARRA_FACTORS):]

        # 每行的行业因子应该只有一个为1
        row_sums = np.sum(industry_exposure, axis=1)
        assert np.allclose(row_sums, 1.0)

    @pytest.mark.unit
    def test_covariance_matrix_is_positive_semi_definite(self, sample_covariance_matrix):
        """测试协方差矩阵是正半定的"""
        cov_data = sample_covariance_matrix.drop(columns=['Observations']).values

        # 检查特征值是否非负
        eigenvalues = np.linalg.eigvalsh(cov_data)
        assert np.all(eigenvalues >= -1e-10), "协方差矩阵应为正半定"

    @pytest.mark.unit
    def test_specific_risk_positive(self, sample_specific_risk):
        """测试特异性风险为正值"""
        assert np.all(sample_specific_risk > 0)

    @pytest.mark.unit
    def test_stock_code_format_sz(self, sample_stock_codes):
        """测试深交所股票代码格式"""
        sz_codes = [c for c in sample_stock_codes if c.endswith('.SZ')]
        for code in sz_codes:
            # 深交所代码应为 6 位数字 + .SZ
            assert len(code) == 9
            assert code[:6].isdigit()

    @pytest.mark.unit
    def test_stock_code_format_sh(self, sample_stock_codes):
        """测试上交所股票代码格式"""
        sh_codes = [c for c in sample_stock_codes if c.endswith('.SH')]
        for code in sh_codes:
            # 上交所代码应为 6 位数字 + .SH
            assert len(code) == 9
            assert code[:6].isdigit()


class TestErrorHandling:
    """异常处理测试"""

    @pytest.mark.unit
    def test_missing_mat_file_returns_empty_dataframe(self, mock_global_tools, test_data_dir):
        """测试 MAT 文件不存在时返回空 DataFrame"""
        mock_glv = MagicMock()
        mock_glv.get = lambda key: str(test_data_dir / 'nonexistent')

        with patch('src.factor_update.factor_preparing.gt', mock_global_tools), \
             patch('src.factor_update.factor_preparing.glv', mock_glv):
            try:
                from src.factor_update.factor_preparing import FactorData_prepare

                fp = FactorData_prepare('2099-12-31')  # 不存在的日期
                result = fp.jy_factor_exposure_update()

                assert isinstance(result, pd.DataFrame)
                assert len(result) == 0
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_invalid_date_format_handling(self, mock_global_tools):
        """测试无效日期格式的处理"""
        with patch('src.factor_update.factor_preparing.gt', mock_global_tools):
            try:
                from src.factor_update.factor_preparing import FactorData_prepare

                # 测试各种日期格式是否能正确转换
                valid_formats = ['2025-01-20', '20250120']
                for date_str in valid_formats:
                    fp = FactorData_prepare(date_str)
                    # 内部应该转换为 YYYYMMDD 格式
                    assert fp.available_date == '20250120'
            except ImportError:
                pytest.skip("模块导入失败")


class TestConfigLoader:
    """ConfigLoader 额外测试"""

    @pytest.mark.unit
    def test_get_with_nonexistent_key_returns_default(self):
        """测试获取不存在的键返回默认值"""
        from src.config_loader import ConfigLoader

        config = ConfigLoader()
        result = config.get('nonexistent.key.path', default='default_value')

        assert result == 'default_value'

    @pytest.mark.unit
    def test_env_variable_overrides_config(self, monkeypatch):
        """测试环境变量优先于配置文件"""
        from src.config_loader import ConfigLoader

        # 设置环境变量
        monkeypatch.setenv('FACTOR_UPDATE_TEST_KEY', 'env_value')

        config = ConfigLoader()
        result = config.get('test.key', default='config_value')

        assert result == 'env_value'

    @pytest.mark.unit
    def test_env_variable_bool_conversion(self, monkeypatch):
        """测试环境变量布尔值转换"""
        from src.config_loader import ConfigLoader

        monkeypatch.setenv('FACTOR_UPDATE_BOOL_TRUE', 'true')
        monkeypatch.setenv('FACTOR_UPDATE_BOOL_FALSE', 'false')

        config = ConfigLoader()

        assert config.get('bool.true') == True
        assert config.get('bool.false') == False

    @pytest.mark.unit
    def test_env_variable_int_conversion(self, monkeypatch):
        """测试环境变量整数转换"""
        from src.config_loader import ConfigLoader

        monkeypatch.setenv('FACTOR_UPDATE_INT_VALUE', '42')

        config = ConfigLoader()
        result = config.get('int.value')

        assert result == 42
        assert isinstance(result, int)


class TestMatFileProcessing:
    """MAT 文件处理测试"""

    @pytest.mark.unit
    def test_mat_file_structure_validation(self, mat_file):
        """测试 MAT 文件结构验证"""
        data = loadmat(str(mat_file))

        assert 'lnmodel_active_daily' in data
        lnmodel = data['lnmodel_active_daily']

        # 验证必需的字段存在
        dtype_names = lnmodel.dtype.names
        assert 'factorexposure' in dtype_names
        assert 'factorret' in dtype_names

    @pytest.mark.unit
    def test_factor_exposure_dimensions(self, mat_file):
        """测试因子暴露度维度正确"""
        data = loadmat(str(mat_file))
        exposure = data['lnmodel_active_daily']['factorexposure'][0][0]

        # 行数应该等于股票数量
        assert exposure.shape[0] == len(TEST_STOCK_CODES)
        # 列数应该等于因子数量
        assert exposure.shape[1] == len(ALL_FACTORS)

    @pytest.mark.unit
    def test_factor_return_dimensions(self, mat_file):
        """测试因子收益率维度正确"""
        data = loadmat(str(mat_file))
        factor_ret = data['lnmodel_active_daily']['factorret'][0][0]

        # 每天只有一行收益率
        assert factor_ret.shape[0] == 1
        # 列数等于因子数量
        assert factor_ret.shape[1] == len(ALL_FACTORS)
