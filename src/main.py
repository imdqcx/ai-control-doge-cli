"""
AI Doge Remote - 主入口
初始化所有模块并启动服务
"""

import sys
import os
import io

# 打包后 --windowed 模式下 stdout/stderr 可能为 None
if sys.stdout is None:
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
if sys.stderr is None:
    sys.stderr = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')

# 打包后支持：将src目录加入sys.path
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    src_dir = os.path.join(base_dir, 'src')
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)
    else:
        sys.path.insert(0, base_dir)
else:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time

from src.config import ConfigManager, get_config_path
from src.server import APIServer
from src.tray import SystemTray
from src.logger import setup_logging, get_logger

# 全局变量
config_manager: ConfigManager = None
api_server: APIServer = None
system_tray: SystemTray = None
logger = None

# 标志位：是否需要显示设置界面
_need_show_settings = False
_root = None


def cleanup():
    global api_server, system_tray
    if api_server:
        api_server.stop()
    if system_tray:
        system_tray.stop()


def on_settings_save(config: dict):
    global config_manager, api_server
    config_manager.save(config)
    if api_server:
        api_server.stop()
        time.sleep(1)  # 等待旧服务释放端口
    api_server = APIServer(config)
    server_thread = threading.Thread(target=api_server.start, daemon=True)
    server_thread.start()


def on_exit():
    cleanup()
    os._exit(0)


def on_settings_click():
    global _need_show_settings
    _need_show_settings = True


def check_settings(root):
    global _need_show_settings
    if _need_show_settings:
        _need_show_settings = False
        show_settings_window(root)
    root.after(100, check_settings, root)


def show_settings_window(root):
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        config = config_manager.config if config_manager else {}
        
        win = tk.Toplevel(root)
        win.title("AI Doge Remote - 设置")
        win.geometry("690x780")
        win.resizable(True, True)
        win.attributes('-topmost', True)
        
        # 先显示窗口
        win.deiconify()
        win.update()
        
        # 延迟设置图标
        def set_window_icon():
            try:
                import ctypes
                if getattr(sys, 'frozen', False):
                    icon_path = os.path.join(os.path.dirname(sys.executable), 'assets', 'doge.ico')
                else:
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'doge.ico')
                if os.path.exists(icon_path):
                    hicon = ctypes.windll.user32.LoadImageW(0, str(icon_path), 1, 0, 0, 0x00000010)
                    if hicon:
                        hwnd = ctypes.windll.user32.FindWindowW(None, "AI Doge Remote - 设置")
                        if hwnd:
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)
            except Exception:
                pass
        win.after(300, set_window_icon)
        
        # DPI适配
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        
        # 主框架（带滚动条）
        main_frame = ttk.Frame(win)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="20")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # 鼠标滚轮
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        
        main_frame = scrollable_frame
        
        # 服务器设置
        server_frame = ttk.LabelFrame(main_frame, text="服务器设置", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_frame, text="监听端口:").grid(row=0, column=0, sticky=tk.W, pady=5)
        port_var = tk.StringVar(value=str(config.get("server", {}).get("port", 8765)))
        ttk.Entry(server_frame, textvariable=port_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(server_frame, text="监听地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        host_var = tk.StringVar(value=config.get("server", {}).get("host", "0.0.0.0"))
        ttk.Entry(server_frame, textvariable=host_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(server_frame, text="(留空或 0.0.0.0 表示所有网卡)").grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # 截图设置
        capture_frame = ttk.LabelFrame(main_frame, text="截图设置", padding="10")
        capture_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(capture_frame, text="截图格式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        format_var = tk.StringVar(value=config.get("capture", {}).get("format", "jpeg"))
        fmt_frame = ttk.Frame(capture_frame)
        fmt_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(fmt_frame, text="PNG", variable=format_var, value="png").pack(side=tk.LEFT)
        ttk.Radiobutton(fmt_frame, text="JPEG", variable=format_var, value="jpeg").pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(capture_frame, text="JPEG 质量:").grid(row=1, column=0, sticky=tk.W, pady=5)
        quality_var = tk.IntVar(value=config.get("capture", {}).get("quality", 80))
        quality_frame = ttk.Frame(capture_frame)
        quality_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Scale(quality_frame, from_=1, to=100, variable=quality_var, orient=tk.HORIZONTAL, length=200).pack(side=tk.LEFT)
        ttk.Label(quality_frame, textvariable=quality_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # 安全设置
        security_frame = ttk.LabelFrame(main_frame, text="安全设置", padding="10")
        security_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(security_frame, text="API 密钥:").grid(row=0, column=0, sticky=tk.W, pady=5)
        key_var = tk.StringVar(value=config.get("security", {}).get("api_key", ""))
        key_frame = ttk.Frame(security_frame)
        key_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        key_entry = ttk.Entry(key_frame, textvariable=key_var, width=30, show="*")
        key_entry.pack(side=tk.LEFT)
        show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(key_frame, text="显示", variable=show_var, 
                        command=lambda: key_entry.configure(show="" if show_var.get() else "*")).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(security_frame, text="(为空则不需要认证)").grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        notify_var = tk.BooleanVar(value=config.get("security", {}).get("notify_on_connect", True))
        ttk.Checkbutton(security_frame, text="启用连接时通知", variable=notify_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 关于
        about_frame = ttk.LabelFrame(main_frame, text="关于", padding="10")
        about_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(about_frame, text="版本: 1.0.0").pack(anchor=tk.W)
        port = config.get("server", {}).get("port", 8765)
        ttk.Label(about_frame, text=f"API 文档: http://localhost:{port}/docs").pack(anchor=tk.W)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        def on_save():
            try:
                port = int(port_var.get())
                if not (1024 <= port <= 65535):
                    messagebox.showerror("错误", "端口必须在 1024-65535 之间")
                    return
                new_config = {
                    "server": {"host": host_var.get(), "port": port},
                    "capture": {"format": format_var.get(), "quality": int(quality_var.get()), 
                               "max_width": 1920, "max_height": 1080},
                    "security": {"api_key": key_var.get(), "notify_on_connect": notify_var.get()}
                }
                on_settings_save(new_config)
                win.destroy()
                messagebox.showinfo("成功", f"配置已保存，服务将在端口 {port} 重启")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
        
        ttk.Button(btn_frame, text="保存", command=on_save).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="取消", command=win.destroy).pack(side=tk.RIGHT)
        
        # 居中
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
        y = (win.winfo_screenheight() // 2) - (win.winfo_height() // 2)
        win.geometry(f'+{x}+{y}')
        
    except Exception as e:
        if logger:
            logger.error(f"显示设置窗口异常: {e}")


def main():
    global config_manager, api_server, system_tray, logger, _root
    
    setup_logging()
    logger = get_logger(__name__)
    
    config_path = get_config_path()
    logger.info(f"配置路径: {config_path}")
    
    config_manager = ConfigManager(config_path)
    config = config_manager.load()
    
    server_config = config.get("server", {})
    port = server_config.get("port", 8765)
    host = server_config.get("host", "0.0.0.0")
    
    logger.info(f"服务器配置: {host}:{port}")
    
    api_server = APIServer(config)
    
    system_tray = SystemTray(
        config=config,
        on_settings=on_settings_click,
        on_exit=on_exit
    )
    
    system_tray.start()
    
    def start_server():
        try:
            logger.info(f"正在启动HTTP服务器 {host}:{port}...")
            api_server.start()
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(1)
    
    system_tray.update_status("运行中", port)
    
    logger.info("AI Doge Remote 已启动")
    
    # 创建隐藏的tkinter根窗口
    import tkinter as tk
    _root = tk.Tk()
    _root.withdraw()
    
    _root.after(100, check_settings, _root)
    
    try:
        _root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
