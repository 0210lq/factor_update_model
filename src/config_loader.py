# -*- coding: utf-8 -*-
"""
配置加载器模块

提供单例模式的 ConfigLoader 类，支持:
- 向上查找 config/config.yaml
- 嵌套键访问 (如 database.host)
- 环境变量优先于配置文件
"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional, Dict


class ConfigLoader:
    """
    配置加载器 - 单例模式

    使用方法:
        config = ConfigLoader()
        db_host = config.get('database.host')
        db_port = config.get('database.port', default=3306)
    """

    _instance = None
    _config: Dict[str, Any] = {}
    _config_path: Optional[Path] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _find_config_dir(self, start_path: Optional[Path] = None, max_levels: int = 10) -> Optional[Path]:
        """
        向上查找 config 目录

        Args:
            start_path: 起始路径，默认为当前文件所在目录
            max_levels: 最大向上查找层数

        Returns:
            config 目录路径，未找到则返回 None
        """
        if start_path is None:
            start_path = Path(__file__).resolve().parent

        current = start_path
        for _ in range(max_levels):
            config_dir = current / 'config'
            if config_dir.is_dir():
                return config_dir

            parent = current.parent
            if parent == current:  # 已到根目录
                break
            current = parent

        return None

    def _load_config(self) -> None:
        """加载配置文件"""
        config_dir = self._find_config_dir()

        if config_dir is None:
            # 尝试从项目根目录查找
            project_root = Path(__file__).resolve().parent.parent
            config_dir = project_root / 'config'

        if not config_dir or not config_dir.exists():
            print(f"警告: 未找到 config 目录")
            return

        # 尝试加载 config.yaml
        config_file = config_dir / 'config.yaml'
        if config_file.exists():
            self._config_path = config_file
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"警告: 加载配置文件失败: {e}")
                self._config = {}
        else:
            # 尝试加载 config.yaml.example 作为后备
            example_file = config_dir / 'config.yaml.example'
            if example_file.exists():
                self._config_path = example_file
                try:
                    with open(example_file, 'r', encoding='utf-8') as f:
                        self._config = yaml.safe_load(f) or {}
                    print(f"警告: 使用示例配置文件 {example_file}")
                except Exception as e:
                    print(f"警告: 加载示例配置文件失败: {e}")
                    self._config = {}

    def get(self, key: str, default: Any = None, env_prefix: str = 'FACTOR_UPDATE_') -> Any:
        """
        获取配置值，支持嵌套键访问

        环境变量优先级高于配置文件。
        环境变量命名规则: {env_prefix}{KEY} (大写，点号替换为下划线)
        例如: database.host -> FACTOR_UPDATE_DATABASE_HOST

        Args:
            key: 配置键，支持点号分隔的嵌套键 (如 'database.host')
            default: 默认值
            env_prefix: 环境变量前缀

        Returns:
            配置值
        """
        # 1. 优先检查环境变量
        env_key = f"{env_prefix}{key.upper().replace('.', '_')}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            # 尝试转换类型
            if env_value.lower() in ('true', 'false'):
                return env_value.lower() == 'true'
            try:
                return int(env_value)
            except ValueError:
                try:
                    return float(env_value)
                except ValueError:
                    return env_value

        # 2. 从配置文件获取
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value if value is not None else default

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()

    def get_config_path(self) -> Optional[Path]:
        """获取配置文件路径"""
        return self._config_path

    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()

    def __repr__(self) -> str:
        return f"ConfigLoader(config_path={self._config_path})"


# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置值的便捷函数

    Args:
        key: 配置键
        default: 默认值

    Returns:
        配置值
    """
    return ConfigLoader().get(key, default)


def get_project_root() -> Path:
    """
    获取项目根目录

    Returns:
        项目根目录路径
    """
    return Path(__file__).resolve().parent.parent


def get_config_dir() -> Path:
    """
    获取配置目录路径

    Returns:
        配置目录路径
    """
    return get_project_root() / 'config'
