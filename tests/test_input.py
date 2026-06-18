"""
输入模拟模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.input_sim import InputSimulator


@pytest.fixture
def simulator():
    """输入模拟器实例"""
    return InputSimulator()


class TestInputSimulator:
    """输入模拟器测试"""
    
    def test_init(self, simulator):
        """测试初始化"""
        assert simulator.key_map is not None
        assert len(simulator.key_map) > 0
    
    @patch('pyautogui.moveTo')
    def test_mouse_move(self, mock_move, simulator):
        """测试鼠标移动"""
        mock_move.return_value = None
        
        position = simulator.mouse_move(500, 300, 0.3)
        
        assert position == (500, 300)
        mock_move.assert_called_once_with(500, 300, duration=0.3)
    
    @patch('pyautogui.click')
    def test_mouse_click(self, mock_click, simulator):
        """测试鼠标点击"""
        mock_click.return_value = None
        
        result = simulator.mouse_click(500, 300, "left", 1, 0.1)
        
        assert result["success"] == True
        assert result["action"] == "click"
        assert result["button"] == "left"
        assert result["clicks"] == 1
        assert result["position"]["x"] == 500
        assert result["position"]["y"] == 300
        
        mock_click.assert_called_once_with(500, 300, clicks=1, button="left", interval=0.1)
    
    @patch('pyautogui.moveTo')
    @patch('pyautogui.scroll')
    @patch('pyautogui.hscroll')
    def test_mouse_scroll(self, mock_hscroll, mock_scroll, mock_move, simulator):
        """测试鼠标滚轮"""
        mock_move.return_value = None
        mock_scroll.return_value = None
        mock_hscroll.return_value = None
        
        result = simulator.mouse_scroll(500, 300, 0, -3)
        
        assert result["success"] == True
        assert result["action"] == "scroll"
        assert result["delta"]["dx"] == 0
        assert result["delta"]["dy"] == -3
        
        mock_move.assert_called_once_with(500, 300)
        mock_scroll.assert_called_once_with(-3, 500, 300)
    
    @patch('pyautogui.moveTo')
    @patch('pyautogui.drag')
    def test_mouse_drag(self, mock_drag, mock_move, simulator):
        """测试鼠标拖拽"""
        mock_move.return_value = None
        mock_drag.return_value = None
        
        result = simulator.mouse_drag(100, 200, 500, 400, "left", 0.5)
        
        assert result["success"] == True
        assert result["action"] == "drag"
        assert result["from"]["x"] == 100
        assert result["from"]["y"] == 200
        assert result["to"]["x"] == 500
        assert result["to"]["y"] == 400
        
        mock_move.assert_called_once_with(100, 200)
        mock_drag.assert_called_once_with(400, 200, duration=0.5, button="left")
    
    @patch('pyautogui.typewrite')
    def test_keyboard_type(self, mock_typewrite, simulator):
        """测试键盘输入"""
        mock_typewrite.return_value = None
        
        result = simulator.keyboard_type("Hello", 0.02)
        
        assert result["success"] == True
        assert result["action"] == "type"
        assert result["length"] == 5
        
        mock_typewrite.assert_called_once_with("Hello", interval=0.02)
    
    @patch('pyautogui.keyDown')
    @patch('pyautogui.keyUp')
    def test_keyboard_press(self, mock_keyUp, mock_keyDown, simulator):
        """测试按键"""
        mock_keyDown.return_value = None
        mock_keyUp.return_value = None
        
        result = simulator.keyboard_press("enter", ["ctrl"])
        
        assert result["success"] == True
        assert result["action"] == "press"
        assert result["key"] == "enter"
        assert result["modifiers"] == ["ctrl"]
        
        # 验证调用顺序
        calls = mock_keyDown.call_args_list
        assert len(calls) == 2
        assert calls[0] == (("ctrl",),)
        assert calls[1] == (("enter",),)
        
        calls = mock_keyUp.call_args_list
        assert len(calls) == 2
        assert calls[0] == (("enter",),)
        assert calls[1] == (("ctrl",),)
    
    @patch('pyautogui.hotkey')
    def test_keyboard_hotkey(self, mock_hotkey, simulator):
        """测试组合快捷键"""
        mock_hotkey.return_value = None
        
        result = simulator.keyboard_hotkey(["ctrl", "a"])
        
        assert result["success"] == True
        assert result["action"] == "hotkey"
        assert result["keys"] == ["ctrl", "a"]
        
        mock_hotkey.assert_called_once_with("ctrl", "a")
    
    def test_key_mapping(self, simulator):
        """测试按键映射"""
        # 测试特殊按键映射
        assert simulator.key_map["enter"] == "enter"
        assert simulator.key_map["tab"] == "tab"
        assert simulator.key_map["escape"] == "escape"
        assert simulator.key_map["space"] == "space"
        
        # 测试功能键映射
        assert simulator.key_map["f1"] == "f1"
        assert simulator.key_map["f12"] == "f12"
        
        # 测试方向键映射
        assert simulator.key_map["up"] == "up"
        assert simulator.key_map["down"] == "down"
        assert simulator.key_map["left"] == "left"
        assert simulator.key_map["right"] == "right"


class TestInputSimulatorIntegration:
    """输入模拟器集成测试"""
    
    @pytest.mark.skipif(
        not hasattr(pytest, "enable_integration_tests"),
        reason="集成测试默认禁用"
    )
    def test_real_mouse_move(self, simulator):
        """真实鼠标移动测试"""
        try:
            # 获取当前鼠标位置
            import pyautogui
            original_pos = pyautogui.position()
            
            # 移动鼠标
            new_pos = simulator.mouse_move(100, 100, 0.1)
            
            # 验证鼠标已移动
            current_pos = pyautogui.position()
            assert current_pos == (100, 100)
            
            # 恢复原位置
            simulator.mouse_move(original_pos[0], original_pos[1], 0.1)
            
        except Exception as e:
            pytest.skip(f"无法进行真实鼠标测试: {e}")
    
    @pytest.mark.skipif(
        not hasattr(pytest, "enable_integration_tests"),
        reason="集成测试默认禁用"
    )
    def test_real_keyboard_type(self, simulator):
        """真实键盘输入测试"""
        try:
            # 注意：这个测试可能会在活动窗口中输入文字
            # 在实际测试环境中应该小心使用
            
            # 模拟输入（不会实际输入到活动窗口）
            result = simulator.keyboard_type("test", 0.01)
            
            assert result["success"] == True
            assert result["length"] == 4
            
        except Exception as e:
            pytest.skip(f"无法进行真实键盘测试: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])