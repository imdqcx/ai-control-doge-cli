"""
屏幕截图模块
负责屏幕捕获、图像处理、格式转换
"""

import io
import time
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
        self.sct = mss.mss()
        self._last_capture_time = 0
        self._last_capture_result = None
    
    def capture(self, 
                format: str = None, 
                quality: int = None, 
                scale: float = 1.0, 
                region: Optional[str] = None, 
                cursor: bool = True) -> Tuple[bytes, Dict[str, Any]]:
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
        
        # 绘制鼠标指针
        if cursor:
            image = self._draw_cursor(image)
        
        # 缩放图像
        if scale < 1.0:
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 转换为字节
        image_bytes = self._image_to_bytes(image, format, quality)
        
        # 准备元数据
        metadata = {
            "screen_width": screen_width,
            "screen_height": screen_height,
            "image_width": image.width,
            "image_height": image.height,
            "cursor_x": 0,  # TODO: 获取实际鼠标位置
            "cursor_y": 0,
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
        monitor = self.sct.monitors[1]
        return {
            "width": monitor["width"],
            "height": monitor["height"],
            "scale_factor": 1.0,  # TODO: 获取实际缩放比例
            "dpi": 96,  # TODO: 获取实际DPI
            "mouse_position": self.get_mouse_position()
        }
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        获取鼠标位置
        
        Returns:
            (x, y) 坐标
        """
        # TODO: 实现鼠标位置获取
        return (0, 0)
    
    def _draw_cursor(self, image: Image.Image) -> Image.Image:
        """
        在图像上绘制鼠标指针
        
        Args:
            image: 原始图像
        
        Returns:
            绘制了鼠标指针的图像
        """
        # TODO: 实现鼠标指针绘制
        # 这里需要获取鼠标位置和图标，然后绘制到图像上
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
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
        else:
            raise ValueError(f"不支持的图像格式: {format}")
        
        return buffer.getvalue()
    
    def __del__(self):
        """析构函数，释放资源"""
        if hasattr(self, 'sct'):
            self.sct.close()