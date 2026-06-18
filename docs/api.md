# AI Doge Remote API 文档

## 概述

AI Doge Remote 提供 RESTful HTTP API，用于远程控制 Windows 桌面。

## 基础信息

- **基础地址**: `http://<被控端IP>:<端口>`（默认 `http://localhost:8765`）
- **内容类型**: 请求体统一使用 `application/json`
- **响应格式**: 成功返回 JSON 或二进制图片；失败返回 JSON 错误体
- **字符编码**: UTF-8
- **API 文档**: 自动生成的 Swagger UI 可通过 `/docs` 访问
- **坐标系**: 屏幕左上角为原点 `(0, 0)`，X 轴向右，Y 轴向下
- **坐标单位**: 像素（px）

## 认证

若配置了 API 密钥，请求头必须包含：
```
Authorization: Bearer <api_key>
```

## 错误响应格式

所有错误返回统一的 JSON 结构：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {
      "parameter": "参数名",
      "received": "接收到的值"
    }
  }
}
```

## API 端点

### 1. 健康检查

**GET /health**

检测被控端是否在线、服务是否正常运行。

**响应** `200 OK`：
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "screen": {
    "width": 1920,
    "height": 1080
  }
}
```

---

### 2. 获取 AI 说明书

**GET /manual**

返回一份结构化的说明书，告诉 AI Agent 如何使用本系统。

**请求参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `format` | string | 否 | `plain` | 返回格式：`plain` 或 `markdown` |
| `lang` | string | 否 | `en` | 语言：`en` 或 `zh` |

**响应** `200 OK`：

| format | Content-Type | 说明 |
|--------|--------------|------|
| `plain` | `text/plain; charset=utf-8` | 纯文本格式 |
| `markdown` | `text/markdown; charset=utf-8` | Markdown 格式 |

---

### 3. 获取屏幕截图

**GET /screenshot**

获取当前屏幕的截图。

**请求参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `format` | string | 否 | 配置值 | 返回格式：`png` 或 `jpeg` |
| `quality` | int | 否 | 配置值 | JPEG 质量 1–100 |
| `scale` | float | 否 | `1.0` | 缩放比例 0.1–1.0 |
| `region` | string | 否 | 全屏 | 截取区域，格式：`x,y,width,height` |
| `cursor` | bool | 否 | `true` | 是否绘制鼠标指针 |

**响应** `200 OK`：

| 格式 | Content-Type | Body |
|------|--------------|------|
| PNG | `image/png` | PNG 二进制数据 |
| JPEG | `image/jpeg` | JPEG 二进制数据 |

**响应头**：

| Header | 示例值 | 说明 |
|--------|--------|------|
| `X-Screen-Width` | `1920` | 原始屏幕宽度 |
| `X-Screen-Height` | `1080` | 原始屏幕高度 |
| `X-Screenshot-Width` | `960` | 返回图片实际宽度 |
| `X-Screenshot-Height` | `540` | 返回图片实际高度 |
| `X-Cursor-X` | `500` | 截图时鼠标 X 坐标 |
| `X-Cursor-Y` | `300` | 截图时鼠标 Y 坐标 |

---

### 4. 鼠标移动

**POST /mouse/move**

将鼠标指针移动到指定屏幕坐标。

**请求体**：
```json
{
  "x": 500,
  "y": 300,
  "duration": 0.3
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `x` | int | ✅ | 目标 X 坐标（像素） |
| `y` | int | ✅ | 目标 Y 坐标（像素） |
| `duration` | float | 否 | 移动耗时（秒），默认 `0` |

**响应** `200 OK`：
```json
{
  "success": true,
  "position": { "x": 500, "y": 300 }
}
```

---

### 5. 鼠标点击

**POST /mouse/click**

在指定坐标执行鼠标点击。

**请求体**：
```json
{
  "x": 500,
  "y": 300,
  "button": "left",
  "clicks": 1,
  "interval": 0.1
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `x` | int | ✅ | 点击位置 X 坐标 |
| `y` | int | ✅ | 点击位置 Y 坐标 |
| `button` | string | 否 | 按键：`left`（默认）/ `right` / `middle` |
| `clicks` | int | 否 | 点击次数：`1`（默认）、`2`（双击） |
| `interval` | float | 否 | 多次点击间隔（秒），默认 `0.1` |

**响应** `200 OK`：
```json
{
  "success": true,
  "action": "click",
  "button": "left",
  "clicks": 1,
  "position": { "x": 500, "y": 300 }
}
```

---

### 6. 鼠标滚轮

**POST /mouse/scroll**

在指定位置执行滚轮滚动。

**请求体**：
```json
{
  "x": 500,
  "y": 300,
  "dx": 0,
  "dy": -3
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `x` | int | 否 | 滚轮位置 X（不传则在当前鼠标位置） |
| `y` | int | 否 | 滚轮位置 Y |
| `dx` | int | 否 | 水平滚动量，默认 `0` |
| `dy` | int | ✅ | 垂直滚动量，正数向下，负数向上 |

**响应** `200 OK`：
```json
{
  "success": true,
  "action": "scroll",
  "delta": { "dx": 0, "dy": -3 }
}
```

---

### 7. 鼠标拖拽

**POST /mouse/drag**

从起点按住鼠标拖拽到终点。

**请求体**：
```json
{
  "from_x": 100,
  "from_y": 200,
  "to_x": 500,
  "to_y": 400,
  "button": "left",
  "duration": 0.5
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `from_x` | int | ✅ | 起点 X |
| `from_y` | int | ✅ | 起点 Y |
| `to_x` | int | ✅ | 终点 X |
| `to_y` | int | ✅ | 终点 Y |
| `button` | string | 否 | 按键，默认 `left` |
| `duration` | float | 否 | 拖拽耗时（秒），默认 `0.5` |

**响应** `200 OK`：
```json
{
  "success": true,
  "action": "drag",
  "from": { "x": 100, "y": 200 },
  "to": { "x": 500, "y": 400 }
}
```

---

### 8. 键盘输入文本

**POST /keyboard/type**

模拟键盘输入一段文本。

**请求体**：
```json
{
  "text": "Hello, World!",
  "interval": 0.05
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | ✅ | 要输入的文本内容 |
| `interval` | float | 否 | 每个字符间隔（秒），默认 `0.02` |

**响应** `200 OK`：
```json
{
  "success": true,
  "action": "type",
  "length": 13
}
```

---

### 9. 按下单个键

**POST /keyboard/press**

模拟按下并释放一个键盘按键。

**请求体**：
```json
{
  "key": "enter",
  "modifiers": ["ctrl"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `key` | string | ✅ | 按键名（见下方按键表） |
| `modifiers` | string[] | 否 | 修饰键列表：`ctrl` / `alt` / `shift` / `win` |

**支持的按键名**：

| 分类 | 按键名 |
|------|--------|
| 字母 | `a`–`z` |
| 数字 | `0`–`9` |
| 功能键 | `f1`–`f12` |
| 方向键 | `up` / `down` / `left` / `right` |
| 控制键 | `enter` / `tab` / `escape` / `backspace` / `delete` / `space` |
| 编辑键 | `home` / `end` / `pageup` / `pagedown` / `insert` |
| 锁定键 | `capslock` / `numlock` / `scrolllock` |

**响应** `200 OK`：
```json
{
  "success": true,
  "action": "press",
  "key": "enter",
  "modifiers": ["ctrl"]
}
```

---

### 10. 组合快捷键

**POST /keyboard/hotkey**

执行组合快捷键。

**请求体**：
```json
{
  "keys": ["ctrl", "a"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keys` | string[] | ✅ | 按键列表，按顺序按下，逆序释放 |

**响应** `200 OK`：
```json
{
  "success": true,
  "action": "hotkey",
  "keys": ["ctrl", "a"]
}
```

---

### 11. 获取屏幕信息

**GET /screen/info**

获取屏幕分辨率、DPI 缩放等信息。

**响应** `200 OK`：
```json
{
  "width": 1920,
  "height": 1080,
  "scale_factor": 1.25,
  "dpi": 120,
  "mouse_position": { "x": 500, "y": 300 }
}
```

---

### 12. 读取剪贴板

**GET /session/clipboard**

读取被控端的剪贴板内容。

**响应**：
```json
{
  "content": "剪贴板中的文本内容",
  "has_image": false
}
```

---

### 13. 写入剪贴板

**POST /session/clipboard**

设置被控端的剪贴板内容。

**请求体**：
```json
{
  "content": "要写入剪贴板的文本"
}
```

**响应**：
```json
{
  "success": true
}
```

---

## 错误码列表

| 错误码 | HTTP 状态码 | 含义 |
|--------|-------------|------|
| `UNAUTHORIZED` | 401 | API 密钥缺失或无效 |
| `INVALID_PARAMETER` | 400 | 请求参数不合法 |
| `SCREEN_CAPTURE_FAILED` | 500 | 截图失败 |
| `INPUT_FAILED` | 500 | 输入模拟失败 |
| `INTERNAL_ERROR` | 500 | 未知内部错误 |

---

## 使用示例

### Python 示例

```python
import requests

base_url = "http://localhost:8765"

# 健康检查
response = requests.get(f"{base_url}/health")
print(response.json())

# 获取截图
response = requests.get(f"{base_url}/screenshot?format=jpeg&quality=80")
with open("screenshot.jpg", "wb") as f:
    f.write(response.content)

# 鼠标点击
response = requests.post(f"{base_url}/mouse/click", json={
    "x": 500,
    "y": 300,
    "button": "left",
    "clicks": 1
})
print(response.json())

# 键盘输入
response = requests.post(f"{base_url}/keyboard/type", json={
    "text": "Hello, World!",
    "interval": 0.05
})
print(response.json())
```

### cURL 示例

```bash
# 健康检查
curl http://localhost:8765/health

# 获取截图
curl -o screenshot.jpg http://localhost:8765/screenshot?format=jpeg

# 鼠标点击
curl -X POST http://localhost:8765/mouse/click \
  -H "Content-Type: application/json" \
  -d '{"x": 500, "y": 300, "button": "left", "clicks": 1}'

# 键盘输入
curl -X POST http://localhost:8765/keyboard/type \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, World!", "interval": 0.05}'
```

---

*文档版本：1.0*  
*最后更新：2026年6月19日*