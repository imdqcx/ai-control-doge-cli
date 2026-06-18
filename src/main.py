"""
AI Doge Remote - 主入口
初始化所有模块并启动服务
"""

import sys
import signal
import threading
import time
from pathlib import Path

from .config import ConfigManager
from .server import APIServer
from .capture import ScreenCapture
from .input_sim import InputSimulator
from .tray import SystemTray
from .settings_ui import SettingsUI
from .logger import setup_logging

# 全局变量
config_manager: ConfigManager = None
api_server: APIServer = None
system_tray: SystemTray = None
settings_ui: SettingsUI = None
start_time: float = 0


def signal_handler(signum, frame):
    """信号处理器，用于优雅退出"""
    print("\n正在退出...")
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
    global config_manager, api_server, system_tray, settings_ui, start_time
    
    # 设置日志
    setup_logging()
    
    # 记录启动时间
    start_time = time.time()
    
    # 初始化配置管理器
    config_path = Path.home() / ".aidogeremote" / "config.json"
    config_manager = ConfigManager(config_path)
    config = config_manager.load()
    
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
    system_tray.update_status("运行中", config.get("server", {}).get("port", 8765))
    
    print(f"AI Doge Remote 已启动")
    print(f"API地址: http://localhost:{config.get('server', {}).get('port', 8765)}")
    print(f"API文档: http://localhost:{config.get('server', {}).get('port', 8765)}/docs")
    
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