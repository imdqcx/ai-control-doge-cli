"""输入模拟模块

负责鼠标移动、点击、滚轮、拖拽和键盘输入。"""

import time
from typing import List, Optional, Tuple
import pyautogui


class InputSimulator:
    """输入模拟器"""
    
    def __init__(self):
        """初始化输入模拟器"""
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        # 按键映射表
        self.key_map = {
            "enter": "enter",
            "tab": "tab",
            "escape": "escape",
            "backspace": "backspace",
            "delete": "delete",
            "space": "space",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "home": "home",
            "end": "end",
            "pageup": "pageup",
            "pagedown": "pagedown",
            "insert": "insert",
            "capslock": "capslock",
            "numlock": "numlock",
            "scrolllock": "scrolllock",
            "f1": "f1",
            "f2": "f2",
            "f3": "f3",
            "f4": "f4",
            "f5": "f5",
            "f6": "f6",
            "f7": "f7",
            "f8": "f8",
            "f9": "f9",
            "f10": "f10",
            "f11": "f11",
            "f12": "f12",
            # 符号键
            "-": "-",
            "=": "=",
            "[": "[",
            "]": "]",
            "\\": "\\",
            ";": ";",
            "'": "'",
            ",": ",",
            ".": ".",
            "/": "/",
            "`": "`",
        }
    
    def mouse_move(self, x: int, y: int, duration: float = 0) -> Tuple[int, int]:
        """
        移动鼠标
        
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动耗时（秒）
        
        Returns:
            实际鼠标位置
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return (x, y)
        except Exception as e:
            raise RuntimeError(f"鼠标移动失败: {e}")
    
    def mouse_click(self, 
                   x: int, 
                   y: int, 
                   button: str = "left", 
                   clicks: int = 1, 
                   interval: float = 0.1) -> dict:
        """
        鼠标点击
        
        Args:
            x: 点击位置X坐标
            y: 点击位置Y坐标
            button: 按键 ('left', 'right', 'middle')
            clicks: 点击次数
            interval: 多次点击间隔（秒）
        
        Returns:
            操作结果
        """
        try:
            pyautogui.click(x, y, clicks=clicks, button=button, interval=interval)
            return {
                "success": True,
                "action": "click",
                "button": button,
                "clicks": clicks,
                "position": {"x": x, "y": y}
            }
        except Exception as e:
            raise RuntimeError(f"鼠标点击失败: {e}")
    
    def mouse_scroll(self, 
                    x: int, 
                    y: int, 
                    dx: int, 
                    dy: int) -> dict:
        """
        鼠标滚轮
        
        Args:
            x: 滚轮位置X坐标
            y: 滚轮位置Y坐标
            dx: 水平滚动量
            dy: 垂直滚动量
        
        Returns:
            操作结果
        """
        try:
            # 先移动鼠标到指定位置
            pyautogui.moveTo(x, y)
            # 执行滚动
            pyautogui.scroll(dy, x, y)
            if dx != 0:
                pyautogui.hscroll(dx, x, y)
            
            return {
                "success": True,
                "action": "scroll",
                "delta": {"dx": dx, "dy": dy}
            }
        except Exception as e:
            raise RuntimeError(f"鼠标滚轮失败: {e}")
    
    def mouse_drag(self, 
                  from_x: int, 
                  from_y: int, 
                  to_x: int, 
                  to_y: int, 
                  button: str = "left", 
                  duration: float = 0.5) -> dict:
        """
        鼠标拖拽
        
        Args:
            from_x: 起点X坐标
            from_y: 起点Y坐标
            to_x: 终点X坐标
            to_y: 终点Y坐标
            button: 按键
            duration: 拖拽耗时（秒）
        
        Returns:
            操作结果
        """
        try:
            pyautogui.moveTo(from_x, from_y)
            pyautogui.drag(to_x - from_x, to_y - from_y, duration=duration, button=button)
            return {
                "success": True,
                "action": "drag",
                "from": {"x": from_x, "y": from_y},
                "to": {"x": to_x, "y": to_y}
            }
        except Exception as e:
            raise RuntimeError(f"鼠标拖拽失败: {e}")
    
    def keyboard_type(self, text: str, interval: float = 0.02) -> dict:
        """
        键盘输入文本
        
        Args:
            text: 要输入的文本
            interval: 每个字符间隔（秒）
        
        Returns:
            操作结果
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            return {
                "success": True,
                "action": "type",
                "length": len(text)
            }
        except Exception as e:
            raise RuntimeError(f"键盘输入失败: {e}")
    
    def keyboard_press(self, key: str, modifiers: List[str] = []) -> dict:
        """
        按下单个键
        
        Args:
            key: 按键名
            modifiers: 修饰键列表
        
        Returns:
            操作结果
        """
        try:
            # 映射按键名
            mapped_key = self.key_map.get(key.lower(), key)
            
            # 按下修饰键
            for modifier in modifiers:
                mapped_modifier = self.key_map.get(modifier.lower(), modifier)
                pyautogui.keyDown(mapped_modifier)
            
            # 按下主键
            pyautogui.keyDown(mapped_key)
            pyautogui.keyUp(mapped_key)
            
            # 释放修饰键（逆序）
            for modifier in reversed(modifiers):
                mapped_modifier = self.key_map.get(modifier.lower(), modifier)
                pyautogui.keyUp(mapped_modifier)
            
            return {
                "success": True,
                "action": "press",
                "key": key,
                "modifiers": modifiers
            }
        except Exception as e:
            raise RuntimeError(f"按键失败: {e}")
    
    def keyboard_hotkey(self, keys: List[str]) -> dict:
        """
        组合快捷键
        
        Args:
            keys: 按键列表
        
        Returns:
            操作结果
        """
        try:
            # 映射所有按键
            mapped_keys = [self.key_map.get(k.lower(), k) for k in keys]
            
            # 执行组合键
            pyautogui.hotkey(*mapped_keys)
            
            return {
                "success": True,
                "action": "hotkey",
                "keys": keys
            }
        except Exception as e:
            raise RuntimeError(f"组合快捷键失败: {e}")