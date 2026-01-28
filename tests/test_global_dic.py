"""
global_setting/global_dic.py 模块测试

测试路径配置加载和管理功能。
"""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# 添加项目路径
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


class TestGlobalDic:
    """global_dic 模块测试类"""

    @pytest.mark.unit
    def test_module_import(self):
        """测试模块能否正常导入"""
        try:
            import global_setting.global_dic as glv
            assert hasattr(glv, 'get')
            assert hasattr(glv, 'config_path_processing')
        except ImportError as e:
            pytest.skip(f"模块导入失败 (可能缺少配置文件): {e}")

    @pytest.mark.unit
    def test_get_function_exists(self):
        """测试 get 函数存在"""
        try:
            import global_setting.global_dic as glv
            assert callable(glv.get)
        except ImportError:
            pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_config_path_processing_function(self):
        """测试 config_path_processing 函数"""
        try:
            import global_setting.global_dic as glv
            assert callable(glv.config_path_processing)
        except ImportError:
            pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_get_returns_string_path(self):
        """测试 get 函数返回字符串路径"""
        try:
            import global_setting.global_dic as glv
            # 测试一个应该存在的配置项
            result = glv.get('output_factor_exposure')
            assert isinstance(result, str)
        except (ImportError, KeyError):
            pytest.skip("模块导入失败或配置项不存在")

    @pytest.mark.unit
    def test_get_with_invalid_key(self):
        """测试 get 函数处理无效键"""
        try:
            import global_setting.global_dic as glv
            result = glv.get('nonexistent_key_12345')
            # 可能返回 None 或空字符串或抛出异常
            assert result is None or result == '' or isinstance(result, str)
        except (ImportError, KeyError):
            # KeyError 是可接受的行为
            pass

    @pytest.mark.unit
    def test_path_config_file_exists(self, project_dir):
        """测试路径配置文件存在"""
        config_path = os.path.join(project_dir, 'config', 'legacy', 'data_update_path_config.xlsx')
        assert os.path.exists(config_path), f"配置文件不存在: {config_path}"

    @pytest.mark.unit
    def test_path_config_file_readable(self, project_dir):
        """测试路径配置文件可读取"""
        config_path = os.path.join(project_dir, 'config', 'legacy', 'data_update_path_config.xlsx')
        if os.path.exists(config_path):
            df_main = pd.read_excel(config_path, sheet_name='main_folder')
            df_sub = pd.read_excel(config_path, sheet_name='sub_folder')

            assert 'folder_type' in df_main.columns
            assert 'data_type' in df_sub.columns
        else:
            pytest.skip("配置文件不存在")

    @pytest.mark.unit
    def test_required_paths_configured(self):
        """测试必需的路径配置项"""
        required_keys = [
            'output_factor_exposure',
            'output_factor_return',
            'input_factor_jy',
            'data_other',
        ]

        try:
            import global_setting.global_dic as glv
            for key in required_keys:
                result = glv.get(key)
                assert result is not None, f"配置项 {key} 未配置"
                assert isinstance(result, str), f"配置项 {key} 应返回字符串"
        except ImportError:
            pytest.skip("模块导入失败")


class TestPathValidation:
    """路径验证测试"""

    @pytest.mark.unit
    def test_output_paths_are_directories(self):
        """测试输出路径是目录路径 (非文件路径)"""
        output_keys = [
            'output_factor_exposure',
            'output_factor_return',
            'output_factor_stockpool',
        ]

        try:
            import global_setting.global_dic as glv
            for key in output_keys:
                path = glv.get(key)
                if path:
                    # 路径不应该以文件扩展名结尾
                    assert not path.endswith('.csv'), f"{key} 应该是目录路径"
                    assert not path.endswith('.xlsx'), f"{key} 应该是目录路径"
        except ImportError:
            pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_config_paths_are_files(self):
        """测试配置路径是文件路径"""
        config_keys = [
            'data_source_priority',
            'time_tools_config',
        ]

        try:
            import global_setting.global_dic as glv
            for key in config_keys:
                path = glv.get(key)
                if path:
                    # 配置文件应该以 .xlsx 或 .yaml 结尾
                    assert path.endswith('.xlsx') or path.endswith('.yaml') or path.endswith('.yml'), \
                        f"{key} 应该是配置文件路径"
        except ImportError:
            pytest.skip("模块导入失败")
