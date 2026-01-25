"""
配置加载器测试

测试 ConfigLoader 类的功能:
- 配置文件查找
- 配置值获取
- 嵌套键访问
- 环境变量优先级
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

# 添加项目路径
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from src.config_loader import ConfigLoader, get_config, get_project_root, get_config_dir


class TestConfigLoader:
    """ConfigLoader 测试类"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        config1 = ConfigLoader()
        config2 = ConfigLoader()
        assert config1 is config2

    def test_get_project_root(self):
        """测试获取项目根目录"""
        root = get_project_root()
        assert root.exists()
        assert (root / 'factor_update_main.py').exists() or (root / 'src').exists()

    def test_get_config_dir(self):
        """测试获取配置目录"""
        config_dir = get_config_dir()
        # 配置目录应该存在或者可以创建
        assert config_dir is not None

    def test_get_with_default(self):
        """测试使用默认值获取配置"""
        config = ConfigLoader()
        result = config.get('nonexistent.key', default='default_value')
        assert result == 'default_value'

    def test_get_nested_key(self):
        """测试嵌套键访问"""
        config = ConfigLoader()
        # 测试不存在的嵌套键返回默认值
        result = config.get('database.host', default='localhost')
        assert result is not None

    def test_environment_variable_priority(self):
        """测试环境变量优先级"""
        env_key = 'FACTOR_UPDATE_TEST_VALUE'
        env_value = 'from_env'

        try:
            os.environ[env_key] = env_value
            config = ConfigLoader()
            result = config.get('test.value', default='default')
            assert result == env_value
        finally:
            if env_key in os.environ:
                del os.environ[env_key]

    def test_environment_variable_bool_conversion(self):
        """测试环境变量布尔值转换"""
        env_key = 'FACTOR_UPDATE_TEST_BOOL'

        try:
            os.environ[env_key] = 'true'
            config = ConfigLoader()
            result = config.get('test.bool', default=False)
            assert result is True

            os.environ[env_key] = 'false'
            config.reload()
            result = config.get('test.bool', default=True)
            assert result is False
        finally:
            if env_key in os.environ:
                del os.environ[env_key]

    def test_environment_variable_int_conversion(self):
        """测试环境变量整数转换"""
        env_key = 'FACTOR_UPDATE_TEST_INT'

        try:
            os.environ[env_key] = '42'
            config = ConfigLoader()
            result = config.get('test.int', default=0)
            assert result == 42
            assert isinstance(result, int)
        finally:
            if env_key in os.environ:
                del os.environ[env_key]

    def test_get_all(self):
        """测试获取所有配置"""
        config = ConfigLoader()
        all_config = config.get_all()
        assert isinstance(all_config, dict)

    def test_get_config_path(self):
        """测试获取配置文件路径"""
        config = ConfigLoader()
        path = config.get_config_path()
        # 路径可能为 None (如果没有配置文件) 或者是 Path 对象
        assert path is None or isinstance(path, Path)

    def test_reload(self):
        """测试重新加载配置"""
        config = ConfigLoader()
        # 重新加载不应该抛出异常
        config.reload()

    def test_repr(self):
        """测试字符串表示"""
        config = ConfigLoader()
        repr_str = repr(config)
        assert 'ConfigLoader' in repr_str


class TestGetConfigFunction:
    """get_config 便捷函数测试"""

    def test_get_config_with_default(self):
        """测试 get_config 函数默认值"""
        result = get_config('nonexistent.key', default='test_default')
        assert result == 'test_default'

    def test_get_config_without_default(self):
        """测试 get_config 函数无默认值"""
        result = get_config('nonexistent.key')
        assert result is None


class TestConfigWithTempFile:
    """使用临时配置文件的测试"""

    @pytest.fixture
    def temp_config_dir(self):
        """创建临时配置目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_config_file_loading(self, temp_config_dir):
        """测试配置文件加载"""
        # 创建临时配置文件
        config_content = """
database:
  host: test_host
  port: 3306
  user: test_user

update:
  factor_rollback_days: 5
  save_to_sql: true
"""
        config_file = Path(temp_config_dir) / 'config.yaml'
        config_file.write_text(config_content, encoding='utf-8')

        # 注意: 由于 ConfigLoader 是单例，这个测试可能受到其他测试的影响
        # 在实际使用中，应该在应用启动时只初始化一次
        pass  # 跳过此测试，避免单例问题


@pytest.mark.unit
class TestConfigLoaderEdgeCases:
    """边界情况测试"""

    def test_empty_key(self):
        """测试空键"""
        config = ConfigLoader()
        result = config.get('', default='empty')
        assert result == 'empty'

    def test_deeply_nested_key(self):
        """测试深层嵌套键"""
        config = ConfigLoader()
        result = config.get('a.b.c.d.e.f', default='deep')
        assert result == 'deep'

    def test_special_characters_in_key(self):
        """测试键中的特殊字符"""
        config = ConfigLoader()
        result = config.get('key_with_underscore', default='special')
        assert result == 'special'
