"""
系统托盘模块
负责托盘图标、右键菜单、状态管理
"""

import threading
from typing import Callable, Optional
import pystray
from PIL import Image, ImageDraw


class SystemTray:
    """系统托盘管理器"""
    
    def __init__(self, 
                 config: dict, 
                 on_settings: Callable, 
                 on_exit: Callable):
        """
        初始化系统托盘
        
        Args:
            config: 配置字典
            on_settings: 设置回调函数
            on_exit: 退出回调函数
        """
        self.config = config
        self.on_settings = on_settings
        self.on_exit = on_exit
        
        self.icon: Optional[pystray.Icon] = None
        self.status = "启动中"
        self.port = config.get("server", {}).get("port", 8765)
        
        # 创建图标
        self._create_icon()
    
    def _create_icon(self):
        """创建托盘图标"""
        # 创建简单的Dog图标（实际项目中应该加载ICO文件）
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制简单的狗头形状
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
        
        self.icon_image = image
    
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
    
    def _on_settings_click(self, icon, item):
        """设置菜单点击"""
        if self.on_settings:
            self.on_settings()
    
    def _on_copy_address(self, icon, item):
        """复制API地址"""
        import pyperclip
        address = f"http://localhost:{self.port}"
        pyperclip.copy(address)
        # 可以显示通知
        self.show_notification("已复制", f"API地址已复制到剪贴板")
    
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
            self.icon.run()
        
        # 在新线程中运行
        self.thread = threading.Thread(target=run_icon, daemon=True)
        self.thread.start()
    
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
            self.icon.menu = self._create_menu()
    
    def show_notification(self, title: str, message: str):
        """
        显示系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
        """
        if self.icon:
            self.icon.notify(message, title)