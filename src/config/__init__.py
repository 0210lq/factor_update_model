# -*- coding: utf-8 -*-
"""
配置模块

提供统一的配置访问接口。
"""

from .unified_config import (
    UnifiedConfig,
    config,
    get_config,
    get_path,
    get_database_url,
)

__all__ = [
    'UnifiedConfig',
    'config',
    'get_config',
    'get_path',
    'get_database_url',
]
