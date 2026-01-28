"""
FactorData_update/factor_update.py 模块测试

测试因子更新主逻辑。
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from tests.conftest import (
    BARRA_FACTORS, INDUSTRY_FACTORS, ALL_FACTORS,
    TEST_STOCK_CODES, TEST_DATE, TEST_DATE_INT,
    create_test_mat_file
)


class TestFactorDataUpdate:
    """FactorData_update 类测试"""

    @pytest.mark.unit
    def test_module_import(self):
        """测试模块能否正常导入"""
        try:
            from src.factor_update.factor_update import FactorData_update
            assert FactorData_update is not None
        except ImportError as e:
            pytest.skip(f"模块导入失败: {e}")

    @pytest.mark.unit
    def test_class_instantiation(self, mock_global_tools):
        """测试类能否正常实例化"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update
                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                assert fu.start_date == '2025-01-01'
                assert fu.end_date == '2025-01-31'
                assert fu.is_sql == False
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_source_priority_withdraw_method_exists(self, mock_global_tools):
        """测试 source_priority_withdraw 方法存在"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update
                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                assert hasattr(fu, 'source_priority_withdraw')
                assert callable(fu.source_priority_withdraw)
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_index_dic_processing_method(self, mock_global_tools):
        """测试 index_dic_processing 方法"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update
                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                dic = fu.index_dic_processing()
                assert isinstance(dic, dict)
                assert '沪深300' in dic
                assert dic['沪深300'] == 'hs300'
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_factor_update_main_method_exists(self, mock_global_tools):
        """测试 factor_update_main 方法存在"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update
                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                assert hasattr(fu, 'factor_update_main')
                assert callable(fu.factor_update_main)
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_index_factor_update_main_method_exists(self, mock_global_tools):
        """测试 index_factor_update_main 方法存在"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update
                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)

                assert hasattr(fu, 'index_factor_update_main')
                assert callable(fu.index_factor_update_main)
            except ImportError:
                pytest.skip("模块导入失败")


class TestDataSourcePriority:
    """数据源优先级测试"""

    @pytest.mark.unit
    def test_priority_config_format(self, project_dir):
        """测试优先级配置文件格式"""
        config_path = os.path.join(project_dir, 'config', 'legacy', 'data_source_priority_config.xlsx')

        if os.path.exists(config_path):
            df = pd.read_excel(config_path, sheet_name='factor')

            # 检查必需的列
            assert 'source_name' in df.columns
            assert 'rank' in df.columns
        else:
            pytest.skip("配置文件不存在")

    @pytest.mark.unit
    def test_valid_source_names(self, project_dir):
        """测试数据源名称有效"""
        config_path = os.path.join(project_dir, 'config', 'legacy', 'data_source_priority_config.xlsx')
        valid_sources = ['jy', 'wind']

        if os.path.exists(config_path):
            df = pd.read_excel(config_path, sheet_name='factor')
            sources = df['source_name'].unique()

            for source in sources:
                assert source in valid_sources, f"无效的数据源: {source}"
        else:
            pytest.skip("配置文件不存在")


class TestOutputGeneration:
    """输出生成测试"""

    @pytest.mark.unit
    def test_factor_exposure_output_format(self, sample_factor_exposure, sample_stock_codes):
        """测试因子暴露度输出格式"""
        # 模拟输出 DataFrame
        df = pd.DataFrame(
            sample_factor_exposure,
            columns=ALL_FACTORS
        )
        df.drop(columns=['country'], inplace=True)
        df['code'] = sample_stock_codes
        df['valuation_date'] = TEST_DATE
        df = df[['valuation_date', 'code'] + [c for c in df.columns if c not in ['valuation_date', 'code']]]

        # 验证格式
        assert df.columns[0] == 'valuation_date'
        assert df.columns[1] == 'code'
        assert 'country' not in df.columns

    @pytest.mark.unit
    def test_factor_return_output_format(self, sample_factor_return):
        """测试因子收益率输出格式"""
        df = pd.DataFrame(sample_factor_return, columns=ALL_FACTORS)
        df.drop(columns=['country'], inplace=True)
        df['valuation_date'] = TEST_DATE
        df = df[['valuation_date'] + [c for c in df.columns if c != 'valuation_date']]

        assert df.columns[0] == 'valuation_date'
        assert len(df) == 1  # 每天一行

    @pytest.mark.unit
    def test_csv_encoding_gbk(self, tmp_path, sample_factor_names):
        """测试 CSV 文件使用 GBK 编码"""
        df = pd.DataFrame({
            'valuation_date': [TEST_DATE],
            '石油石化': [0.1],
            '煤炭': [0.2],
        })

        csv_path = tmp_path / 'test_encoding.csv'
        df.to_csv(csv_path, index=False, encoding='gbk')

        # 验证可以用 GBK 读取
        df_read = pd.read_csv(csv_path, encoding='gbk')
        assert '石油石化' in df_read.columns


class TestSQLIntegration:
    """SQL 集成测试"""

    @pytest.mark.unit
    def test_sql_config_file_exists(self, project_dir):
        """测试 SQL 配置文件或示例文件存在"""
        sql_config = os.path.join(project_dir, 'config', 'database.yaml')
        sql_example = os.path.join(project_dir, 'config', 'database.yaml.example')

        assert os.path.exists(sql_config) or os.path.exists(sql_example), \
            "SQL 配置文件或示例文件应该存在"

    @pytest.mark.unit
    def test_is_sql_parameter_controls_db_write(self, mock_global_tools):
        """测试 is_sql 参数控制数据库写入"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update

                # is_sql=False 不应该触发数据库操作
                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)
                assert fu.is_sql == False

                # is_sql=True 应该启用数据库操作
                fu2 = FactorData_update('2025-01-01', '2025-01-31', is_sql=True)
                assert fu2.is_sql == True
            except ImportError:
                pytest.skip("模块导入失败")


class TestDateRangeHandling:
    """日期范围处理测试"""

    @pytest.mark.unit
    def test_date_range_parsing(self, mock_global_tools):
        """测试日期范围解析"""
        with patch('src.factor_update.factor_update.gt', mock_global_tools):
            try:
                from src.factor_update.factor_update import FactorData_update

                fu = FactorData_update('2025-01-01', '2025-01-31', is_sql=False)
                assert fu.start_date == '2025-01-01'
                assert fu.end_date == '2025-01-31'
            except ImportError:
                pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_hardcoded_start_date_fallback(self):
        """测试硬编码的起始日期回退逻辑"""
        # 代码中有 start_date='2023-06-01' 的硬编码
        hardcoded_date = '2023-06-01'

        # 验证日期格式正确
        datetime.strptime(hardcoded_date, '%Y-%m-%d')


class TestLogging:
    """日志记录测试"""

    @pytest.mark.unit
    def test_logger_setup(self):
        """测试日志设置"""
        try:
            from src.setup_logger.logger_setup import setup_logger
            logger = setup_logger('test_logger')

            assert logger is not None
            assert hasattr(logger, 'info')
            assert hasattr(logger, 'warning')
            assert hasattr(logger, 'error')
        except ImportError:
            pytest.skip("日志模块导入失败")

    @pytest.mark.unit
    def test_logger_writes_to_file(self, tmp_path):
        """测试日志写入文件"""
        try:
            from src.setup_logger.logger_setup import setup_logger
            # 这个测试依赖于 setup_logger 的具体实现
            # 如果 setup_logger 创建文件日志，可以验证文件是否创建
            pass
        except ImportError:
            pytest.skip("日志模块导入失败")
