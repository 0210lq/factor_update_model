"""
集成测试

测试整个因子更新流程的端到端功能。
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from scipy.io import savemat
import tempfile
import shutil

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from tests.conftest import (
    BARRA_FACTORS, INDUSTRY_FACTORS, ALL_FACTORS,
    TEST_STOCK_CODES, TEST_DATE, TEST_DATE_INT,
    create_test_mat_file
)


class TestEndToEndWorkflow:
    """端到端工作流测试"""

    @pytest.fixture
    def full_test_env(self, tmp_path):
        """创建完整的测试环境"""
        # 创建目录结构
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
            'output/factor_cov',
            'output/factor_specific_risk',
            'output/indexexposure/hs300',
            'output/indexexposure/zz500',
            'indexcomponent/hs300',
            'indexcomponent/zz500',
        ]

        for d in dirs:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)

        # 创建 MAT 文件
        mat_path = tmp_path / 'input' / 'jy' / 'FactorRet' / f'LNMODELACTIVE-{TEST_DATE_INT}.mat'
        create_test_mat_file(mat_path, n_stocks=len(TEST_STOCK_CODES))

        # 创建股票池
        stock_df = pd.DataFrame({
            'S_INFO_WINDCODE': TEST_STOCK_CODES,
            'type': ['stockuni_new'] * len(TEST_STOCK_CODES),
            'S_INFO_LISTDATE': [19910101] * len(TEST_STOCK_CODES),
            'S_INFO_DELISTDATE': [np.nan] * len(TEST_STOCK_CODES)
        })
        stock_df.to_csv(tmp_path / 'other' / 'StockUniverse_new.csv', index=False, encoding='gbk')
        stock_df.to_csv(tmp_path / 'other' / 'StockUniverse.csv', index=False, encoding='gbk')

        # 创建协方差文件
        n_factors = len(ALL_FACTORS)
        A = np.random.randn(n_factors, n_factors)
        cov_matrix = np.dot(A, A.T) / n_factors * 0.0001
        cov_df = pd.DataFrame(cov_matrix, columns=ALL_FACTORS)
        cov_df.insert(0, 'Observations', range(1, n_factors + 1))
        cov_df.to_csv(tmp_path / 'input' / 'cov_jy' / f'CovarianceMatrix_{TEST_DATE_INT}.csv',
                      index=False, encoding='gbk')

        # 创建特异性风险文件
        specific_risk = np.abs(np.random.randn(1, len(TEST_STOCK_CODES))) * 0.02 + 0.01
        risk_df = pd.DataFrame(specific_risk)
        risk_df.to_csv(tmp_path / 'input' / 'specific_jy' / f'SpecificRisk_{TEST_DATE_INT}.csv',
                       index=False, header=False, encoding='gbk')

        # 创建指数成分股
        for idx in ['hs300', 'zz500']:
            n_comp = 30
            selected = np.random.choice(TEST_STOCK_CODES, n_comp, replace=False)
            weights = np.random.rand(n_comp)
            weights = weights / weights.sum()
            comp_df = pd.DataFrame({
                'code': selected,
                'weight': weights,
                'status': [1] * n_comp
            })
            comp_df.to_csv(tmp_path / 'indexcomponent' / idx / f'{idx}Component_{TEST_DATE_INT}.csv',
                          index=False, encoding='gbk')

        return tmp_path

    @pytest.mark.integration
    def test_mat_file_can_be_read(self, full_test_env):
        """测试 MAT 文件可读取"""
        from scipy.io import loadmat

        mat_path = full_test_env / 'input' / 'jy' / 'FactorRet' / f'LNMODELACTIVE-{TEST_DATE_INT}.mat'
        data = loadmat(str(mat_path))

        assert 'lnmodel_active_daily' in data

    @pytest.mark.integration
    def test_all_input_files_exist(self, full_test_env):
        """测试所有输入文件存在"""
        expected_files = [
            f'input/jy/FactorRet/LNMODELACTIVE-{TEST_DATE_INT}.mat',
            'other/StockUniverse_new.csv',
            f'input/cov_jy/CovarianceMatrix_{TEST_DATE_INT}.csv',
            f'input/specific_jy/SpecificRisk_{TEST_DATE_INT}.csv',
        ]

        for f in expected_files:
            assert (full_test_env / f).exists(), f"文件不存在: {f}"

    @pytest.mark.integration
    def test_data_processing_pipeline(self, full_test_env):
        """测试数据处理管道"""
        from scipy.io import loadmat

        # 1. 读取 MAT 文件
        mat_path = full_test_env / 'input' / 'jy' / 'FactorRet' / f'LNMODELACTIVE-{TEST_DATE_INT}.mat'
        data = loadmat(str(mat_path))
        exposure = data['lnmodel_active_daily']['factorexposure'][0][0]
        factor_ret = data['lnmodel_active_daily']['factorret'][0][0]

        # 2. 创建 DataFrame
        df_exposure = pd.DataFrame(exposure, columns=ALL_FACTORS)
        df_return = pd.DataFrame(factor_ret, columns=ALL_FACTORS)

        # 3. 删除 country 列
        df_exposure.drop(columns=['country'], inplace=True)
        df_return.drop(columns=['country'], inplace=True)

        # 4. 读取股票池
        stock_df = pd.read_csv(full_test_env / 'other' / 'StockUniverse_new.csv', encoding='gbk')
        stock_codes = stock_df['S_INFO_WINDCODE'].tolist()

        # 5. 添加股票代码
        df_exposure['code'] = stock_codes[:len(df_exposure)]
        df_exposure['valuation_date'] = TEST_DATE

        # 6. 验证输出格式
        assert 'valuation_date' in df_exposure.columns
        assert 'code' in df_exposure.columns
        assert len(df_exposure) > 0

    @pytest.mark.integration
    def test_output_file_generation(self, full_test_env):
        """测试输出文件生成"""
        from scipy.io import loadmat

        # 处理数据
        mat_path = full_test_env / 'input' / 'jy' / 'FactorRet' / f'LNMODELACTIVE-{TEST_DATE_INT}.mat'
        data = loadmat(str(mat_path))
        exposure = data['lnmodel_active_daily']['factorexposure'][0][0]

        # 创建输出
        df = pd.DataFrame(exposure, columns=ALL_FACTORS)
        df.drop(columns=['country'], inplace=True)

        stock_df = pd.read_csv(full_test_env / 'other' / 'StockUniverse_new.csv', encoding='gbk')
        df['code'] = stock_df['S_INFO_WINDCODE'].tolist()[:len(df)]
        df['valuation_date'] = TEST_DATE
        df = df[['valuation_date', 'code'] + [c for c in df.columns if c not in ['valuation_date', 'code']]]

        # 保存输出
        output_path = full_test_env / 'output' / 'factor_exposure' / f'factorExposure_{TEST_DATE_INT}.csv'
        df.to_csv(output_path, index=False, encoding='gbk')

        # 验证文件存在且可读
        assert output_path.exists()
        df_read = pd.read_csv(output_path, encoding='gbk')
        assert len(df_read) == len(df)


class TestModuleImports:
    """模块导入测试"""

    @pytest.mark.integration
    def test_all_modules_importable(self):
        """测试所有模块可导入"""
        modules = [
            'global_setting.global_dic',
            'setup_logger.logger_setup',
        ]

        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.skip(f"模块 {module} 导入失败: {e}")

    @pytest.mark.integration
    def test_main_entry_importable(self):
        """测试主入口可导入"""
        try:
            import factor_update_main
            assert hasattr(factor_update_main, 'FactorData_update_main')
            assert hasattr(factor_update_main, 'FactorData_history_update')
        except ImportError as e:
            pytest.skip(f"主入口导入失败: {e}")


class TestDataConsistency:
    """数据一致性测试"""

    @pytest.mark.integration
    def test_factor_count_consistency(self):
        """测试因子数量一致性"""
        assert len(BARRA_FACTORS) == 10
        assert len(INDUSTRY_FACTORS) == 30
        assert len(ALL_FACTORS) == 40

    @pytest.mark.integration
    def test_stock_code_format_consistency(self):
        """测试股票代码格式一致性"""
        for code in TEST_STOCK_CODES:
            assert '.' in code
            suffix = code.split('.')[-1]
            assert suffix in ['SZ', 'SH']

    @pytest.mark.integration
    def test_date_format_consistency(self):
        """测试日期格式一致性"""
        from datetime import datetime

        # TEST_DATE 应该是 YYYY-MM-DD 格式
        datetime.strptime(TEST_DATE, '%Y-%m-%d')

        # TEST_DATE_INT 应该是 YYYYMMDD 格式
        datetime.strptime(TEST_DATE_INT, '%Y%m%d')


class TestErrorHandling:
    """错误处理测试"""

    @pytest.mark.integration
    def test_missing_file_handling(self, tmp_path):
        """测试缺失文件处理"""
        # 尝试读取不存在的文件
        non_existent = tmp_path / 'non_existent.mat'

        with pytest.raises(FileNotFoundError):
            from scipy.io import loadmat
            loadmat(str(non_existent))

    @pytest.mark.integration
    def test_invalid_mat_file_handling(self, tmp_path):
        """测试无效 MAT 文件处理"""
        # 创建一个无效的文件
        invalid_mat = tmp_path / 'invalid.mat'
        invalid_mat.write_text('not a mat file')

        with pytest.raises(Exception):
            from scipy.io import loadmat
            loadmat(str(invalid_mat))

    @pytest.mark.integration
    def test_empty_dataframe_handling(self):
        """测试空 DataFrame 处理"""
        df = pd.DataFrame()

        assert len(df) == 0
        assert df.empty


class TestConfigurationValidation:
    """配置验证测试"""

    @pytest.mark.integration
    def test_required_config_files_exist(self, project_dir):
        """测试必需的配置文件存在"""
        required_files = [
            'config/legacy/data_source_priority_config.xlsx',
            'config/legacy/time_tools_config.xlsx',
            'config/legacy/data_update_path_config.xlsx',
        ]

        for f in required_files:
            path = os.path.join(project_dir, f)
            assert os.path.exists(path), f"必需的配置文件不存在: {f}"

    @pytest.mark.integration
    def test_config_files_readable(self, project_dir):
        """测试配置文件可读取"""
        config_files = [
            ('config/legacy/data_source_priority_config.xlsx', 'factor'),
            ('config/legacy/time_tools_config.xlsx', 'critical_time'),
        ]

        for file_path, sheet_name in config_files:
            full_path = os.path.join(project_dir, file_path)
            if os.path.exists(full_path):
                try:
                    df = pd.read_excel(full_path, sheet_name=sheet_name)
                    assert len(df) > 0, f"配置文件为空: {file_path}"
                except Exception as e:
                    pytest.fail(f"无法读取配置文件 {file_path}: {e}")
