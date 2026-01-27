# -*- coding: utf-8 -*-
"""
统一配置加载器

整合了项目中的所有配置文件，提供统一的配置访问接口。
支持新配置结构，同时兼容旧配置文件。

使用方法:
    from src.config.unified_config import config

    # 获取数据库配置
    db_host = config.get('database.host')

    # 获取路径配置
    factor_jy_path = config.get_path('input.factor_jy')

    # 获取数据源优先级
    priorities = config.get_data_source_priority('factor')

    # 获取时间配置
    critical_time = config.get_critical_time('time_1')

    # 获取指数映射
    index_short = config.get_index_mapping('沪深300', 'short')
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import time


class UnifiedConfig:
    """
    统一配置加载器 - 单例模式

    整合了以下配置：
    - app_config.yaml: 主配置（路径、数据源、时间、常量）
    - database.yaml: 数据库连接配置
    - tables/dataUpdate_sql.yaml: 数据表定义
    """

    _instance = None
    _app_config: Dict[str, Any] = {}
    _db_config: Dict[str, Any] = {}
    _tables_config: Dict[str, Any] = {}
    _project_root: Optional[Path] = None
    _config_dir: Optional[Path] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """初始化配置"""
        self._find_project_root()
        self._load_all_configs()

    def _find_project_root(self) -> None:
        """查找项目根目录"""
        current = Path(__file__).resolve().parent

        # 向上查找包含 config/app_config.yaml 的位置
        for _ in range(10):
            config_dir = current / 'config'
            app_config = config_dir / 'app_config.yaml'
            if app_config.exists():
                self._project_root = current
                self._config_dir = config_dir
                return
            parent = current.parent
            if parent == current:
                break
            current = parent

        # 回退到默认位置 (从 src/config/ 向上两级)
        self._project_root = Path(__file__).resolve().parent.parent.parent
        self._config_dir = self._project_root / 'config'

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """加载 YAML 文件"""
        if not file_path.exists():
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"警告: 加载配置文件失败 {file_path}: {e}")
            return {}

    def _load_all_configs(self) -> None:
        """加载所有配置文件"""
        if self._config_dir is None:
            return

        # 加载主配置
        app_config_path = self._config_dir / 'app_config.yaml'
        self._app_config = self._load_yaml(app_config_path)

        # 加载数据库配置
        db_config_path = self._config_dir / 'database.yaml'
        self._db_config = self._load_yaml(db_config_path)

        # 加载数据表配置
        tables_config_path = self._config_dir / 'tables' / 'dataUpdate_sql.yaml'
        self._tables_config = self._load_yaml(tables_config_path)

    def get(self, key: str, default: Any = None, env_prefix: str = 'FACTOR_UPDATE_') -> Any:
        """
        获取配置值，支持嵌套键访问

        Args:
            key: 配置键，支持点号分隔 (如 'database.host')
            default: 默认值
            env_prefix: 环境变量前缀

        Returns:
            配置值
        """
        # 优先检查环境变量
        env_key = f"{env_prefix}{key.upper().replace('.', '_')}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return self._convert_env_value(env_value)

        # 先在数据库配置中查找
        if key.startswith('database.') or key.startswith('connection_pool.'):
            value = self._get_nested(self._db_config, key)
            if value is not None:
                return value

        # 在主配置中查找
        value = self._get_nested(self._app_config, key)
        return value if value is not None else default

    def _get_nested(self, config: Dict, key: str) -> Any:
        """获取嵌套配置值"""
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value

    def _convert_env_value(self, value: str) -> Any:
        """转换环境变量值的类型"""
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    # ==================== 路径配置 ====================

    def get_path(self, path_key: str, base_folder: str = None) -> str:
        """
        获取完整路径

        Args:
            path_key: 路径键 (如 'input.factor_jy', 'output.factor_exposure')
            base_folder: 基础目录类型 ('input', 'output', 'config')

        Returns:
            完整路径字符串
        """
        paths_config = self._app_config.get('paths', {})

        # 解析路径键
        parts = path_key.split('.')
        if len(parts) == 2:
            category, name = parts
        else:
            category = None
            name = path_key

        # 获取相对路径
        if category:
            relative_path = paths_config.get(category, {}).get(name, '')
        else:
            # 在所有类别中查找
            for cat in ['input', 'output', 'other', 'config']:
                if name in paths_config.get(cat, {}):
                    relative_path = paths_config[cat][name]
                    category = cat
                    break
            else:
                relative_path = ''

        if not relative_path:
            return ''

        # 确定基础目录
        base_folders = paths_config.get('base_folders', {})
        if category == 'input':
            base_info = base_folders.get('input_folder', {})
        elif category == 'output':
            base_info = base_folders.get('output_folder', {})
        elif category == 'config':
            base_info = base_folders.get('config_folder', {})
        else:
            base_info = base_folders.get('input_folder', {})

        base_path = base_info.get('path', '')
        mode = base_info.get('mode', 'relative')

        # 构建完整路径
        if mode == 'absolute':
            # 绝对路径模式：从磁盘根目录开始
            full_path = Path('D:/') / base_path / relative_path
        elif mode == 'relative':
            # 相对路径模式：从项目根目录开始
            full_path = self._project_root / base_path / relative_path
        else:
            full_path = self._project_root / relative_path

        return str(full_path)

    def get_project_root(self) -> Path:
        """获取项目根目录"""
        return self._project_root

    def get_config_dir(self) -> Path:
        """获取配置目录"""
        return self._config_dir

    # ==================== 数据源优先级 ====================

    def get_data_source_priority(self, data_type: str = 'factor') -> List[Dict[str, Any]]:
        """
        获取数据源优先级列表

        Args:
            data_type: 数据类型 ('factor' 等)

        Returns:
            按优先级排序的数据源列表
        """
        priority_config = self._app_config.get('data_source_priority', {})
        sources = priority_config.get(data_type, [])

        # 按 rank 排序
        return sorted(sources, key=lambda x: x.get('rank', 999))

    def get_source_names_ordered(self, data_type: str = 'factor') -> List[str]:
        """获取按优先级排序的数据源名称列表"""
        priorities = self.get_data_source_priority(data_type)
        return [s.get('source_name') for s in priorities]

    # ==================== 时间配置 ====================

    def get_critical_time(self, time_key: str) -> Optional[time]:
        """
        获取关键时间点

        Args:
            time_key: 时间键 ('time_1', 'time_2', 'time_3')

        Returns:
            time 对象
        """
        time_config = self._app_config.get('time_tools', {}).get('critical_time', {})
        time_info = time_config.get(time_key, {})
        time_str = time_info.get('time', '')

        if time_str:
            parts = time_str.split(':')
            if len(parts) >= 2:
                return time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
        return None

    def get_critical_time_str(self, time_key: str) -> str:
        """获取关键时间点字符串 (HH:MM 格式)"""
        time_config = self._app_config.get('time_tools', {}).get('critical_time', {})
        time_info = time_config.get(time_key, {})
        time_str = time_info.get('time', '')

        # 返回 HH:MM 格式
        if time_str:
            parts = time_str.split(':')
            return f"{parts[0]}:{parts[1]}"
        return ''

    # ==================== 指数映射 ====================

    def get_index_mapping(self, index_name: str, mapping_type: str = 'short') -> str:
        """
        获取指数映射名称

        Args:
            index_name: 指数中文名称 (如 '沪深300')
            mapping_type: 映射类型 ('short' 或 'monthly')

        Returns:
            映射后的名称
        """
        index_config = self._app_config.get('index_mapping', {})

        if mapping_type == 'short':
            mapping = index_config.get('short_names', {})
        elif mapping_type == 'monthly':
            mapping = index_config.get('monthly_names', {})
        else:
            mapping = {}

        return mapping.get(index_name, '')

    def get_all_index_mapping(self, mapping_type: str = 'short') -> Dict[str, str]:
        """获取所有指数映射"""
        index_config = self._app_config.get('index_mapping', {})

        if mapping_type == 'short':
            return index_config.get('short_names', {})
        elif mapping_type == 'monthly':
            return index_config.get('monthly_names', {})
        return {}

    def get_supported_indices(self) -> List[str]:
        """获取支持的指数列表"""
        return self._app_config.get('index_mapping', {}).get('supported_indices', [])

    # ==================== 因子配置 ====================

    def get_barra_factors(self) -> List[str]:
        """获取 Barra 因子列表"""
        return self._app_config.get('factors', {}).get('barra', [])

    def get_industry_factors(self) -> List[str]:
        """获取行业因子列表"""
        return self._app_config.get('factors', {}).get('industry', [])

    def get_all_factors(self) -> List[str]:
        """获取所有因子列表"""
        return self.get_barra_factors() + self.get_industry_factors()

    # ==================== 日期常量 ====================

    def get_fallback_date(self, date_type: str) -> str:
        """
        获取回退日期

        Args:
            date_type: 'factor', 'yg_factor'

        Returns:
            日期字符串
        """
        dates_config = self._app_config.get('dates', {})

        if date_type == 'factor':
            return dates_config.get('factor_fallback_start', '2023-06-01')
        elif date_type == 'yg_factor':
            return dates_config.get('yg_factor_fallback_start', '2024-07-05')
        elif date_type == 'jy_old_cutoff':
            return dates_config.get('jy_old_data_cutoff', '20200531')
        return ''

    # ==================== 数据库配置 ====================

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库连接配置"""
        return self._db_config.get('database', {})

    def get_database_url(self) -> str:
        """获取 SQLAlchemy 数据库连接 URL"""
        db = self.get_database_config()
        if not db:
            return ''

        host = db.get('host', 'localhost')
        port = db.get('port', 3306)
        database = db.get('database', '')
        user = db.get('user', '')
        password = db.get('password', '')
        charset = db.get('charset', 'utf8mb4')

        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"

    def get_connection_pool_config(self) -> Dict[str, Any]:
        """获取连接池配置"""
        return self._db_config.get('connection_pool', {})

    # ==================== 数据表配置 ====================

    def get_table_config(self, table_name: str) -> Dict[str, Any]:
        """获取指定数据表的配置"""
        return self._tables_config.get(table_name, {})

    def get_all_table_names(self) -> List[str]:
        """获取所有配置的数据表名称"""
        return list(self._tables_config.keys())

    # ==================== 日志配置 ====================

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self._app_config.get('logging', {})

    # ==================== 批量写入配置 ====================

    def get_batch_config(self) -> Dict[str, Any]:
        """获取批量写入配置"""
        return self._app_config.get('database_batch', {})

    def get_chunk_size(self, table_name: str = None) -> int:
        """获取批量写入大小"""
        if table_name:
            table_config = self.get_table_config(table_name)
            if 'chunk_size' in table_config:
                return table_config['chunk_size']

        return self._app_config.get('database_batch', {}).get('default_chunk_size', 20000)

    def get_workers(self, table_name: str = None) -> int:
        """获取并行工作线程数"""
        if table_name:
            table_config = self.get_table_config(table_name)
            if 'workers' in table_config:
                return table_config['workers']

        return self._app_config.get('database_batch', {}).get('default_workers', 4)

    # ==================== 配置重载 ====================

    def reload(self) -> None:
        """重新加载所有配置"""
        self._load_all_configs()

    def __repr__(self) -> str:
        return f"UnifiedConfig(config_dir={self._config_dir})"


# 单例实例
config = UnifiedConfig()


# ==================== 便捷函数 ====================

def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return config.get(key, default)


def get_path(path_key: str) -> str:
    """获取路径的便捷函数"""
    return config.get_path(path_key)


def get_database_url() -> str:
    """获取数据库 URL 的便捷函数"""
    return config.get_database_url()
