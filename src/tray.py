"""系统托盘模块

负责托盘图标、右键菜单和状态管理。"""

import sys
import os
import threading
import socket
from pathlib import Path
from typing import Callable, Optional
import pystray
from PIL import Image


class SystemTray:
    """系统托盘管理器"""
    
    def __init__(self, 
                 config: dict, 
                 on_settings: Callable, 
                 on_exit: Callable,
                 icon_path: str = None):
        """
        初始化系统托盘
        """
        self.config = config
        self.on_settings = on_settings
        self.on_exit = on_exit
        
        self.icon: Optional[pystray.Icon] = None
        self.status = "启动中"
        self.port = config.get("server", {}).get("port", 8765)
        self._running = False
        
        # 加载图标
        self.icon_image = self._load_icon(icon_path)
    
    def _load_icon(self, icon_path: str = None) -> Image.Image:
        """加载图标文件"""
        if icon_path and Path(icon_path).exists():
            try:
                return Image.open(icon_path)
            except Exception:
                pass
        
        # 确定assets目录位置
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent.parent
        
        # 尝试加载ico
        for name in ["doge.ico", "doge_256.png"]:
            path = base_dir / "assets" / name
            if path.exists():
                try:
                    return Image.open(path)
                except Exception:
                    continue
        
        # 回退：简单图标
        return self._create_fallback_icon()
    
    def _create_fallback_icon(self) -> Image.Image:
        """生成简单的回退图标"""
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.ellipse([2, 2, size-2, size-2], fill=(255, 180, 60, 255))
            draw.ellipse([14, 20, size-14, size-10], fill=(255, 255, 240, 255))
        except Exception:
            pass
        return img
    
    def _get_local_ip(self) -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
    
    def _create_menu(self) -> pystray.Menu:
        """创建右键菜单"""
        return pystray.Menu(
            pystray.MenuItem("AI Doge Remote", None, enabled=False),
            pystray.MenuItem(f"状态: {self.status} | 端口 {self.port}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("设置...", self._on_settings_click),
            pystray.MenuItem("复制 API 地址", self._on_copy_address),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self._on_exit_click)
        )
    
    def _on_settings_click(self, icon=None, item=None):
        """设置菜单点击"""
        try:
            if self.on_settings:
                # 在新线程中调用，避免阻塞托盘
                t = threading.Thread(target=self._safe_call_settings, daemon=True)
                t.start()
        except Exception as e:
            print(f"设置点击异常: {e}")
    
    def _safe_call_settings(self):
        """安全调用设置回调"""
        try:
            self.on_settings()
        except Exception as e:
            print(f"设置回调异常: {e}")
    
    def _on_copy_address(self, icon=None, item=None):
        """复制API地址"""
        try:
            import pyperclip
            address = f"http://{self._get_local_ip()}:{self.port}"
            pyperclip.copy(address)
            if self.icon:
                self.icon.notify("API地址已复制到剪贴板", "已复制")
        except Exception:
            pass
    
    def _on_exit_click(self, icon=None, item=None):
        """退出菜单点击"""
        try:
            self._running = False
            if self.on_exit:
                self.on_exit()
        except Exception:
            pass
    
    def start(self):
        """启动系统托盘"""
        self._running = True
        
        def run_icon():
            try:
                self.icon = pystray.Icon(
                    "AIDogeRemote",
                    self.icon_image,
                    "AI Doge Remote",
                    self._create_menu()
                )
                self.icon.run()
            except Exception as e:
                print(f"托盘图标异常: {e}")
        
        self.thread = threading.Thread(target=run_icon, daemon=True, name="SysTray")
        self.thread.start()
    
    def stop(self):
        """停止系统托盘"""
        self._running = False
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
    
    def update_status(self, status: str, port: int):
        """更新状态"""
        self.status = status
        self.port = port
        if self.icon:
            try:
                self.icon.menu = self._create_menu()
            except Exception:
                pass
    
    def show_notification(self, title: str, message: str):
        """显示系统通知"""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception:
                pass
