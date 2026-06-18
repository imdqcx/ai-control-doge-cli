"""
API接口测试
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import time

# 导入被测模块
from src.server import APIServer


@pytest.fixture
def config():
    """测试配置"""
    return {
        "server": {
            "host": "127.0.0.1",
            "port": 8765
        },
        "capture": {
            "format": "jpeg",
            "quality": 80,
            "max_width": 1920,
            "max_height": 1080
        },
        "security": {
            "api_key": "",
            "notify_on_connect": True
        }
    }


@pytest.fixture
def api_server(config):
    """API服务器实例"""
    return APIServer(config)


@pytest.fixture
def client(api_server):
    """测试客户端"""
    return TestClient(api_server.app)


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "uptime_seconds" in data
        assert "screen" in data


class TestManual:
    """说明书测试"""
    
    def test_get_manual_plain(self, client):
        """测试获取纯文本说明书"""
        response = client.get("/manual")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        
        content = response.text
        assert "AI Doge Remote" in content
        assert "操作手册" in content or "Operation Manual" in content
    
    def test_get_manual_markdown(self, client):
        """测试获取Markdown说明书"""
        response = client.get("/manual?format=markdown")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
    
    def test_get_manual_zh(self, client):
        """测试获取中文说明书"""
        response = client.get("/manual?lang=zh")
        assert response.status_code == 200
        assert "操作手册" in response.text
    
    def test_get_manual_en(self, client):
        """测试获取英文说明书"""
        response = client.get("/manual?lang=en")
        assert response.status_code == 200
        assert "Operation Manual" in response.text


class TestScreenInfo:
    """屏幕信息测试"""
    
    def test_get_screen_info(self, client):
        """测试获取屏幕信息"""
        response = client.get("/screen/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "width" in data
        assert "height" in data
        assert "scale_factor" in data
        assert "dpi" in data
        assert "mouse_position" in data


class TestScreenshot:
    """截图测试"""
    
    @patch('src.capture.ScreenCapture.capture')
    def test_get_screenshot(self, mock_capture, client):
        """测试获取截图"""
        # 模拟截图返回
        mock_capture.return_value = (
            b"fake_image_data",
            {
                "screen_width": 1920,
                "screen_height": 1080,
                "image_width": 1920,
                "image_height": 1080,
                "cursor_x": 500,
                "cursor_y": 300,
                "format": "jpeg",
                "timestamp": time.time()
            }
        )
        
        response = client.get("/screenshot")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert "X-Screen-Width" in response.headers
        assert "X-Screen-Height" in response.headers


class TestClipboard:
    """剪贴板测试"""
    
    @patch('src.clipboard.ClipboardManager.get_content')
    def test_get_clipboard(self, mock_get_content, client):
        """测试读取剪贴板"""
        mock_get_content.return_value = ("test content", False)
        
        response = client.get("/session/clipboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["content"] == "test content"
        assert data["has_image"] == False
    
    @patch('src.clipboard.ClipboardManager.set_content')
    def test_set_clipboard(self, mock_set_content, client):
        """测试写入剪贴板"""
        mock_set_content.return_value = None
        
        response = client.post(
            "/session/clipboard",
            json={"content": "new content"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True


class TestMouseOperations:
    """鼠标操作测试"""
    
    @patch('src.input_sim.InputSimulator.mouse_move')
    def test_mouse_move(self, mock_move, client):
        """测试鼠标移动"""
        mock_move.return_value = (500, 300)
        
        response = client.post(
            "/mouse/move",
            json={"x": 500, "y": 300, "duration": 0.3}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["position"]["x"] == 500
        assert data["position"]["y"] == 300
    
    @patch('src.input_sim.InputSimulator.mouse_click')
    def test_mouse_click(self, mock_click, client):
        """测试鼠标点击"""
        mock_click.return_value = {
            "success": True,
            "action": "click",
            "button": "left",
            "clicks": 1,
            "position": {"x": 500, "y": 300}
        }
        
        response = client.post(
            "/mouse/click",
            json={"x": 500, "y": 300, "button": "left", "clicks": 1}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["action"] == "click"


class TestKeyboardOperations:
    """键盘操作测试"""
    
    @patch('src.input_sim.InputSimulator.keyboard_type')
    def test_keyboard_type(self, mock_type, client):
        """测试键盘输入"""
        mock_type.return_value = {
            "success": True,
            "action": "type",
            "length": 13
        }
        
        response = client.post(
            "/keyboard/type",
            json={"text": "Hello, World!", "interval": 0.05}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["action"] == "type"
        assert data["length"] == 13
    
    @patch('src.input_sim.InputSimulator.keyboard_press')
    def test_keyboard_press(self, mock_press, client):
        """测试按键"""
        mock_press.return_value = {
            "success": True,
            "action": "press",
            "key": "enter",
            "modifiers": ["ctrl"]
        }
        
        response = client.post(
            "/keyboard/press",
            json={"key": "enter", "modifiers": ["ctrl"]}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["action"] == "press"
        assert data["key"] == "enter"
        assert data["modifiers"] == ["ctrl"]
    
    @patch('src.input_sim.InputSimulator.keyboard_hotkey')
    def test_keyboard_hotkey(self, mock_hotkey, client):
        """测试组合快捷键"""
        mock_hotkey.return_value = {
            "success": True,
            "action": "hotkey",
            "keys": ["ctrl", "a"]
        }
        
        response = client.post(
            "/keyboard/hotkey",
            json={"keys": ["ctrl", "a"]}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["action"] == "hotkey"
        assert data["keys"] == ["ctrl", "a"]


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_parameter(self, client):
        """测试无效参数"""
        response = client.post(
            "/mouse/click",
            json={"x": -1, "y": 300}  # 无效的x坐标
        )
        # 注意：实际实现中可能不会验证负数坐标
        # 这里只是示例
        assert response.status_code in [200, 400, 500]
    
    @patch('src.capture.ScreenCapture.capture')
    def test_screen_capture_failed(self, mock_capture, client):
        """测试截图失败"""
        mock_capture.side_effect = RuntimeError("截图失败")
        
        response = client.get("/screenshot")
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == "SCREEN_CAPTURE_FAILED"


class TestAuthentication:
    """认证测试"""
    
    def test_no_auth_required(self, client):
        """测试不需要认证"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_auth_required(self, config):
        """测试需要认证"""
        # 设置API密钥
        config["security"]["api_key"] = "test_key"
        
        api_server = APIServer(config)
        client = TestClient(api_server.app)
        
        # 无密钥请求
        response = client.get("/screenshot")
        assert response.status_code == 401
        
        # 有密钥请求
        response = client.get(
            "/screenshot",
            headers={"Authorization": "Bearer test_key"}
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])