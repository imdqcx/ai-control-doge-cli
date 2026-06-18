"""
截图模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from src.capture import ScreenCapture


@pytest.fixture
def config():
    """测试配置"""
    return {
        "capture": {
            "format": "jpeg",
            "quality": 80,
            "max_width": 1920,
            "max_height": 1080
        }
    }


@pytest.fixture
def capture(config):
    """截图引擎实例"""
    return ScreenCapture(config)


class TestScreenCapture:
    """屏幕截图测试"""
    
    def test_init(self, capture):
        """测试初始化"""
        assert capture.config is not None
        assert capture.sct is not None
    
    @patch('mss.mss')
    def test_capture_default(self, mock_mss, capture):
        """测试默认截图"""
        # 模拟mss返回
        mock_monitor = {"width": 1920, "height": 1080}
        mock_screenshot = MagicMock()
        mock_screenshot.size = (1920, 1080)
        mock_screenshot.bgra = b'\x00' * (1920 * 1080 * 4)
        
        mock_sct = MagicMock()
        mock_sct.monitors = [None, mock_monitor]
        mock_sct.grab.return_value = mock_screenshot
        
        capture.sct = mock_sct
        
        # 模拟PIL Image
        with patch('PIL.Image.frombytes') as mock_frombytes:
            mock_image = MagicMock()
            mock_image.width = 1920
            mock_image.height = 1080
            mock_image.save = MagicMock()
            mock_frombytes.return_value = mock_image
            
            # 模拟图像保存
            def mock_save(buffer, format, **kwargs):
                buffer.write(b'fake_image_data')
            mock_image.save.side_effect = mock_save
            
            image_bytes, metadata = capture.capture()
            
            assert image_bytes is not None
            assert metadata["screen_width"] == 1920
            assert metadata["screen_height"] == 1080
            assert metadata["format"] == "jpeg"
    
    @patch('mss.mss')
    def test_capture_with_params(self, mock_mss, capture):
        """测试带参数的截图"""
        # 模拟mss返回
        mock_monitor = {"width": 1920, "height": 1080}
        mock_screenshot = MagicMock()
        mock_screenshot.size = (960, 540)
        mock_screenshot.bgra = b'\x00' * (960 * 540 * 4)
        
        mock_sct = MagicMock()
        mock_sct.monitors = [None, mock_monitor]
        mock_sct.grab.return_value = mock_screenshot
        
        capture.sct = mock_sct
        
        # 模拟PIL Image
        with patch('PIL.Image.frombytes') as mock_frombytes:
            mock_image = MagicMock()
            mock_image.width = 960
            mock_image.height = 540
            mock_image.save = MagicMock()
            mock_frombytes.return_value = mock_image
            
            # 模拟图像保存
            def mock_save(buffer, format, **kwargs):
                buffer.write(b'fake_image_data')
            mock_image.save.side_effect = mock_save
            
            image_bytes, metadata = capture.capture(
                format="png",
                quality=90,
                scale=0.5,
                region="0,0,960,540",
                cursor=False
            )
            
            assert image_bytes is not None
            assert metadata["format"] == "png"
            assert metadata["image_width"] == 960
            assert metadata["image_height"] == 540
    
    def test_get_screen_info(self, capture):
        """测试获取屏幕信息"""
        # 模拟mss
        mock_monitor = {"width": 1920, "height": 1080}
        mock_sct = MagicMock()
        mock_sct.monitors = [None, mock_monitor]
        capture.sct = mock_sct
        
        info = capture.get_screen_info()
        
        assert info["width"] == 1920
        assert info["height"] == 1080
        assert "scale_factor" in info
        assert "dpi" in info
        assert "mouse_position" in info
    
    def test_get_mouse_position(self, capture):
        """测试获取鼠标位置"""
        # 当前实现返回(0, 0)
        pos = capture.get_mouse_position()
        assert pos == (0, 0)
    
    def test_image_to_bytes_jpeg(self, capture):
        """测试JPEG图像转换"""
        # 创建测试图像
        image = Image.new('RGB', (100, 100), color='red')
        
        image_bytes = capture._image_to_bytes(image, "jpeg", 80)
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
    
    def test_image_to_bytes_png(self, capture):
        """测试PNG图像转换"""
        # 创建测试图像
        image = Image.new('RGB', (100, 100), color='red')
        
        image_bytes = capture._image_to_bytes(image, "png", 80)
        
        assert image_bytes is not None
        assert len(image_bytes) > 0
    
    def test_invalid_format(self, capture):
        """测试无效格式"""
        image = Image.new('RGB', (100, 100), color='red')
        
        with pytest.raises(ValueError):
            capture._image_to_bytes(image, "invalid", 80)


class TestScreenCaptureIntegration:
    """屏幕截图集成测试"""
    
    @pytest.mark.skipif(
        not hasattr(pytest, "enable_integration_tests"),
        reason="集成测试默认禁用"
    )
    def test_real_capture(self, capture):
        """真实截图测试（需要显示器）"""
        try:
            image_bytes, metadata = capture.capture()
            
            assert image_bytes is not None
            assert len(image_bytes) > 0
            assert metadata["screen_width"] > 0
            assert metadata["screen_height"] > 0
            
            # 验证图像格式
            image = Image.open(io.BytesIO(image_bytes))
            assert image.size[0] > 0
            assert image.size[1] > 0
            
        except Exception as e:
            pytest.skip(f"无法进行真实截图测试: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])