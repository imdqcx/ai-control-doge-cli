"""
剪贴板管理模块
负责读写系统剪贴板
"""

import sys
from typing import Tuple


class ClipboardManager:
    """剪贴板管理器"""
    
    def __init__(self):
        """初始化剪贴板管理器"""
        self._check_platform()
    
    def _check_platform(self):
        """检查平台并导入相应的剪贴板库"""
        if sys.platform == "win32":
            try:
                import win32clipboard
                self.win32clipboard = win32clipboard
                self.platform = "windows"
            except ImportError:
                # 回退到pyperclip
                try:
                    import pyperclip
                    self.pyperclip = pyperclip
                    self.platform = "pyperclip"
                except ImportError:
                    self.platform = "none"
        else:
            # 非Windows平台使用pyperclip
            try:
                import pyperclip
                self.pyperclip = pyperclip
                self.platform = "pyperclip"
            except ImportError:
                self.platform = "none"
    
    def get_content(self) -> Tuple[str, bool]:
        """
        获取剪贴板内容
        
        Returns:
            (文本内容, 是否有图像)
        """
        if self.platform == "windows":
            return self._get_content_windows()
        elif self.platform == "pyperclip":
            return self._get_content_pyperclip()
        else:
            return ("", False)
    
    def set_content(self, content: str):
        """
        设置剪贴板内容
        
        Args:
            content: 要设置的文本内容
        """
        if self.platform == "windows":
            self._set_content_windows(content)
        elif self.platform == "pyperclip":
            self._set_content_pyperclip(content)
        else:
            raise RuntimeError("剪贴板功能不可用")
    
    def has_image(self) -> bool:
        """
        检查剪贴板是否有图像
        
        Returns:
            是否有图像
        """
        if self.platform == "windows":
            return self._has_image_windows()
        return False
    
    def _get_content_windows(self) -> Tuple[str, bool]:
        """Windows平台获取剪贴板内容"""
        try:
            self.win32clipboard.OpenClipboard()
            
            # 检查是否有文本
            if self.win32clipboard.IsClipboardFormatAvailable(self.win32clipboard.CF_TEXT):
                data = self.win32clipboard.GetClipboardData(self.win32clipboard.CF_TEXT)
                self.win32clipboard.CloseClipboard()
                return (data.decode('utf-8', errors='replace'), False)
            
            # 检查是否有Unicode文本
            if self.win32clipboard.IsClipboardFormatAvailable(self.win32clipboard.CF_UNICODETEXT):
                data = self.win32clipboard.GetClipboardData(self.win32clipboard.CF_UNICODETEXT)
                self.win32clipboard.CloseClipboard()
                return (data, False)
            
            # 检查是否有图像
            has_image = self.win32clipboard.IsClipboardFormatAvailable(self.win32clipboard.CF_BITMAP)
            self.win32clipboard.CloseClipboard()
            
            return ("", has_image)
        except Exception as e:
            try:
                self.win32clipboard.CloseClipboard()
            except:
                pass
            raise RuntimeError(f"读取剪贴板失败: {e}")
    
    def _set_content_windows(self, content: str):
        """Windows平台设置剪贴板内容"""
        try:
            self.win32clipboard.OpenClipboard()
            self.win32clipboard.EmptyClipboard()
            self.win32clipboard.SetClipboardText(content, self.win32clipboard.CF_UNICODETEXT)
            self.win32clipboard.CloseClipboard()
        except Exception as e:
            try:
                self.win32clipboard.CloseClipboard()
            except:
                pass
            raise RuntimeError(f"设置剪贴板失败: {e}")
    
    def _has_image_windows(self) -> bool:
        """Windows平台检查剪贴板是否有图像"""
        try:
            self.win32clipboard.OpenClipboard()
            has_image = self.win32clipboard.IsClipboardFormatAvailable(self.win32clipboard.CF_BITMAP)
            self.win32clipboard.CloseClipboard()
            return has_image
        except Exception:
            try:
                self.win32clipboard.CloseClipboard()
            except:
                pass
            return False
    
    def _get_content_pyperclip(self) -> Tuple[str, bool]:
        """pyperclip获取剪贴板内容"""
        try:
            text = self.pyperclip.paste()
            return (text, False)
        except Exception as e:
            raise RuntimeError(f"读取剪贴板失败: {e}")
    
    def _set_content_pyperclip(self, content: str):
        """pyperclip设置剪贴板内容"""
        try:
            self.pyperclip.copy(content)
        except Exception as e:
            raise RuntimeError(f"设置剪贴板失败: {e}")