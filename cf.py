import sys, os, subprocess, threading, re, webbrowser, shutil, time
import tkinter as tk
from tkinter import messagebox, ttk

def get_cf_executable():
    arch_str = os.environ.get("PROCESSOR_ARCHITECTURE", "x86").upper()
    wow64_arch = os.environ.get("PROCESSOR_ARCHITEW6432", "").upper()
    is_64bit = (arch_str == "AMD64" or wow64_arch == "AMD64")
    target_exe = "cloudflared64.exe" if is_64bit else "cloudflared32.exe"
    base_dir = os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(base_dir, target_exe)
    if not os.path.exists(local_path) and hasattr(sys, '_MEIPASS'):
        bundled_path = os.path.join(sys._MEIPASS, target_exe)
        if os.path.exists(bundled_path):
            try: shutil.copy2(bundled_path, local_path)
            except: pass
    return local_path, "x64" if is_64bit else "x86"

class CloudflareGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloudflare Tunnel 快捷工具")
        self.root.geometry("560x540")
        self.root.configure(bg="#f5f5f7") # 苹果风浅灰色背景
        
        self.cf_exe, self.arch = get_cf_executable()
        self.process = None
        
        self.setup_styles()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # 全局背景
        style.configure("TFrame", background="#f5f5f7")
        # 标签区
        style.configure("TLabelframe", background="#f5f5f7", font=('微软雅黑', 10, 'bold'))
        style.configure("TLabelframe.Label", background="#f5f5f7", foreground="#333333")
        # 按钮样式
        style.configure("TButton", font=('微软雅黑', 9))
        style.configure("Accent.TButton", font=('微软雅黑', 10, 'bold'), foreground="#ffffff", background="#007aff")
        style.map("Accent.TButton", background=[('active', '#0062cc'), ('disabled', '#cccccc')])

    def create_widgets(self):
        # 顶部状态条
        status_bar = tk.Frame(self.root, bg="#ffffff", height=30, bd=1, relief="groove")
        status_bar.pack(fill="x", side="top")
        tk.Label(status_bar, text=f"系统架构: {self.arch} | 内核: {os.path.basename(self.cf_exe)}", 
                 bg="#ffffff", fg="#666666", font=('微软雅黑', 9)).pack(side="left", padx=15)

        # 1. 端口设置
        config_frame = ttk.Labelframe(self.root, text=" 1. 基础配置 ")
        config_frame.pack(fill="x", padx=20, pady=10)
        
        input_inner = tk.Frame(config_frame, bg="#f5f5f7")
        input_inner.pack(padx=10, pady=15)
        
        tk.Label(input_inner, text="映射端口:", bg="#f5f5f7", font=('微软雅黑', 10)).pack(side="left")
        self.port_entry = tk.Entry(input_inner, width=8, font=("Consolas", 14), bd=2, relief="flat", justify="center")
        self.port_entry.insert(0, "8000")
        self.port_entry.pack(side="left", padx=10)
        tk.Label(input_inner, text="( 映射至 http://127.0.0.1 )", bg="#f5f5f7", fg="#999").pack(side="left")

        # 2. 控制区
        ctrl_frame = tk.Frame(self.root, bg="#f5f5f7")
        ctrl_frame.pack(pady=5)
        self.start_btn = ttk.Button(ctrl_frame, text=" 开启穿透隧道 ", style="Accent.TButton", command=self.start_tunnel)
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn = ttk.Button(ctrl_frame, text=" 停止并清理 ", command=self.stop_tunnel, state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        # 3. 核心结果显示区 (加重显示)
        result_frame = ttk.Labelframe(self.root, text=" 2. 公网访问地址 ")
        result_frame.pack(fill="x", padx=20, pady=10)
        
        self.address_display = tk.Entry(result_frame, font=("Consolas", 14, "bold"), 
                                        bg="#ffffff", fg="#d35400", # 橙红色域名显示
                                        bd=0, justify="center")
        self.address_display.pack(fill="x", padx=20, pady=20)
        
        self.open_btn = ttk.Button(result_frame, text=" 点击在浏览器中直接打开 ", command=self.open_browser, state="disabled")
        self.open_btn.pack(pady=5)

        # 4. 日志显示区
        log_frame = ttk.Labelframe(self.root, text=" 3. 运行日志 ")
        log_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        self.log_text = tk.Text(log_frame, bg="#ffffff", fg="#333333", font=("Consolas", 9), 
                                wrap="none", bd=1, relief="flat", padx=5, pady=5)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def start_tunnel(self):
        port = self.port_entry.get().strip()
        if not port.isdigit():
            messagebox.showwarning("提示", "请输入有效的端口数字")
            return
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.address_display.delete(0, tk.END)
        self.address_display.insert(0, "正在获取域名...")
        self.log(f"--- 启动映射: 127.0.0.1:{port} ---")
        threading.Thread(target=self.run_process, args=(f"http://127.0.0.1:{port}",), daemon=True).start()

    def run_process(self, target_url):
        cmd = [self.cf_exe, "tunnel", "--url", target_url]
        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW,
                encoding='utf-8', errors='replace'
            )
            for line in self.process.stdout:
                line_content = line.strip()
                if line_content: self.log(line_content)
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if match:
                    self.root.after(0, self.update_address, match.group(0))
        except Exception as e:
            self.root.after(0, self.log, f"内核启动失败: {str(e)}")

    def update_address(self, url):
        self.address_display.delete(0, tk.END)
        self.address_display.insert(0, url)
        self.address_display.config(fg="#007aff") # 获取成功后变蓝色
        self.open_btn.config(state="normal")

    def open_browser(self):
        webbrowser.open(self.address_display.get())

    def stop_tunnel(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        self.log("--- 隧道已关闭 ---")
        if os.path.exists(self.cf_exe):
            try: 
                time.sleep(0.5)
                os.remove(self.cf_exe)
                self.log("内核文件已清理。")
            except: pass
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.open_btn.config(state="disabled")
        self.address_display.delete(0, tk.END)

    def on_closing(self):
        if self.process: self.process.terminate()
        if os.path.exists(self.cf_exe):
            try: os.remove(self.cf_exe)
            except: pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CloudflareGUI(root)
    root.mainloop()