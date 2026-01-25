# -*- coding: utf-8 -*-
"""
日志设置模块

提供日志记录器的配置函数。
日志文件存储在项目根目录的 logs/ 目录下。
"""

import os
import logging
from datetime import datetime
from pathlib import Path


def get_project_root():
    """
    获取项目根目录

    当前文件位于 src/setup_logger/logger_setup.py
    需要向上 3 层获取项目根目录

    Returns:
        Path: 项目根目录路径
    """
    current_file = Path(__file__).resolve()
    # src/setup_logger/logger_setup.py -> src/setup_logger -> src -> project_root
    return current_file.parent.parent.parent


def setup_logger(logger_name):
    """
    设置日志记录器

    Args:
        logger_name (str): 日志记录器的名称，用于区分不同的处理模块

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建 logs 目录（在项目根目录下）
    project_root = get_project_root()
    log_dir = project_root / 'logs' / 'processing_log'
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志文件名
    current_date = datetime.now().strftime('%Y%m%d')
    log_file = log_dir / f'processingLogs_{current_date}.log'

    # 创建日志记录器
    logger = logging.getLogger(logger_name)

    # 如果 logger 已经有处理器，直接返回
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # 创建文件处理器
    file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s\n%(message)s\n' + '=' * 80)
    file_handler.setFormatter(formatter)

    # 添加处理器到记录器
    logger.addHandler(file_handler)

    return logger


def setup_logger2(logger_name):
    """
    设置数据检查日志记录器

    Args:
        logger_name (str): 日志记录器的名称，用于区分不同的处理模块

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建 logs 目录（在项目根目录下）
    project_root = get_project_root()
    log_dir = project_root / 'logs' / 'DataCheck_log'
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志文件名
    current_date = datetime.now().strftime('%Y%m%d')
    log_file = log_dir / f'DataCheckLog_{current_date}.log'

    # 创建日志记录器
    logger = logging.getLogger(logger_name)

    # 如果 logger 已经有处理器，直接返回
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # 创建文件处理器
    file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 创建格式化器 - 移除分隔线
    formatter = logging.Formatter('%(asctime)s - %(name)s\n%(message)s')
    file_handler.setFormatter(formatter)

    # 添加处理器到记录器
    logger.addHandler(file_handler)

    return logger
