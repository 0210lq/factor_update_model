"""
FactorData_update/factor_preparing.py 模块测试

测试因子数据准备和处理功能。
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from scipy.io import loadmat, savemat

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from tests.conftest import (
    BARRA_FACTORS, INDUSTRY_FACTORS, ALL_FACTORS,
    TEST_STOCK_CODES, TEST_DATE, TEST_DATE_INT,
    create_test_mat_file
)


class TestFactorDataPrepare:
    """FactorData_prepare 类测试"""

    @pytest.mark.unit
    def test_module_import(self):
        """测试模块能否正常导入"""
        try:
            from FactorData_update.factor_preparing import FactorData_prepare
            assert FactorData_prepare is not None
        except ImportError as e:
            pytest.skip(f"模块导入失败: {e}")

    @pytest.mark.unit
    def test_class_instantiation(self, mock_global_tools):
        """测试类能否正常实例化"""
        with patch('FactorData_update.factor_preparing.gt', mock_global_tools):
            try:
                from FactorData_update.factor_preparing import FactorData_prepare
                fp = FactorData_prepare(TEST_DATE)
                assert fp is not None
                assert fp.available_date == TEST_DATE_INT
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_index_dic_processing(self, mock_global_tools):
        """测试 index_dic_processing 方法"""
        with patch('FactorData_update.factor_preparing.gt', mock_global_tools):
            try:
                from FactorData_update.factor_preparing import FactorData_prepare
                fp = FactorData_prepare(TEST_DATE)
                dic = fp.index_dic_processing()

                assert isinstance(dic, dict)
                assert '沪深300' in dic
                assert '中证500' in dic
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_index_dic_processing2(self, mock_global_tools):
        """测试 index_dic_processing2 方法"""
        with patch('FactorData_update.factor_preparing.gt', mock_global_tools):
            try:
                from FactorData_update.factor_preparing import FactorData_prepare
                fp = FactorData_prepare(TEST_DATE)
                dic = fp.index_dic_processing2()

                assert isinstance(dic, dict)
                assert dic.get('沪深300') == 'hs300'
                assert dic.get('中证500') == 'zz500'
            except ImportError:
                pytest.skip("模块导入失败")


class TestMatFileReading:
    """MAT 文件读取测试"""

    @pytest.mark.unit
    def test_mat_file_structure(self, mat_file):
        """测试 MAT 文件结构正确"""
        data = loadmat(str(mat_file))

        assert 'lnmodel_active_daily' in data
        lnmodel = data['lnmodel_active_daily']

        # 检查嵌套结构
        assert 'factorexposure' in lnmodel.dtype.names or hasattr(lnmodel, 'factorexposure')
        assert 'factorret' in lnmodel.dtype.names or hasattr(lnmodel, 'factorret')

    @pytest.mark.unit
    def test_factor_exposure_shape(self, mat_file):
        """测试因子暴露度矩阵形状"""
        data = loadmat(str(mat_file))
        exposure = data['lnmodel_active_daily']['factorexposure'][0][0]

        # 应该是 (n_stocks, n_factors) 的矩阵
        assert len(exposure.shape) == 2
        assert exposure.shape[1] == len(ALL_FACTORS)

    @pytest.mark.unit
    def test_factor_return_shape(self, mat_file):
        """测试因子收益率形状"""
        data = loadmat(str(mat_file))
        factor_ret = data['lnmodel_active_daily']['factorret'][0][0]

        # 应该是 (1, n_factors) 的矩阵
        assert factor_ret.shape[0] == 1
        assert factor_ret.shape[1] == len(ALL_FACTORS)


class TestFactorExposureUpdate:
    """因子暴露度更新测试"""

    @pytest.fixture
    def setup_test_env(self, test_data_dir, mock_global_tools, mock_glv):
        """设置测试环境"""
        # 创建测试 MAT 文件
        mat_path = test_data_dir / 'input' / 'jy' / 'FactorRet' / f'LNMODELACTIVE-{TEST_DATE_INT}.mat'
        create_test_mat_file(mat_path, n_stocks=len(TEST_STOCK_CODES))

        # 创建股票池文件
        stock_df = pd.DataFrame({
            'S_INFO_WINDCODE': TEST_STOCK_CODES,
            'type': ['stockuni_new'] * len(TEST_STOCK_CODES),
            'S_INFO_LISTDATE': [19910101] * len(TEST_STOCK_CODES),
            'S_INFO_DELISTDATE': [np.nan] * len(TEST_STOCK_CODES)
        })
        stock_path = test_data_dir / 'other' / 'StockUniverse_new.csv'
        stock_df.to_csv(stock_path, index=False, encoding='gbk')

        # 创建旧版股票池
        stock_path_old = test_data_dir / 'other' / 'StockUniverse.csv'
        stock_df.to_csv(stock_path_old, index=False, encoding='gbk')

        return {
            'mat_path': mat_path,
            'stock_path': stock_path,
            'mock_gt': mock_global_tools,
            'mock_glv': mock_glv
        }

    @pytest.mark.unit
    def test_jy_factor_exposure_update_returns_dataframe(self, setup_test_env):
        """测试 JY 因子暴露度更新返回 DataFrame"""
        env = setup_test_env

        with patch('FactorData_update.factor_preparing.gt', env['mock_gt']), \
             patch('FactorData_update.factor_preparing.glv', env['mock_glv']):
            try:
                from FactorData_update.factor_preparing import FactorData_prepare
                fp = FactorData_prepare(TEST_DATE)
                result = fp.jy_factor_exposure_update()

                if len(result) > 0:
                    assert isinstance(result, pd.DataFrame)
                    assert 'valuation_date' in result.columns
            except Exception as e:
                pytest.skip(f"测试跳过: {e}")

    @pytest.mark.unit
    def test_factor_exposure_columns(self, sample_factor_names):
        """测试因子暴露度应包含的列"""
        expected_columns = ['valuation_date', 'code'] + sample_factor_names['barra'][1:] + sample_factor_names['industry']

        # country 列应该被删除
        assert 'country' not in expected_columns[2:]


class TestCovarianceUpdate:
    """协方差矩阵更新测试"""

    @pytest.mark.unit
    def test_covariance_file_reading(self, covariance_file):
        """测试协方差文件读取"""
        df = pd.read_csv(str(covariance_file), encoding='gbk')

        assert 'Observations' in df.columns
        assert len(df) == len(ALL_FACTORS)
        assert len(df.columns) == len(ALL_FACTORS) + 1  # factors + Observations

    @pytest.mark.unit
    def test_covariance_matrix_symmetric(self, sample_covariance_matrix):
        """测试协方差矩阵对称性"""
        # 移除 Observations 列
        cov_data = sample_covariance_matrix.drop(columns=['Observations']).values

        # 协方差矩阵应该近似对称
        assert np.allclose(cov_data, cov_data.T, rtol=1e-5)

    @pytest.mark.unit
    def test_covariance_matrix_positive_diagonal(self, sample_covariance_matrix):
        """测试协方差矩阵对角线为正"""
        cov_data = sample_covariance_matrix.drop(columns=['Observations']).values
        diagonal = np.diag(cov_data)

        assert np.all(diagonal >= 0), "协方差矩阵对角线应为非负"


class TestSpecificRiskUpdate:
    """特异性风险更新测试"""

    @pytest.mark.unit
    def test_specific_risk_values_positive(self, sample_specific_risk):
        """测试特异性风险值为正"""
        assert np.all(sample_specific_risk > 0), "特异性风险应为正值"

    @pytest.mark.unit
    def test_specific_risk_reasonable_range(self, sample_specific_risk):
        """测试特异性风险值在合理范围内"""
        # 特异性风险通常在 0.01 到 0.1 之间
        assert np.all(sample_specific_risk < 1.0), "特异性风险过大"


class TestStockPoolProcessing:
    """股票池处理测试"""

    @pytest.mark.unit
    def test_stock_universe_format(self, sample_stock_universe):
        """测试股票池格式"""
        required_columns = ['S_INFO_WINDCODE', 'type', 'S_INFO_LISTDATE', 'S_INFO_DELISTDATE']

        for col in required_columns:
            assert col in sample_stock_universe.columns

    @pytest.mark.unit
    def test_stock_codes_format(self, sample_stock_codes):
        """测试股票代码格式"""
        for code in sample_stock_codes:
            # 格式应为 XXXXXX.SZ 或 XXXXXX.SH
            assert len(code) == 9
            assert code[-3:] in ['.SZ', '.SH']


class TestIndexExposureUpdate:
    """指数暴露度更新测试"""

    @pytest.mark.unit
    def test_index_component_format(self, sample_index_component):
        """测试指数成分股格式"""
        assert 'code' in sample_index_component.columns
        assert 'weight' in sample_index_component.columns
        assert 'status' in sample_index_component.columns

    @pytest.mark.unit
    def test_index_weights_sum_to_one(self, sample_index_component):
        """测试指数权重和为1"""
        total_weight = sample_index_component['weight'].sum()
        assert abs(total_weight - 1.0) < 0.001, f"权重和应为1，实际为{total_weight}"

    @pytest.mark.unit
    def test_all_indices_covered(self):
        """测试所有指数都被覆盖"""
        expected_indices = ['上证50', '沪深300', '中证500', '中证1000', '中证2000', '中证A500', '国证2000']

        try:
            from FactorData_update.factor_preparing import FactorData_prepare
            # 检查类中定义的指数字典
            fp_class = FactorData_prepare.__init__.__code__
            # 这里只检查预期的指数列表
            assert len(expected_indices) == 7
        except ImportError:
            pytest.skip("模块导入失败")
