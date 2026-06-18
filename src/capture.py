"""
屏幕截图模块
负责屏幕捕获、图像处理、格式转换
"""

import io
import sys
import time
import ctypes
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw
import mss
import mss.tools


class ScreenCapture:
    """屏幕截图引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化屏幕截图引擎
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.sct = mss.MSS()
        self._last_capture_time = 0
        self._last_capture_result = None
        
        # 初始化Windows DPI感知
        self._init_dpi_awareness()
        
        # 缓存屏幕信息
        self._screen_info_cache = None
        self._screen_info_cache_time = 0
    
    def _init_dpi_awareness(self):
        """初始化Windows DPI感知，确保获取正确的屏幕坐标"""
        if sys.platform == "win32":
            try:
                # 设置为Per-Monitor DPI Aware
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                try:
                    # 回退到System DPI Aware
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
    
    def _get_dpi_info(self) -> Tuple[float, int]:
        """
        获取系统DPI信息
        
        Returns:
            (scale_factor, dpi)
        """
        if sys.platform != "win32":
            return (1.0, 96)
        
        try:
            # 获取主显示器DPI
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            scale_factor = dpi / 96.0
            return (round(scale_factor, 2), dpi)
        except Exception:
            return (1.0, 96)
    
    def capture(self, 
                format: str = None, 
                quality: int = None, 
                scale: float = 1.0, 
                region: Optional[str] = None, 
                cursor: bool = False) -> Tuple[bytes, Dict[str, Any]]:
        """
        捕获屏幕截图
        
        Args:
            format: 图像格式 ('png' 或 'jpeg')
            quality: JPEG质量 (1-100)
            scale: 缩放比例 (0.1-1.0)
            region: 截取区域 (格式: 'x,y,width,height')
            cursor: 是否绘制鼠标指针
        
        Returns:
            (图像二进制数据, 元数据字典)
        """
        # 使用配置默认值
        if format is None:
            format = self.config.get("capture", {}).get("format", "jpeg")
        if quality is None:
            quality = self.config.get("capture", {}).get("quality", 80)
        
        # 获取屏幕信息
        monitor = self.sct.monitors[1]  # 主显示器
        screen_width = monitor["width"]
        screen_height = monitor["height"]
        
        # 获取鼠标位置（屏幕坐标）
        mouse_x, mouse_y = self.get_mouse_position()
        
        # 解析区域
        if region:
            try:
                x, y, w, h = map(int, region.split(","))
                capture_region = {"left": x, "top": y, "width": w, "height": h}
            except ValueError:
                capture_region = monitor
        else:
            capture_region = monitor
        
        # 捕获屏幕
        try:
            screenshot = self.sct.grab(capture_region)
        except Exception as e:
            raise RuntimeError(f"屏幕截图失败: {e}")
        
        # 转换为PIL图像
        image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # 计算鼠标在图像中的相对位置
        rel_x = mouse_x - capture_region.get("left", 0)
        rel_y = mouse_y - capture_region.get("top", 0)
        
        # 缩放图像
        total_scale = 1.0
        if scale < 1.0:
            total_scale *= scale
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 绘制鼠标指针（使用缩放后的坐标）
        if cursor:
            scaled_x = int(rel_x * total_scale)
            scaled_y = int(rel_y * total_scale)
            image = self._draw_cursor(image, scaled_x, scaled_y)
        
        # 转换为字节
        image_bytes = self._image_to_bytes(image, format, quality)
        
        # 准备元数据
        metadata = {
            "screen_width": screen_width,
            "screen_height": screen_height,
            "image_width": image.width,
            "image_height": image.height,
            "cursor_x": mouse_x,
            "cursor_y": mouse_y,
            "format": format,
            "timestamp": time.time()
        }
        
        return image_bytes, metadata
    
    def get_screen_info(self) -> Dict[str, Any]:
        """
        获取屏幕信息
        
        Returns:
            屏幕信息字典
        """
        # 使用缓存（5秒有效期）
        now = time.time()
        if self._screen_info_cache and (now - self._screen_info_cache_time) < 5:
            return self._screen_info_cache
        
        monitor = self.sct.monitors[1]
        scale_factor, dpi = self._get_dpi_info()
        mouse_pos = self.get_mouse_position()
        
        info = {
            "width": monitor["width"],
            "height": monitor["height"],
            "scale_factor": scale_factor,
            "dpi": dpi,
            "mouse_position": {"x": mouse_pos[0], "y": mouse_pos[1]}
        }
        
        self._screen_info_cache = info
        self._screen_info_cache_time = now
        
        return info
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        获取当前鼠标位置
        
        Returns:
            (x, y) 坐标
        """
        if sys.platform == "win32":
            try:
                from ctypes import wintypes
                point = wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
                return (point.x, point.y)
            except Exception:
                pass
        
        # 回退到pyautogui
        try:
            import pyautogui
            pos = pyautogui.position()
            return (pos[0], pos[1])
        except Exception:
            return (0, 0)
    
    def _draw_cursor(self, image: Image.Image, cursor_x: int, cursor_y: int) -> Image.Image:
        """
        在图像上绘制鼠标指针（标准Windows白色箭头，放大版）
        
        Args:
            image: 原始图像
            cursor_x: 鼠标在图像中的X坐标
            cursor_y: 鼠标在图像中的Y坐标
        
        Returns:
            绘制了鼠标指针的图像
        """
        # 确保坐标在图像范围内
        if cursor_x < 0 or cursor_y < 0 or cursor_x >= image.width or cursor_y >= image.height:
            return image
        
        draw = ImageDraw.Draw(image)
        
        # 根据图像大小动态计算光标缩放比例
        # 小截图用2倍，大截图用1倍
        s = 2 if min(image.width, image.height) < 1000 else 1
        
        # 标准Windows鼠标指针形状（白色箭头+黑色边框）
        # 外轮廓（黑色）
        outer = [
            (cursor_x, cursor_y),
            (cursor_x + s, cursor_y + s),
            (cursor_x + s, cursor_y + 13*s),
            (cursor_x + 4*s, cursor_y + 10*s),
            (cursor_x + 7*s, cursor_y + 15*s),
            (cursor_x + 9*s, cursor_y + 14*s),
            (cursor_x + 6*s, cursor_y + 9*s),
            (cursor_x + 10*s, cursor_y + 9*s),
        ]
        draw.polygon(outer, fill="black")
        
        # 内部填充（白色）
        inner = [
            (cursor_x + s, cursor_y + s),
            (cursor_x + s, cursor_y + 12*s),
            (cursor_x + 4*s, cursor_y + 9*s),
            (cursor_x + 6*s, cursor_y + 13*s),
            (cursor_x + 8*s, cursor_y + 12*s),
            (cursor_x + 5*s, cursor_y + 8*s),
            (cursor_x + 9*s, cursor_y + 8*s),
        ]
        draw.polygon(inner, fill="white")
        
        return image
    
    def _image_to_bytes(self, 
                       image: Image.Image, 
                       format: str, 
                       quality: int) -> bytes:
        """
        将图像转换为字节
        
        Args:
            image: PIL图像
            format: 图像格式
            quality: JPEG质量
        
        Returns:
            图像字节数据
        """
        buffer = io.BytesIO()
        
        if format.lower() == "png":
            image.save(buffer, format="PNG", optimize=True)
        elif format.lower() == "jpeg":
            # JPEG不支持RGBA，转换为RGB
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
        else:
            raise ValueError(f"不支持的图像格式: {format}")
        
        return buffer.getvalue()
    
    def __del__(self):
        """析构函数，释放资源"""
        if hasattr(self, 'sct'):
            self.sct.close()
