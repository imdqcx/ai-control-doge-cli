"""
AI Doge Remote - 主入口
初始化所有模块并启动服务
"""

import sys
import os

# 打包后支持：将src目录加入sys.path
if getattr(sys, 'frozen', False):
    # PyInstaller打包后的路径
    base_dir = os.path.dirname(sys.executable)
    src_dir = os.path.join(base_dir, 'src')
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)
    else:
        sys.path.insert(0, base_dir)
else:
    # 开发模式：将当前目录的父目录加入path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import signal
import threading
import time
from pathlib import Path

from src.config import ConfigManager, get_config_path
from src.server import APIServer
from src.capture import ScreenCapture
from src.input_sim import InputSimulator
from src.tray import SystemTray
from src.settings_ui import SettingsUI
from src.logger import setup_logging, get_logger

# 全局变量
config_manager: ConfigManager = None
api_server: APIServer = None
system_tray: SystemTray = None
settings_ui: SettingsUI = None
start_time: float = 0

logger = None


def signal_handler(signum, frame):
    """信号处理器，用于优雅退出"""
    if logger:
        logger.info("收到退出信号，正在退出...")
    cleanup()
    sys.exit(0)


def cleanup():
    """清理资源"""
    global api_server, system_tray
    
    if api_server:
        api_server.stop()
    
    if system_tray:
        system_tray.stop()


def on_settings_save(config: dict):
    """设置保存回调"""
    global config_manager, api_server
    
    # 保存配置
    config_manager.save(config)
    
    # 重启服务器（如果需要）
    if api_server:
        api_server.stop()
    
    # 重新创建服务器
    api_server = APIServer(config)
    api_server.start()


def on_exit():
    """退出回调"""
    cleanup()
    sys.exit(0)


def main():
    """主函数"""
    global config_manager, api_server, system_tray, settings_ui, start_time, logger
    
    # 设置日志
    setup_logging()
    logger = get_logger(__name__)
    
    # 记录启动时间
    start_time = time.time()
    
    # 初始化配置管理器（使用PRD规范的路径）
    config_path = get_config_path()
    logger.info(f"配置文件路径: {config_path}")
    
    config_manager = ConfigManager(config_path)
    config = config_manager.load()
    
    # 获取服务器配置
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8765)
    
    # 初始化API服务器
    api_server = APIServer(config)
    
    # 初始化系统托盘
    system_tray = SystemTray(
        config=config,
        on_settings=lambda: show_settings(config),
        on_exit=on_exit
    )
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动系统托盘
    system_tray.start()
    
    # 启动API服务器（在新线程中）
    server_thread = threading.Thread(target=api_server.start, daemon=True)
    server_thread.start()
    
    # 更新托盘状态
    system_tray.update_status("运行中", port)
    
    logger.info("=" * 50)
    logger.info("AI Doge Remote 已启动")
    logger.info(f"API地址: http://{host}:{port}")
    logger.info(f"API文档: http://localhost:{port}/docs")
    logger.info("=" * 50)
    
    print(f"\nAI Doge Remote 已启动")
    print(f"API地址: http://{host}:{port}")
    print(f"API文档: http://localhost:{port}/docs")
    print(f"配置文件: {config_path}")
    print(f"\n程序将在系统托盘运行，右键图标可打开设置或退出\n")
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


def show_settings(config: dict):
    """显示设置界面"""
    global settings_ui
    
    if settings_ui is None:
        settings_ui = SettingsUI(
            config=config,
            on_save=on_settings_save,
            on_cancel=lambda: settings_ui.hide()
        )
    
    settings_ui.show()


if __name__ == "__main__":
    main()
