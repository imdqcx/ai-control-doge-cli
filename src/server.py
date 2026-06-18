"""
HTTP服务器模块
负责API路由、请求处理、中间件
"""

import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import io

from .capture import ScreenCapture
from .input_sim import InputSimulator
from .clipboard import ClipboardManager
from .logger import get_logger

logger = get_logger(__name__)


class APIServer:
    """API服务器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化API服务器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.start_time = time.time()
        
        # 初始化核心模块
        self.capture = ScreenCapture(config)
        self.input_sim = InputSimulator()
        self.clipboard = ClipboardManager()
        
        # 创建FastAPI应用
        self.app = self._create_app()
        
        # 添加路由
        self._add_routes()
        
        # 添加中间件
        self._add_middleware()
        
        # 服务器实例
        self.server: Optional[uvicorn.Server] = None
    
    def _create_app(self) -> FastAPI:
        """创建FastAPI应用"""
        app = FastAPI(
            title="AI Doge Remote",
            description="AI远程桌面控制被控端",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        return app
    
    def _add_routes(self):
        """添加API路由"""
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {
                "status": "ok",
                "version": "1.0.0",
                "uptime_seconds": time.time() - self.start_time,
                "screen": self.capture.get_screen_info()
            }
        
        @self.app.get("/manual")
        async def get_manual(format: str = "plain", lang: str = "en"):
            """获取AI说明书"""
            # 动态生成说明书
            screen_info = self.capture.get_screen_info()
            mouse_pos = self.capture.get_mouse_position()
            
            manual_content = self._generate_manual(screen_info, mouse_pos, lang)
            
            if format == "markdown":
                return Response(
                    content=manual_content,
                    media_type="text/markdown; charset=utf-8"
                )
            else:
                return Response(
                    content=manual_content,
                    media_type="text/plain; charset=utf-8"
                )
        
        @self.app.get("/screenshot")
        async def get_screenshot(
            format: str = None,
            quality: int = None,
            scale: float = 1.0,
            region: str = None,
            cursor: bool = True
        ):
            """获取屏幕截图"""
            try:
                image_bytes, metadata = self.capture.capture(
                    format=format,
                    quality=quality,
                    scale=scale,
                    region=region,
                    cursor=cursor
                )
                
                # 确定Content-Type
                if metadata["format"] == "png":
                    content_type = "image/png"
                else:
                    content_type = "image/jpeg"
                
                # 创建响应
                response = Response(
                    content=image_bytes,
                    media_type=content_type
                )
                
                # 添加自定义响应头
                response.headers["X-Screen-Width"] = str(metadata["screen_width"])
                response.headers["X-Screen-Height"] = str(metadata["screen_height"])
                response.headers["X-Screenshot-Width"] = str(metadata["image_width"])
                response.headers["X-Screenshot-Height"] = str(metadata["image_height"])
                response.headers["X-Cursor-X"] = str(metadata["cursor_x"])
                response.headers["X-Cursor-Y"] = str(metadata["cursor_y"])
                
                return response
                
            except Exception as e:
                logger.error(f"截图失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "SCREEN_CAPTURE_FAILED",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.get("/screen/info")
        async def get_screen_info():
            """获取屏幕信息"""
            return self.capture.get_screen_info()
        
        @self.app.get("/session/clipboard")
        async def get_clipboard():
            """读取剪贴板"""
            try:
                content, has_image = self.clipboard.get_content()
                return {
                    "content": content,
                    "has_image": has_image
                }
            except Exception as e:
                logger.error(f"读取剪贴板失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/session/clipboard")
        async def set_clipboard(request: Request):
            """写入剪贴板"""
            try:
                data = await request.json()
                content = data.get("content", "")
                self.clipboard.set_content(content)
                return {"success": True}
            except Exception as e:
                logger.error(f"写入剪贴板失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/mouse/move")
        async def mouse_move(request: Request):
            """移动鼠标"""
            try:
                data = await request.json()
                x = data.get("x")
                y = data.get("y")
                duration = data.get("duration", 0)
                
                if x is None or y is None:
                    raise ValueError("x and y are required")
                
                position = self.input_sim.mouse_move(x, y, duration)
                return {
                    "success": True,
                    "position": {"x": position[0], "y": position[1]}
                }
            except Exception as e:
                logger.error(f"鼠标移动失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INPUT_FAILED",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/mouse/click")
        async def mouse_click(request: Request):
            """鼠标点击"""
            try:
                data = await request.json()
                x = data.get("x")
                y = data.get("y")
                button = data.get("button", "left")
                clicks = data.get("clicks", 1)
                interval = data.get("interval", 0.1)
                
                if x is None or y is None:
                    raise ValueError("x and y are required")
                
                result = self.input_sim.mouse_click(x, y, button, clicks, interval)
                return result
            except Exception as e:
                logger.error(f"鼠标点击失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INPUT_FAILED",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/mouse/scroll")
        async def mouse_scroll(request: Request):
            """鼠标滚轮"""
            try:
                data = await request.json()
                x = data.get("x")
                y = data.get("y")
                dx = data.get("dx", 0)
                dy = data.get("dy")
                
                if dy is None:
                    raise ValueError("dy is required")
                
                # 如果没有指定位置，使用当前位置
                if x is None or y is None:
                    x, y = self.capture.get_mouse_position()
                
                result = self.input_sim.mouse_scroll(x, y, dx, dy)
                return result
            except Exception as e:
                logger.error(f"鼠标滚轮失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INPUT_FAILED",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/mouse/drag")
        async def mouse_drag(request: Request):
            """鼠标拖拽"""
            try:
                data = await request.json()
                from_x = data.get("from_x")
                from_y = data.get("from_y")
                to_x = data.get("to_x")
                to_y = data.get("to_y")
                button = data.get("button", "left")
                duration = data.get("duration", 0.5)
                
                if None in (from_x, from_y, to_x, to_y):
                    raise ValueError("from_x, from_y, to_x, to_y are required")
                
                result = self.input_sim.mouse_drag(from_x, from_y, to_x, to_y, button, duration)
                return result
            except Exception as e:
                logger.error(f"鼠标拖拽失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INPUT_FAILED",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/keyboard/type")
        async def keyboard_type(request: Request):
            """键盘输入文本"""
            try:
                data = await request.json()
                text = data.get("text")
                interval = data.get("interval", 0.02)
                
                if text is None:
                    raise ValueError("text is required")
                
                result = self.input_sim.keyboard_type(text, interval)
                return result
            except Exception as e:
                logger.error(f"键盘输入失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INPUT_FAILED",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/keyboard/press")
        async def keyboard_press(request: Request):
            """按下单个键"""
            try:
                data = await request.json()
                key = data.get("key")
                modifiers = data.get("modifiers", [])
                
                if key is None:
                    raise ValueError("key is required")
                
                result = self.input_sim.keyboard_press(key, modifiers)
                return result
            except Exception as e:
                logger.error(f"按键失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INPUT_FAILED",
                            "message": str(e)
                        }
                    }
                )
        
        @self.app.post("/keyboard/hotkey")
        async def keyboard_hotkey(request: Request):
            """组合快捷键"""
            try:
                data = await request.json()
                keys = data.get("keys")
                
                if keys is None or not isinstance(keys, list):
                    raise ValueError("keys is required and must be a list")
                
                result = self.input_sim.keyboard_hotkey(keys)
                return result
            except Exception as e:
                logger.error(f"组合快捷键失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": {
                            "code": "INPUT_FAILED",
                            "message": str(e)
                        }
                    }
                )
    
    def _add_middleware(self):
        """添加中间件"""
        
        # CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 认证中间件
        @self.app.middleware("http")
        async def auth_middleware(request: Request, call_next):
            """认证中间件"""
            # 检查是否需要认证
            api_key = self.config.get("security", {}).get("api_key", "")
            
            if api_key:
                # 跳过健康检查和文档端点
                if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
                    return await call_next(request)
                
                # 检查Authorization头
                auth_header = request.headers.get("Authorization")
                if not auth_header or auth_header != f"Bearer {api_key}":
                    return JSONResponse(
                        status_code=401,
                        content={
                            "error": {
                                "code": "UNAUTHORIZED",
                                "message": "API key is missing or invalid"
                            }
                        }
                    )
            
            return await call_next(request)
        
        # 请求日志中间件
        @self.app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            """请求日志中间件"""
            start_time = time.time()
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.3f}s"
            )
            
            return response
    
    def _generate_manual(self, screen_info: dict, mouse_pos: tuple, lang: str) -> str:
        """生成AI说明书"""
        if lang == "zh":
            return self._generate_manual_zh(screen_info, mouse_pos)
        else:
            return self._generate_manual_en(screen_info, mouse_pos)
    
    def _generate_manual_zh(self, screen_info: dict, mouse_pos: tuple) -> str:
        """生成中文说明书"""
        return f"""=== AI Doge Remote - 操作手册 ===

【产品简介】
AI Doge Remote v1.0.0 是一个运行在 Windows 桌面的远程控制被控端。
你（AI Agent）可以通过 HTTP API 获取屏幕截图、模拟鼠标和键盘操作。
本手册包含你需要知道的全部信息。

【屏幕信息】
分辨率: {screen_info['width']} x {screen_info['height']}
缩放比例: {screen_info['scale_factor']} (DPI: {screen_info['dpi']})
当前鼠标位置: ({mouse_pos[0]}, {mouse_pos[1]})

【能力总览】
• 截图 — 看到当前桌面内容
• 鼠标 — 移动、点击（单击/双击/右键）、滚轮、拖拽
• 键盘 — 输入文本、按下单键、组合快捷键
• 剪贴板 — 读写剪贴板，高效传输文本数据

【坐标系】
原点在屏幕左上角 (0, 0)。
X 轴向右增大，Y 轴向下增大。
单位是像素（px）。坐标不能为负数，不能超过屏幕分辨率。

【接口清单】
GET  /health             — 健康检查，确认服务是否在线
GET  /manual             — 获取本说明书（你正在读的就是这个接口的返回）
GET  /screenshot         — 获取当前屏幕截图（PNG/JPEG）
GET  /screen/info        — 获取屏幕分辨率、DPI 等信息
GET  /session/clipboard  — 读取剪贴板内容
POST /mouse/move         — 移动鼠标到指定坐标
POST /mouse/click        — 鼠标点击（支持单击/双击/右键）
POST /mouse/scroll       — 鼠标滚轮滚动
POST /mouse/drag         — 鼠标拖拽（从 A 点到 B 点）
POST /keyboard/type      — 逐字符输入文本
POST /keyboard/press     — 按下单个键（支持修饰键组合）
POST /keyboard/hotkey    — 组合快捷键（如 Ctrl+C）
POST /session/clipboard  — 写入剪贴板

【典型工作流：看 → 想 → 做】
1. 调用 GET /screenshot 获取当前桌面截图
2. 分析截图，理解桌面上有什么（窗口、按钮、文本框等）
3. 根据任务目标，调用鼠标/键盘接口执行操作
4. 再次调用 GET /screenshot 确认操作结果
5. 如果任务未完成，回到步骤 2 继续

【注意事项】
• 截图后有约 100-200ms 的处理延迟，操作后请稍等再截图确认
• 双击操作通常用于打开文件/文件夹
• 右键点击会弹出上下文菜单，需要再次截图查看菜单内容
• 大段文本传输建议使用剪贴板（POST /session/clipboard）而非逐字输入
• 某些操作可能触发 Windows UAC 弹窗，截图中会看到弹窗，需要特殊处理

【错误处理】
• 401 UNAUTHORIZED — 请检查 API 密钥是否正确
• 400 INVALID_PARAMETER — 检查请求参数格式和取值范围
• 500 SCREEN_CAPTURE_FAILED — 截图失败，可能是显示器断开，请稍后重试
• 500 INPUT_FAILED — 输入模拟失败，可能是目标窗口已关闭

=== 手册结束 ==="""
    
    def _generate_manual_en(self, screen_info: dict, mouse_pos: tuple) -> str:
        """生成英文说明书"""
        return f"""=== AI Doge Remote - Operation Manual ===

【Product Introduction】
AI Doge Remote v1.0.0 is a remote control server running on Windows desktop.
You (AI Agent) can get screenshots and simulate mouse/keyboard operations through HTTP API.
This manual contains all the information you need to know.

【Screen Information】
Resolution: {screen_info['width']} x {screen_info['height']}
Scale Factor: {screen_info['scale_factor']} (DPI: {screen_info['dpi']})
Current Mouse Position: ({mouse_pos[0]}, {mouse_pos[1]})

【Capabilities】
• Screenshot — See current desktop content
• Mouse — Move, click (single/double/right), scroll, drag
• Keyboard — Type text, press single key, combination shortcuts
• Clipboard — Read/write clipboard, efficient text data transfer

【Coordinate System】
Origin is at the top-left corner of the screen (0, 0).
X axis increases to the right, Y axis increases downward.
Unit is pixels (px). Coordinates cannot be negative or exceed screen resolution.

【API Endpoints】
GET  /health             — Health check, confirm service is online
GET  /manual             — Get this manual (what you're reading now)
GET  /screenshot         — Get current screenshot (PNG/JPEG)
GET  /screen/info        — Get screen resolution, DPI, etc.
GET  /session/clipboard  — Read clipboard content
POST /mouse/move         — Move mouse to specified coordinates
POST /mouse/click        — Mouse click (single/double/right)
POST /mouse/scroll       — Mouse scroll
POST /mouse/drag         — Mouse drag (from point A to B)
POST /keyboard/type      — Type text character by character
POST /keyboard/press     — Press single key (with modifier keys)
POST /keyboard/hotkey    — Combination shortcut (e.g., Ctrl+C)
POST /session/clipboard  — Write to clipboard

【Typical Workflow: See → Think → Do】
1. Call GET /screenshot to get current desktop screenshot
2. Analyze screenshot, understand what's on the desktop (windows, buttons, text fields, etc.)
3. Based on task goals, call mouse/keyboard APIs to perform operations
4. Call GET /screenshot again to confirm operation results
5. If task not complete, go back to step 2 and continue

【Notes】
• Screenshot has about 100-200ms processing delay, wait a moment after operation before taking another screenshot
• Double-click is usually used to open files/folders
• Right-click will pop up context menu, need to take another screenshot to see menu content
• For large text transfer, use clipboard (POST /session/clipboard) instead of typing character by character
• Some operations may trigger Windows UAC dialog, which will appear in screenshot and need special handling

【Error Handling】
• 401 UNAUTHORIZED — Please check if API key is correct
• 400 INVALID_PARAMETER — Check request parameter format and value range
• 500 SCREEN_CAPTURE_FAILED — Screenshot failed, possibly disconnected monitor, please retry later
• 500 INPUT_FAILED — Input simulation failed, possibly target window closed

=== Manual End ==="""
    
    def start(self):
        """启动服务器"""
        host = self.config.get("server", {}).get("host", "0.0.0.0")
        port = self.config.get("server", {}).get("port", 8765)
        
        logger.info(f"启动API服务器: {host}:{port}")
        
        # 创建uvicorn配置
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=False
        )
        
        # 创建服务器实例
        self.server = uvicorn.Server(config)
        
        # 运行服务器
        self.server.run()
    
    def stop(self):
        """停止服务器"""
        if self.server:
            logger.info("正在停止API服务器...")
            self.server.should_exit = True