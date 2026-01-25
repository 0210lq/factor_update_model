import os
import logging
from datetime import datetime

def setup_logger(logger_name):
    """
    设置日志记录器
    
    Args:
        logger_name (str): 日志记录器的名称，用于区分不同的处理模块
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建logs目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'processing_log')
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志文件名
    current_date = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'processingLogs_{current_date}.log')
    
    # 创建日志记录器
    logger = logging.getLogger(logger_name)
    
    # 如果logger已经有处理器，直接返回
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s\n%(message)s\n' + '='*80)
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
    # 创建logs目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'DataCheck_log')
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志文件名
    current_date = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'DataCheckLog_{current_date}.log')
    
    # 创建日志记录器
    logger = logging.getLogger(logger_name)
    
    # 如果logger已经有处理器，直接返回
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建格式化器 - 移除分隔线
    formatter = logging.Formatter('%(asctime)s - %(name)s\n%(message)s')
    file_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    
    return logger 