"""
配置管理模块
负责加载、保存、验证配置文件
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import os


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Path):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件失败: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
            self.save(self.config)
        
        # 合并默认配置（确保所有必要的键存在）
        self.config = self._merge_with_default(self.config)
        return self.config
    
    def save(self, config: Dict[str, Any]):
        """
        保存配置文件
        
        Args:
            config: 配置字典
        """
        self.config = config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键（支持点号分隔，如 "server.port"）
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置项
        
        Args:
            key: 配置键（支持点号分隔）
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            是否有效
        """
        try:
            # 验证服务器配置
            server = self.config.get("server", {})
            port = server.get("port", 8765)
            if not (1024 <= port <= 65535):
                return False
            
            # 验证截图配置
            capture = self.config.get("capture", {})
            quality = capture.get("quality", 80)
            if not (1 <= quality <= 100):
                return False
            
            return True
        except Exception:
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "server": {
                "host": "0.0.0.0",
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
    
    def _merge_with_default(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """与默认配置合并"""
        default = self._get_default_config()
        
        def merge(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = merge(base[key], value)
                else:
                    base[key] = value
            return base
        
        return merge(default, config)


def get_config_path() -> Path:
    """获取配置文件路径"""
    # 优先使用环境变量
    if "AIDOGE_CONFIG" in os.environ:
        return Path(os.environ["AIDOGE_CONFIG"])
    
    # 默认路径
    return Path.home() / ".aidogeremote" / "config.json"