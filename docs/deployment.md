# AI Doge Remote 部署指南

## 概述

本指南介绍如何部署和运行 AI Doge Remote 被控端。

## 系统要求

- **操作系统**: Windows 10/11 (64-bit)
- **Python**: 3.10 或更高版本
- **内存**: 至少 100MB 可用内存
- **磁盘空间**: 至少 50MB 可用空间

## 安装方式

### 方式一：从源码安装（推荐）

1. **克隆或下载项目**
   ```bash
   git clone https://github.com/ai-doge/ai-doge-remote.git
   cd ai-doge-remote
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**
   ```bash
   python -m src.main
   ```

### 方式二：使用 pip 安装

```bash
pip install ai-doge-remote
ai-doge-remote
```

### 方式三：使用打包好的可执行文件

1. 下载 `AIDogeRemote.exe`
2. 双击运行即可

## 配置说明

### 配置文件位置

配置文件默认位于：
```
%USERPROFILE%\.aidogeremote\config.json
```

### 配置文件示例

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

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `server.host` | string | `0.0.0.0` | 监听地址 |
| `server.port` | int | `8765` | 监听端口 |
| `capture.format` | string | `jpeg` | 截图格式 |
| `capture.quality` | int | `80` | JPEG 质量 |
| `capture.max_width` | int | `1920` | 最大宽度 |
| `capture.max_height` | int | `1080` | 最大高度 |
| `security.api_key` | string | `""` | API 密钥 |
| `security.notify_on_connect` | bool | `true` | 连接通知 |

## 运行模式

### 开发模式

```bash
# 启用热重载
uvicorn src.main:app --reload --host 0.0.0.0 --port 8765
```

### 生产模式

```bash
# 直接运行
python -m src.main

# 或使用 uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8765 --workers 1
```

### 后台运行

#### 使用 Windows 服务

1. 安装 `pywin32`
   ```bash
   pip install pywin32
   ```

2. 创建服务脚本 `install_service.py`
   ```python
   import win32serviceutil
   import win32service
   import win32event
   import servicemanager
   import subprocess
   import sys
   
   class AIDogeRemoteService(win32serviceutil.ServiceFramework):
       _svc_name_ = "AIDogeRemote"
       _svc_display_name_ = "AI Doge Remote Service"
       _svc_description_ = "AI Remote Desktop Control Server"
       
       def __init__(self, args):
           win32serviceutil.ServiceFramework.__init__(self, args)
           self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
           self.process = None
       
       def SvcStop(self):
           self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
           if self.process:
               self.process.terminate()
           win32event.SetEvent(self.hWaitStop)
       
       def SvcDoRun(self):
           servicemanager.LogMsg(
               servicemanager.EVENTLOG_INFORMATION_TYPE,
               servicemanager.PYS_SERVICE_STARTED,
               (self._svc_name_, '')
           )
           self.main()
       
       def main(self):
           python_exe = sys.executable
           script_path = r"C:\path\to\ai-doge-remote\src\main.py"
           self.process = subprocess.Popen([python_exe, script_path])
           win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
   
   if __name__ == '__main__':
       win32serviceutil.HandleCommandLine(AIDogeRemoteService)
   ```

3. 安装服务
   ```bash
   python install_service.py install
   ```

4. 启动服务
   ```bash
   python install_service.py start
   ```

#### 使用任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为"计算机启动时"
4. 操作为"启动程序"
5. 程序路径指向 `python.exe` 或 `AIDogeRemote.exe`
6. 参数为 `-m src.main`（如果是 Python）

## 打包为可执行文件

### 使用 PyInstaller

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为单文件
pyinstaller --onefile --windowed --icon=assets/doge.ico src/main.py

# 打包为目录
pyinstaller --windowed --icon=assets/doge.ico src/main.py
```

### 使用 Nuitka

```bash
# 安装 Nuitka
pip install nuitka

# 打包
nuitka --standalone --onefile --windows-icon-from-ico=assets/doge.ico src/main.py
```

## 网络配置

### 防火墙设置

如果需要从其他设备访问，需要在 Windows 防火墙中添加规则：

1. 打开"Windows Defender 防火墙"
2. 点击"高级设置"
3. 选择"入站规则" -> "新建规则"
4. 选择"端口"
5. 输入端口号（默认 8765）
6. 选择"允许连接"
7. 选择适用的网络类型
8. 输入规则名称

### 路由器端口转发

如果需要从外网访问，需要在路由器中设置端口转发：

1. 登录路由器管理界面
2. 找到端口转发设置
3. 添加规则：外部端口 8765 -> 内部 IP:8765
4. 保存并应用

## 安全建议

1. **设置 API 密钥**
   - 在配置文件中设置 `security.api_key`
   - 使用强密码（至少 16 位，包含大小写字母、数字、特殊字符）

2. **限制访问 IP**
   - 如果只需要本地访问，将 `server.host` 设置为 `127.0.0.1`
   - 如果需要局域网访问，确保网络环境安全

3. **启用 HTTPS**（可选）
   - 使用反向代理（如 Nginx）配置 SSL
   - 或使用 Let's Encrypt 获取免费证书

4. **定期更新**
   - 定期检查项目更新
   - 及时修复安全漏洞

## 故障排除

### 常见问题

#### 1. 端口被占用

**错误信息**: `Address already in use`

**解决方法**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8765

# 终止进程
taskkill /PID <进程ID> /F

# 或修改配置使用其他端口
```

#### 2. 截图失败

**错误信息**: `SCREEN_CAPTURE_FAILED`

**解决方法**:
- 确保显示器已连接
- 检查是否有远程桌面会话断开
- 尝试以管理员权限运行

#### 3. 输入模拟失败

**错误信息**: `INPUT_FAILED`

**解决方法**:
- 确保目标窗口存在
- 检查是否有 UAC 弹窗
- 尝试以管理员权限运行

#### 4. 依赖安装失败

**解决方法**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 日志文件

日志文件位于：
```
%USERPROFILE%\.aidogeremote\logs\ai-doge-remote.log
```

## 性能优化

### 截图性能

1. **使用 JPEG 格式**：比 PNG 更快，文件更小
2. **降低质量**：将 `capture.quality` 设置为 60-80
3. **缩小分辨率**：设置 `capture.max_width` 和 `capture.max_height`
4. **使用区域截图**：只截取需要的区域

### 网络性能

1. **使用有线网络**：比无线网络更稳定
2. **减少截图频率**：避免频繁请求截图
3. **使用压缩**：启用 HTTP 压缩

## 监控与维护

### 健康检查

定期调用 `/health` 端点检查服务状态。

### 日志监控

监控日志文件，及时发现错误。

### 资源监控

监控 CPU、内存使用情况，确保服务稳定运行。

## 升级与备份

### 升级步骤

1. 备份配置文件
2. 下载新版本
3. 停止旧服务
4. 替换文件
5. 启动新服务
6. 验证功能

### 备份内容

- 配置文件：`%USERPROFILE%\.aidogeremote\config.json`
- 日志文件：`%USERPROFILE%\.aidogeremote\logs\`
- 自定义图标：`assets/`

---

*文档版本：1.0*  
*最后更新：2026年6月19日*