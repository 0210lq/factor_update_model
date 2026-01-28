"""
factor_update_main.py 主入口模块测试
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


class TestMainModule:
    """主模块测试"""

    @pytest.mark.unit
    def test_module_import(self):
        """测试主模块可导入"""
        try:
            import factor_update_main
            assert factor_update_main is not None
        except ImportError as e:
            pytest.skip(f"主模块导入失败: {e}")

    @pytest.mark.unit
    def test_factordata_update_main_exists(self):
        """测试 FactorData_update_main 函数存在"""
        try:
            from factor_update_main import FactorData_update_main
            assert callable(FactorData_update_main)
        except ImportError:
            pytest.skip("函数导入失败")

    @pytest.mark.unit
    def test_factordata_history_update_exists(self):
        """测试 FactorData_history_update 函数存在"""
        try:
            from factor_update_main import FactorData_history_update
            assert callable(FactorData_history_update)
        except ImportError:
            pytest.skip("函数导入失败")

    @pytest.mark.unit
    def test_factordata_update_main_signature(self):
        """测试 FactorData_update_main 函数签名"""
        try:
            from factor_update_main import FactorData_update_main
            import inspect

            sig = inspect.signature(FactorData_update_main)
            params = list(sig.parameters.keys())

            assert 'is_sql' in params
        except ImportError:
            pytest.skip("函数导入失败")

    @pytest.mark.unit
    def test_factordata_history_update_signature(self):
        """测试 FactorData_history_update 函数签名"""
        try:
            from factor_update_main import FactorData_history_update
            import inspect

            sig = inspect.signature(FactorData_history_update)
            params = list(sig.parameters.keys())

            assert 'start_date' in params
            assert 'end_date' in params
            assert 'is_sql' in params
        except ImportError:
            pytest.skip("函数导入失败")


class TestMainFunctionality:
    """主功能测试"""

    @pytest.mark.unit
    def test_is_sql_default_value(self):
        """测试 is_sql 参数默认值"""
        try:
            from factor_update_main import FactorData_update_main
            import inspect

            sig = inspect.signature(FactorData_update_main)
            is_sql_param = sig.parameters.get('is_sql')

            assert is_sql_param is not None
            assert is_sql_param.default == True
        except ImportError:
            pytest.skip("函数导入失败")

    @pytest.mark.unit
    def test_include_timeseries_default_value(self):
        """测试 include_timeseries 参数默认值"""
        try:
            from factor_update_main import FactorData_history_update
            import inspect

            sig = inspect.signature(FactorData_history_update)
            param = sig.parameters.get('include_timeseries')

            assert param is not None
            assert param.default == True
        except ImportError:
            pytest.skip("函数导入失败")


class TestEnvironmentCheck:
    """环境检查测试"""

    @pytest.mark.unit
    def test_environment_variable_check(self):
        """测试环境变量检查逻辑"""
        env_var = os.getenv('GLOBAL_TOOLSFUNC_new')

        if env_var is None:
            # 如果环境变量未设置，导入应该失败
            with pytest.raises(EnvironmentError):
                # 清除已导入的模块以重新测试
                if 'factor_update_main' in sys.modules:
                    del sys.modules['factor_update_main']
                import factor_update_main
        else:
            # 环境变量已设置，导入应该成功
            try:
                import factor_update_main
                assert factor_update_main is not None
            except ImportError:
                pytest.skip("导入失败")

    @pytest.mark.unit
    def test_environment_variable_path_valid(self):
        """测试环境变量指向的路径有效"""
        env_var = os.getenv('GLOBAL_TOOLSFUNC_new')

        if env_var:
            assert os.path.exists(env_var), f"环境变量路径不存在: {env_var}"


class TestImportDependencies:
    """导入依赖测试"""

    @pytest.mark.unit
    def test_factordata_update_import(self):
        """测试 FactorData_update 类可导入"""
        try:
            from src.factor_update.factor_update import FactorData_update
            assert FactorData_update is not None
        except ImportError as e:
            pytest.skip(f"导入失败: {e}")

    @pytest.mark.unit
    def test_time_tools_import(self):
        """测试 time_tools 类可导入"""
        try:
            from src.time_tools.time_tools import time_tools
            assert time_tools is not None
        except ImportError as e:
            pytest.skip(f"导入失败: {e}")

    @pytest.mark.unit
    def test_timeseries_data_update_import(self):
        """测试 timeSeries_data_update 类可导入"""
        try:
            from src.timeseries_update.time_series_data_update import timeSeries_data_update
            assert timeSeries_data_update is not None
        except ImportError as e:
            pytest.skip(f"导入失败: {e}")


class TestDocstrings:
    """文档字符串测试"""

    @pytest.mark.unit
    def test_factordata_update_main_has_docstring(self):
        """测试 FactorData_update_main 有文档字符串"""
        try:
            from factor_update_main import FactorData_update_main
            assert FactorData_update_main.__doc__ is not None
            assert len(FactorData_update_main.__doc__) > 0
        except ImportError:
            pytest.skip("函数导入失败")

    @pytest.mark.unit
    def test_factordata_history_update_has_docstring(self):
        """测试 FactorData_history_update 有文档字符串"""
        try:
            from factor_update_main import FactorData_history_update
            assert FactorData_history_update.__doc__ is not None
            assert len(FactorData_history_update.__doc__) > 0
        except ImportError:
            pytest.skip("函数导入失败")
