# AI Doge Remote - 被控端

🐕 AI远程桌面控制被控端 - 为AI Agent提供远程桌面控制能力

## 项目简介

AI Doge Remote 是一个运行在 Windows 桌面端的常驻服务程序，为 AI Agent 提供远程桌面控制能力。通过 HTTP API 获取屏幕截图、发送鼠标/键盘事件，实现 AI 对 Windows 桌面的远程操控。

## 核心特性

- **屏幕截图**：实时获取桌面截图，支持多种格式和参数
- **鼠标控制**：移动、点击、滚轮、拖拽等完整鼠标操作
- **键盘控制**：文本输入、按键、组合快捷键等键盘操作
- **剪贴板共享**：读写系统剪贴板，高效传输数据
- **系统托盘**：后台常驻，托盘图标管理
- **设置界面**：GUI配置界面，方便参数调整

## 技术栈

- **Python 3.10+**
- **FastAPI** - 现代、快速的Web框架
- **uvicorn** - 轻量级ASGI服务器
- **mss** - 高性能屏幕截图库
- **Pillow** - 图像处理库
- **pyautogui** - 跨平台GUI自动化
- **pystray** - 系统托盘管理

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 开发模式
uvicorn src.main:app --reload --host 0.0.0.0 --port 8765

# 生产模式
uvicorn src.main:app --host 0.0.0.0 --port 8765
```

### 访问API文档

启动后访问：http://localhost:8765/docs

## API 接口

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /manual | 获取AI说明书 |
| GET | /screenshot | 获取屏幕截图 |
| GET | /screen/info | 获取屏幕信息 |
| GET | /session/clipboard | 读取剪贴板 |
| POST | /mouse/move | 移动鼠标 |
| POST | /mouse/click | 鼠标点击 |
| POST | /mouse/scroll | 鼠标滚轮 |
| POST | /mouse/drag | 鼠标拖拽 |
| POST | /keyboard/type | 输入文本 |
| POST | /keyboard/press | 按下单个键 |
| POST | /keyboard/hotkey | 组合快捷键 |
| POST | /session/clipboard | 写入剪贴板 |

## 项目结构

```
ai-doge-remote/
├── README.md                   # 项目说明
├── requirements.txt            # Python依赖
├── pyproject.toml              # 项目元数据
├── build.bat                   # 一键打包脚本
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # 入口：初始化所有模块并启动
│   ├── config.py               # 配置加载/保存
│   ├── server.py               # FastAPI HTTP Server
│   ├── capture.py              # 屏幕截图引擎
│   ├── input_sim.py            # 鼠标/键盘输入模拟
│   ├── tray.py                 # 系统托盘管理
│   ├── settings_ui.py          # 设置界面 (tkinter)
│   └── logger.py               # 日志配置
│
├── assets/
│   ├── doge.ico                # 托盘图标
│   └── doge_256.png            # 高清图标
│
├── tests/
│   ├── test_api.py             # API接口测试
│   ├── test_capture.py         # 截图模块测试
│   └── test_input.py           # 输入模拟测试
│
└── docs/
    ├── api.md                  # API详细文档
    └── deployment.md           # 部署指南
```

## 配置说明

配置文件路径：`%APPDATA%\AIDogeRemote\config.json`

```json
{
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
    "notify_on_connect": true
  }
}
```

## 开发指南

### 代码规范

- 使用类型注解
- 遵循PEP 8规范
- 编写单元测试
- 更新文档

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 打包

```bash
# 使用PyInstaller打包
pyinstaller --onefile --windowed src/main.py

# 使用build.bat一键打包
build.bat
```

## 安全说明

- 支持API密钥认证
- 建议在局域网内使用
- 可配置连接通知
- 支持HTTPS（可选）

## 许可证

MIT License

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 联系方式

- 项目主页：https://github.com/ai-doge/ai-doge-remote
- 问题反馈：https://github.com/ai-doge/ai-doge-remote/issues

---

**AI Doge Remote** - 让AI拥有眼睛和手 🐕