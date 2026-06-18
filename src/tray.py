"""
系统托盘模块
负责托盘图标、右键菜单、状态管理
"""

import sys
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
        
        Args:
            config: 配置字典
            on_settings: 设置回调函数
            on_exit: 退出回调函数
            icon_path: 图标文件路径
        """
        self.config = config
        self.on_settings = on_settings
        self.on_exit = on_exit
        
        self.icon: Optional[pystray.Icon] = None
        self.status = "启动中"
        self.port = config.get("server", {}).get("port", 8765)
        self.host = config.get("server", {}).get("host", "0.0.0.0")
        
        # 加载图标
        self.icon_image = self._load_icon(icon_path)
    
    def _load_icon(self, icon_path: str = None) -> Image.Image:
        """
        加载图标文件
        
        Args:
            icon_path: 图标文件路径
        
        Returns:
            PIL图像对象
        """
        # 尝试从指定路径加载
        if icon_path:
            path = Path(icon_path)
            if path.exists():
                try:
                    return Image.open(path)
                except Exception:
                    pass
        
        # 尝试从assets目录加载
        # 支持多种启动方式：直接运行、打包后运行
        search_paths = [
            Path(__file__).parent.parent / "assets" / "doge.ico",
            Path(__file__).parent / "assets" / "doge.ico",
            Path("assets") / "doge.ico",
            Path(sys.executable).parent / "assets" / "doge.ico" if getattr(sys, 'frozen', False) else None,
        ]
        
        for path in search_paths:
            if path and path.exists():
                try:
                    return Image.open(path)
                except Exception:
                    continue
        
        # 回退：生成简单的Doge图标
        return self._create_default_icon()
    
    def _create_default_icon(self) -> Image.Image:
        """生成默认的Doge图标"""
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(image)
            
            # 背景圆形
            draw.ellipse([4, 4, width-4, height-4], fill=(255, 200, 100, 255))
            
            # 耳朵
            draw.polygon([(15, 20), (25, 5), (35, 20)], fill=(200, 150, 50, 255))
            draw.polygon([(width-35, 20), (width-25, 5), (width-15, 20)], fill=(200, 150, 50, 255))
            
            # 眼睛
            draw.ellipse([20, 25, 30, 35], fill=(50, 50, 50, 255))
            draw.ellipse([width-30, 25, width-20, 35], fill=(50, 50, 50, 255))
            
            # 鼻子
            draw.ellipse([width//2-5, 35, width//2+5, 45], fill=(50, 50, 50, 255))
            
            # 嘴巴
            draw.arc([width//2-10, 40, width//2+10, 55], 0, 180, fill=(50, 50, 50, 255), width=2)
        except Exception:
            pass
        
        return image
    
    def _get_local_ip(self) -> str:
        """获取本机IP地址"""
        try:
            # 创建一个UDP socket来获取本机IP
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
            pystray.MenuItem(
                f"🐕 AI Doge Remote",
                None,
                enabled=False
            ),
            pystray.MenuItem(
                f"📊 状态: {self.status} · 端口 {self.port}",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "⚙️  设置...",
                self._on_settings_click
            ),
            pystray.MenuItem(
                "📋 复制 API 地址",
                self._on_copy_address
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🚪 退出",
                self._on_exit_click
            )
        )
    
    def _on_settings_click(self, icon=None, item=None):
        """设置菜单点击"""
        if self.on_settings:
            # 在新线程中调用，避免阻塞托盘
            threading.Thread(target=self.on_settings, daemon=True).start()
    
    def _on_copy_address(self, icon, item):
        """复制API地址"""
        try:
            import pyperclip
            local_ip = self._get_local_ip()
            address = f"http://{local_ip}:{self.port}"
            pyperclip.copy(address)
            self.show_notification("已复制", f"API地址 {address} 已复制到剪贴板")
        except Exception as e:
            self.show_notification("复制失败", f"无法复制到剪贴板: {e}")
    
    def _on_exit_click(self, icon, item):
        """退出菜单点击"""
        if self.on_exit:
            self.on_exit()
    
    def start(self):
        """启动系统托盘"""
        def run_icon():
            self.icon = pystray.Icon(
                "AI Doge Remote",
                self.icon_image,
                "AI Doge Remote",
                self._create_menu()
            )
            # 设置左键点击行为：打开设置
            self.icon.run(setup=self._setup_icon)
        
        # 在新线程中运行
        self.thread = threading.Thread(target=run_icon, daemon=True)
        self.thread.start()
    
    def _setup_icon(self, icon):
        """图标启动后的设置"""
        # pystray不直接支持左键点击，但我们可以监听
        # 实际上pystray的默认行为就是左键点击弹出菜单
        pass
    
    def stop(self):
        """停止系统托盘"""
        if self.icon:
            self.icon.stop()
    
    def update_status(self, status: str, port: int):
        """
        更新状态
        
        Args:
            status: 状态文本
            port: 端口号
        """
        self.status = status
        self.port = port
        
        # 更新菜单（如果图标已创建）
        if self.icon:
            try:
                self.icon.menu = self._create_menu()
            except Exception:
                pass
    
    def show_notification(self, title: str, message: str):
        """
        显示系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
        """
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception:
                pass
