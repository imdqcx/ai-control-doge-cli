"""
日志配置模块
负责日志初始化和配置
"""

import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def get_log_dir() -> Path:
    """
    获取日志目录
    
    Returns:
        日志目录路径
    """
    # 使用 %APPDATA%\AIDogeRemote\logs
    appdata = os.environ.get("APPDATA")
    if appdata:
        log_dir = Path(appdata) / "AIDogeRemote" / "logs"
    else:
        log_dir = Path.home() / ".aidogeremote" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
    """
    # 创建日志目录
    if log_file is None:
        log_dir = get_log_dir()
        log_file = log_dir / "ai-doge-remote.log"
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（带轮转）
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"无法创建日志文件: {e}")
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    logging.info("日志系统初始化完成")


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)
