# -*- coding: utf-8 -*-
"""
统一配置加载器测试
"""

import os
import sys
import pytest
from pathlib import Path

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


class TestUnifiedConfig:
    """UnifiedConfig 测试"""

    @pytest.mark.unit
    def test_config_singleton(self):
        """测试单例模式"""
        from src.config.unified_config import UnifiedConfig

        config1 = UnifiedConfig()
        config2 = UnifiedConfig()

        assert config1 is config2

    @pytest.mark.unit
    def test_config_loads_app_config(self):
        """测试加载主配置文件"""
        from src.config.unified_config import config

        # 应该能获取到 dates 配置
        factor_fallback = config.get('dates.factor_fallback_start')
        assert factor_fallback is not None

    @pytest.mark.unit
    def test_config_loads_database_config(self):
        """测试加载数据库配置"""
        from src.config.unified_config import config

        db_config = config.get_database_config()
        assert isinstance(db_config, dict)

        # 检查必需字段
        if db_config:
            assert 'host' in db_config
            assert 'port' in db_config
            assert 'database' in db_config

    @pytest.mark.unit
    def test_get_with_default(self):
        """测试默认值"""
        from src.config.unified_config import config

        result = config.get('nonexistent.key', default='default_value')
        assert result == 'default_value'

    @pytest.mark.unit
    def test_get_nested_key(self):
        """测试嵌套键访问"""
        from src.config.unified_config import config

        # 访问嵌套配置
        factor_fallback = config.get('dates.factor_fallback_start')
        assert factor_fallback == '2023-06-01'

    @pytest.mark.unit
    def test_get_data_source_priority(self):
        """测试数据源优先级"""
        from src.config.unified_config import config

        priorities = config.get_data_source_priority('factor')

        assert isinstance(priorities, list)
        assert len(priorities) >= 1

        # 检查第一个数据源
        assert priorities[0]['source_name'] == 'jy'

    @pytest.mark.unit
    def test_get_source_names_ordered(self):
        """测试获取排序后的数据源名称"""
        from src.config.unified_config import config

        sources = config.get_source_names_ordered('factor')

        assert isinstance(sources, list)
        assert 'jy' in sources

    @pytest.mark.unit
    def test_get_critical_time_str(self):
        """测试获取关键时间"""
        from src.config.unified_config import config

        time_str = config.get_critical_time_str('time_1')

        assert time_str == '18:30'

    @pytest.mark.unit
    def test_get_index_mapping_short(self):
        """测试指数映射 - 短名称"""
        from src.config.unified_config import config

        short_name = config.get_index_mapping('沪深300', 'short')
        assert short_name == 'hs300'

        short_name2 = config.get_index_mapping('中证500', 'short')
        assert short_name2 == 'zz500'

    @pytest.mark.unit
    def test_get_index_mapping_monthly(self):
        """测试指数映射 - 月度名称"""
        from src.config.unified_config import config

        monthly_name = config.get_index_mapping('沪深300', 'monthly')
        assert monthly_name == 'csi300Monthly'

    @pytest.mark.unit
    def test_get_all_index_mapping(self):
        """测试获取所有指数映射"""
        from src.config.unified_config import config

        mapping = config.get_all_index_mapping('short')

        assert isinstance(mapping, dict)
        assert '沪深300' in mapping
        assert '中证500' in mapping
        assert '上证50' in mapping

    @pytest.mark.unit
    def test_get_supported_indices(self):
        """测试获取支持的指数列表"""
        from src.config.unified_config import config

        indices = config.get_supported_indices()

        assert isinstance(indices, list)
        assert len(indices) == 7
        assert '沪深300' in indices
        assert '中证1000' in indices

    @pytest.mark.unit
    def test_get_barra_factors(self):
        """测试获取 Barra 因子"""
        from src.config.unified_config import config

        factors = config.get_barra_factors()

        assert isinstance(factors, list)
        assert 'size' in factors
        assert 'beta' in factors
        assert 'momentum' in factors

    @pytest.mark.unit
    def test_get_industry_factors(self):
        """测试获取行业因子"""
        from src.config.unified_config import config

        factors = config.get_industry_factors()

        assert isinstance(factors, list)
        assert len(factors) == 30
        assert '银行' in factors
        assert '医药' in factors

    @pytest.mark.unit
    def test_get_all_factors(self):
        """测试获取所有因子"""
        from src.config.unified_config import config

        all_factors = config.get_all_factors()
        barra = config.get_barra_factors()
        industry = config.get_industry_factors()

        assert len(all_factors) == len(barra) + len(industry)

    @pytest.mark.unit
    def test_get_fallback_date(self):
        """测试获取回退日期"""
        from src.config.unified_config import config

        factor_date = config.get_fallback_date('factor')
        assert factor_date == '2023-06-01'

        yg_date = config.get_fallback_date('yg_factor')
        assert yg_date == '2024-07-05'

    @pytest.mark.unit
    def test_get_database_url(self):
        """测试获取数据库 URL"""
        from src.config.unified_config import config

        url = config.get_database_url()

        if url:
            assert 'mysql+pymysql://' in url
            assert '@' in url

    @pytest.mark.unit
    def test_get_chunk_size(self):
        """测试获取批量写入大小"""
        from src.config.unified_config import config

        chunk_size = config.get_chunk_size()

        assert isinstance(chunk_size, int)
        assert chunk_size > 0

    @pytest.mark.unit
    def test_get_workers(self):
        """测试获取并行工作线程数"""
        from src.config.unified_config import config

        workers = config.get_workers()

        assert isinstance(workers, int)
        assert workers > 0

    @pytest.mark.unit
    def test_get_logging_config(self):
        """测试获取日志配置 - logging 配置已移除"""
        from src.config.unified_config import config

        log_config = config.get_logging_config()

        # logging 配置已删除（未被代码使用），返回空字典
        assert isinstance(log_config, dict)

    @pytest.mark.unit
    def test_get_project_root(self):
        """测试获取项目根目录"""
        from src.config.unified_config import config

        root = config.get_project_root()

        assert isinstance(root, Path)
        assert root.exists()

    @pytest.mark.unit
    def test_convenience_functions(self):
        """测试便捷函数"""
        from src.config.unified_config import get_config, get_database_url

        # get_config
        result = get_config('dates.factor_fallback_start')
        assert result is not None

        # get_database_url
        url = get_database_url()
        # URL 可能为空（如果没有数据库配置），但不应该报错
        assert url is None or isinstance(url, str)

    @pytest.mark.unit
    def test_env_variable_override(self, monkeypatch):
        """测试环境变量覆盖"""
        from src.config.unified_config import UnifiedConfig

        # 重置单例
        UnifiedConfig._instance = None

        monkeypatch.setenv('FACTOR_UPDATE_APP_NAME', 'Test App')

        config = UnifiedConfig()
        result = config.get('app.name')

        assert result == 'Test App'

        # 清理
        UnifiedConfig._instance = None
