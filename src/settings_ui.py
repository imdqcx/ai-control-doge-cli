"""
设置界面模块
提供GUI设置界面，配置编辑
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any
import threading


class SettingsUI:
    """设置界面"""
    
    # 类级别的根窗口（确保只有一个）
    _root: tk.Tk = None
    _root_lock = threading.Lock()
    
    def __init__(self, 
                 config: Dict[str, Any], 
                 on_save: Callable, 
                 on_cancel: Callable):
        """
        初始化设置界面
        
        Args:
            config: 配置字典
            on_save: 保存回调函数
            on_cancel: 取消回调函数
        """
        self.config = config.copy()
        self.on_save = on_save
        self.on_cancel = on_cancel
        
        self.window: tk.Toplevel = None
        self.entries: Dict[str, tk.Entry] = {}
        self.vars: Dict[str, tk.Variable] = {}
        
        # 确保根窗口存在
        self._ensure_root()
    
    @classmethod
    def _ensure_root(cls):
        """确保Tk根窗口存在"""
        with cls._root_lock:
            if cls._root is None:
                cls._root = tk.Tk()
                cls._root.withdraw()  # 隐藏根窗口
    
    def show(self):
        """显示设置界面"""
        if self.window is not None:
            try:
                self.window.deiconify()  # 还原窗口
                self.window.lift()  # 提升到顶层
                self.window.attributes('-topmost', True)  # 置顶
                self.window.focus_force()  # 强制焦点
                return
            except Exception:
                # 窗口已销毁，重新创建
                self.window = None
        
        try:
            self.window = tk.Toplevel(self._root)
            self.window.title("AI Doge Remote - 设置")
            self.window.geometry("500x600")
            self.window.resizable(False, False)
            
            # 创建界面
            self._create_widgets()
            
            # 设置关闭事件
            self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
            
            # 置顶显示
            self.window.attributes('-topmost', True)
            
            # 居中显示
            self._center_window()
            
            # 强制显示和焦点
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            
            # 延迟再次置顶（确保不被其他窗口挡住）
            self.window.after(100, lambda: self.window.attributes('-topmost', True))
        except Exception as e:
            print(f"设置界面启动失败: {e}")
    
    def hide(self):
        """隐藏设置界面"""
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config
    
    def _center_window(self):
        """窗口居中"""
        try:
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f'{width}x{height}+{x}+{y}')
        except Exception:
            pass
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 服务器设置
        server_frame = ttk.LabelFrame(main_frame, text="服务器设置", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 监听端口
        ttk.Label(server_frame, text="监听端口:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.vars["server.port"] = tk.StringVar(value=str(self.config.get("server", {}).get("port", 8765)))
        port_entry = ttk.Entry(server_frame, textvariable=self.vars["server.port"], width=20)
        port_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 监听地址
        ttk.Label(server_frame, text="监听地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.vars["server.host"] = tk.StringVar(value=self.config.get("server", {}).get("host", "0.0.0.0"))
        host_entry = ttk.Entry(server_frame, textvariable=self.vars["server.host"], width=20)
        host_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(server_frame, text="(留空或 0.0.0.0 表示所有网卡)").grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # 截图设置
        capture_frame = ttk.LabelFrame(main_frame, text="截图设置", padding="10")
        capture_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 截图格式
        ttk.Label(capture_frame, text="截图格式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.vars["capture.format"] = tk.StringVar(value=self.config.get("capture", {}).get("format", "jpeg"))
        
        format_frame = ttk.Frame(capture_frame)
        format_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(format_frame, text="PNG", variable=self.vars["capture.format"], value="png").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.vars["capture.format"], value="jpeg").pack(side=tk.LEFT, padx=(10, 0))
        
        # JPEG质量
        ttk.Label(capture_frame, text="JPEG 质量:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.vars["capture.quality"] = tk.StringVar(value=str(self.config.get("capture", {}).get("quality", 80)))
        
        quality_frame = ttk.Frame(capture_frame)
        quality_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        quality_scale = ttk.Scale(quality_frame, from_=1, to=100, variable=self.vars["capture.quality"], orient=tk.HORIZONTAL, length=200)
        quality_scale.pack(side=tk.LEFT)
        
        quality_label = ttk.Label(quality_frame, textvariable=self.vars["capture.quality"])
        quality_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 安全设置
        security_frame = ttk.LabelFrame(main_frame, text="安全设置", padding="10")
        security_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API密钥
        ttk.Label(security_frame, text="API 密钥:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.vars["security.api_key"] = tk.StringVar(value=self.config.get("security", {}).get("api_key", ""))
        
        key_frame = ttk.Frame(security_frame)
        key_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        key_entry = ttk.Entry(key_frame, textvariable=self.vars["security.api_key"], width=30, show="*")
        key_entry.pack(side=tk.LEFT)
        
        self.show_key_var = tk.BooleanVar(value=False)
        show_key_check = ttk.Checkbutton(key_frame, text="显示", variable=self.show_key_var, 
                                         command=lambda: key_entry.configure(show="" if self.show_key_var.get() else "*"))
        show_key_check.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(security_frame, text="(为空则不需要认证)").grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        # 连接通知
        self.vars["security.notify_on_connect"] = tk.BooleanVar(value=self.config.get("security", {}).get("notify_on_connect", True))
        notify_check = ttk.Checkbutton(security_frame, text="启用连接时通知", variable=self.vars["security.notify_on_connect"])
        notify_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 关于
        about_frame = ttk.LabelFrame(main_frame, text="关于", padding="10")
        about_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(about_frame, text="版本: 1.0.0").pack(anchor=tk.W)
        ttk.Label(about_frame, text="API 文档: http://localhost:8765/docs").pack(anchor=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="保存", command=self._on_save).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self._on_cancel).pack(side=tk.RIGHT)
    
    def _on_save(self):
        """保存按钮点击"""
        try:
            # 验证端口
            port = int(self.vars["server.port"].get())
            if not (1024 <= port <= 65535):
                messagebox.showerror("错误", "端口必须在 1024-65535 之间")
                return
            
            # 验证质量
            quality = int(float(self.vars["capture.quality"].get()))
            if not (1 <= quality <= 100):
                messagebox.showerror("错误", "JPEG质量必须在 1-100 之间")
                return
            
            # 更新配置
            self.config["server"]["port"] = port
            self.config["server"]["host"] = self.vars["server.host"].get()
            self.config["capture"]["format"] = self.vars["capture.format"].get()
            self.config["capture"]["quality"] = quality
            self.config["security"]["api_key"] = self.vars["security.api_key"].get()
            self.config["security"]["notify_on_connect"] = self.vars["security.notify_on_connect"].get()
            
            # 调用保存回调
            if self.on_save:
                self.on_save(self.config)
            
            # 关闭窗口
            self.hide()
            
            messagebox.showinfo("成功", "配置已保存，服务器将重启")
            
        except ValueError as e:
            messagebox.showerror("错误", f"请输入有效的数字: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def _on_cancel(self):
        """取消按钮点击"""
        if self.on_cancel:
            self.on_cancel()
        self.hide()
