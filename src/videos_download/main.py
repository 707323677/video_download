"""
B站视频下载工具
简化版 - 手动输入Cookie方式
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import yt_dlp
from pathlib import Path


def get_project_root():
    """获取项目根目录路径"""
    return Path(__file__).parent.parent.parent


class VideoDownloaderApp:
    """视频下载器主应用类"""
    
    def __init__(self, root):
        """初始化应用"""
        self.root = root
        self.root.title("B站视频下载工具")
        self.root.geometry("850x600")
        
        self.video_list = []
        self.download_thread = None
        self.cookies = {}  # 存储用户输入的Cookie
        
        self.show_url_input()
    
    def show_url_input(self):
        """显示视频地址和Cookie输入界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(frame, text="B站视频下载工具", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # 视频地址
        ttk.Label(frame, text="视频地址:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        self.url_entry = ttk.Entry(frame, width=80, font=('Arial', 11))
        self.url_entry.pack(fill=tk.X, pady=(0, 5))
        self.url_entry.insert(0, "https://space.bilibili.com/33291981/lists/525129?type=season")
        
        ttk.Label(
            frame,
            text="支持: 视频链接、合集链接、收藏夹链接",
            font=('Arial', 10), foreground='gray'
        ).pack(anchor='w', pady=(0, 15))
        
        # Cookie输入区域
        cookie_frame = ttk.LabelFrame(frame, text="B站登录Cookie（必须）", padding="12")
        cookie_frame.pack(fill=tk.X, pady=(0, 15))
        
        # SESSDATA输入框
        sdata_frame = ttk.Frame(cookie_frame)
        sdata_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(sdata_frame, text="SESSDATA:", font=('Arial', 11), width=12).pack(side=tk.LEFT)
        self.sessdata_entry = ttk.Entry(sdata_frame, width=65, font=('Consolas', 10))
        self.sessdata_entry.pack(side=tk.LEFT)
        
        # bili_jct输入框
        bjct_frame = ttk.Frame(cookie_frame)
        bjct_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(bjct_frame, text="bili_jct:", font=('Arial', 11), width=12).pack(side=tk.LEFT)
        self.bili_jct_entry = ttk.Entry(bjct_frame, width=65, font=('Consolas', 10))
        self.bili_jct_entry.pack(side=tk.LEFT)
        
        # 提示文字
        ttk.Label(
            cookie_frame,
            text="💡 只需复制浏览器中Cookie的值粘贴到对应输入框即可",
            font=('Arial', 9), foreground='orange'
        ).pack(anchor='w', pady=(0, 10))
        
        # 获取Cookie教程按钮
        ttk.Button(
            cookie_frame,
            text="点击查看：如何获取Cookie值",
            command=self.show_cookie_tutorial,
            style='Info.TButton'
        ).pack(anchor='w')
        
        # 按钮区域
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(20, 0))
        
        ttk.Button(btn_frame, text="获取视频列表", command=self.fetch_video_list, width=22).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="退出", command=self.root.quit, width=15).pack(side=tk.LEFT, padx=5)
    
    def show_cookie_tutorial(self):
        """显示获取Cookie的详细教程"""
        tutorial = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   如何获取B站Cookie值
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 方法：使用浏览器开发者工具

1. 打开浏览器（Chrome/Edge/Firefox），登录B站
2. 在B站页面按 F12 打开开发者工具
3. 切换到「Application」或「存储」标签页
4. 在左侧找到「Cookies」→「https://www.bilibili.com」
5. 找到以下两个Cookie，**只复制值（Value列）**：
   ├── SESSDATA → 复制右侧Value列的内容
   └── bili_jct → 复制右侧Value列的内容

⚠️ 重要提示：
• 只复制值，不要复制名称（Name列）
• Cookie有效期约1个月，过期后需要重新获取
• Cookie包含个人登录信息，请妥善保管，不要泄露

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            示例（假设您获取到这样的值）：
SESSDATA值: abc123xyz789...（约64个字符）
bili_jct值: 456def000...（32个字符的十六进制）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        # 创建新窗口显示教程
        tutorial_win = tk.Toplevel(self.root)
        tutorial_win.title("获取Cookie值教程")
        tutorial_win.geometry("650x400")
        
        text = scrolledtext.ScrolledText(tutorial_win, font=('Consolas', 11), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, tutorial)
        text.config(state='disabled')
        
        ttk.Button(tutorial_win, text="我知道了", command=tutorial_win.destroy).pack(pady=10)
    
    def fetch_video_list(self):
        """获取视频列表"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入视频地址!")
            return
        
        # 从两个输入框获取Cookie值
        sessdata = self.sessdata_entry.get().strip()
        bili_jct = self.bili_jct_entry.get().strip()
        
        if not sessdata:
            messagebox.showwarning("警告", "请输入SESSDATA!\n点击'如何获取Cookie值'查看教程")
            return
        
        if not bili_jct:
            messagebox.showwarning("警告", "请输入bili_jct!\n点击'如何获取Cookie值'查看教程")
            return
        
        # 自动拼接成字典格式
        self.cookies = {
            'SESSDATA': sessdata,
            'bili_jct': bili_jct
        }
        
        # 显示加载界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="正在获取视频列表...", font=('Arial', 14)).pack(pady=20)
        
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        self.progress.start()
        
        threading.Thread(target=self._fetch_video_list_thread, args=(url,), daemon=True).start()
    
    def _fetch_video_list_thread(self, url):
        """后台线程获取视频列表"""
        try:
            ydl_opts = {
                'quiet': True,
                'cookies': self.cookies,
                'noplaylist': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=False)
                
                if 'entries' in result:
                    self.video_list = list(result['entries'])
                else:
                    self.video_list = [result]
                
                self.video_list = [v for v in self.video_list if v is not None]
                
                self.root.after(0, self.show_video_list)
        
        except Exception as exc:
            error_msg = str(exc)
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def show_error(self, error_msg):
        """显示错误界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="获取视频列表失败!", font=('Arial', 14), foreground='red').pack(pady=10)
        
        error_text = scrolledtext.ScrolledText(frame, height=12, font=('Consolas', 10))
        error_text.pack(fill=tk.BOTH, expand=True, pady=10)
        error_text.insert(tk.END, error_msg)
        error_text.config(state='disabled')
        
        tips = """
常见问题：
1. Cookie过期或错误 → 重新获取SESSDATA和bili_jct
2. 网络连接问题 → 检查网络
3. 视频链接无效 → 确认链接正确

建议：
• 确保SESSDATA和bili_jct都正确输入
• Cookie有效期约1个月，过期需重新获取
"""
        ttk.Label(frame, text=tips, font=('Arial', 10), foreground='gray', wraplength=750, justify='left').pack(pady=10)
        
        ttk.Button(frame, text="返回", command=self.show_url_input, width=15).pack(pady=10)
    
    def show_video_list(self):
        """显示视频列表界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text=f"✅ 共找到 {len(self.video_list)} 个视频",
            font=('Arial', 14, 'bold'), foreground='green'
        ).pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT, padx=3)
        
        # 可滚动列表
        container = ttk.Frame(main_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas = tk.Canvas(container, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        self.scroll_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        self.scroll_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # 视频列表
        self.check_vars = {}
        for idx, video in enumerate(self.video_list):
            video_frame = ttk.Frame(self.scroll_frame, padding=6)
            video_frame.pack(fill=tk.X, pady=3)
            video_frame.config(relief=tk.GROOVE, borderwidth=1)
            
            var = tk.BooleanVar()
            self.check_vars[idx] = var
            ttk.Checkbutton(video_frame, variable=var).pack(side=tk.LEFT, padx=8)
            
            title = video.get('title', f'视频 {idx+1}')
            duration = video.get('duration', 0)
            duration_str = self.format_duration(duration)
            url = video.get('url', '')
            
            info_frame = ttk.Frame(video_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            ttk.Label(info_frame, text=f"{idx+1}. {title}", font=('Arial', 11), wraplength=650).pack(anchor='w')
            
            detail_parts = []
            if duration_str != "未知":
                detail_parts.append(f"⏱️ 时长: {duration_str}")
            if url:
                bv = self._extract_bv(url)
                detail_parts.append(f"📺 BV: {bv}")
            
            if detail_parts:
                ttk.Label(
                    info_frame, text=" | ".join(detail_parts),
                    font=('Arial', 9), foreground='gray'
                ).pack(anchor='w')
        
        # 底部
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 质量选择
        ttk.Label(bottom_frame, text="📊 视频质量:").pack(side=tk.LEFT, padx=(0, 5))
        self.quality_var = tk.StringVar(value="best")
        quality_combo = ttk.Combobox(
            bottom_frame, textvariable=self.quality_var,
            width=15, state='readonly', font=('Arial', 10)
        )
        quality_combo['values'] = ('best', '1080p', '720p', '480p', '360p')
        quality_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 按钮
        ttk.Button(bottom_frame, text="⬅️ 返回", command=self.show_url_input).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="⬇️ 下载选中", command=self.start_download, width=15).pack(side=tk.RIGHT, padx=5)
    
    def _extract_bv(self, url):
        """从URL中提取BV号"""
        if 'BV' in url:
            start = url.find('BV')
            end = start + 12
            return url[start:end]
        return url[-12:] if len(url) > 12 else url
    
    def format_duration(self, seconds):
        """将秒数格式化为易读的时间字符串"""
        if not seconds:
            return "未知"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
    
    def select_all(self):
        """全选"""
        for var in self.check_vars.values():
            var.set(True)
    
    def deselect_all(self):
        """取消全选"""
        for var in self.check_vars.values():
            var.set(False)
    
    def start_download(self):
        """开始下载"""
        selected = []
        for idx, var in self.check_vars.items():
            if var.get():
                selected.append(self.video_list[idx])
        
        if not selected:
            messagebox.showwarning("警告", "请至少选择一个视频!")
            return
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="⏳ 正在下载视频...", font=('Arial', 14)).pack(pady=10)
        
        self.current_video_label = ttk.Label(main_frame, text="", font=('Arial', 11))
        self.current_video_label.pack(pady=5)
        
        self.download_progress = ttk.Progressbar(main_frame, mode='determinate')
        self.download_progress.pack(fill=tk.X, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, font=('Consolas', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.cancel_btn = ttk.Button(main_frame, text="❌ 取消下载", command=self.cancel_download)
        self.cancel_btn.pack(pady=10)
        
        self.download_cancelled = False
        self.download_thread = threading.Thread(
            target=self._download_thread,
            args=(selected, self.quality_var.get()),
            daemon=True
        )
        self.download_thread.start()
    
    def cancel_download(self):
        """取消下载"""
        self.download_cancelled = True
        self.cancel_btn.config(state='disabled')
        self.log("⏹️ 正在取消下载...")
    
    def _download_thread(self, videos, quality):
        """后台下载线程"""
        output_path = get_project_root() / "downloads"
        output_path.mkdir(exist_ok=True)
        
        quality_map = {
            'best': 'bestvideo+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        }
        
        ffmpeg_path = get_project_root() / "executables" / "ffmpeg.exe"
        
        ydl_opts = {
            'format': quality_map.get(quality, 'bestvideo+bestaudio/best'),
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),
            'cookies': self.cookies,
            'ffmpeg_location': str(ffmpeg_path) if ffmpeg_path.exists() else None,
            'progress_hooks': [self._progress_hook],
            'quiet': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for idx, video in enumerate(videos):
                    if self.download_cancelled:
                        break
                    
                    title = video.get('title', f'视频 {idx+1}')
                    video_url = video.get('url', '')
                    
                    if not video_url:
                        video_id = video.get('id', '')
                        if video_id:
                            video_url = f"https://www.bilibili.com/video/{video_id}"
                        else:
                            self.root.after(0, lambda t=title: self.log(f"⏭️ 跳过 {t}: 无法获取视频地址"))
                            continue
                    
                    self.root.after(0, lambda t=title: self.current_video_label.config(text=f"当前下载: {t}"))
                    self.root.after(0, lambda t=title: self.log(f"⬇️ 开始下载: {t}"))
                    
                    try:
                        ydl.download([video_url])
                        self.root.after(0, lambda t=title: self.log(f"✅ {t} 下载完成!"))
                    except Exception as exc:
                        self.root.after(0, lambda t=title, e=str(exc): self.log(f"❌ {t} 下载失败: {e}"))
                    
                    progress = ((idx + 1) / len(videos)) * 100
                    self.root.after(0, lambda p=progress: self.download_progress.config(value=p))
            
            if not self.download_cancelled:
                self.root.after(0, self.show_download_complete)
            else:
                self.root.after(0, lambda: self.log("⏹️ 下载已取消"))
        
        except Exception as exc:
            self.root.after(0, lambda: self.log(f"❌ 错误: {str(exc)}"))
    
    def _progress_hook(self, d):
        """下载进度回调"""
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = downloaded / total * 100
                speed = d.get('speed', 0)
                speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "未知速度"
                self.root.after(0, lambda p=percent, s=speed_str: self.log(f"  └─ 进度: {p:.1f}% | 速度: {s}"))
                self.root.after(0, lambda p=percent: self.download_progress.config(value=p))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.log("  └─ 下载完成，正在合并音视频..."))
    
    def log(self, message):
        """向日志文本框添加消息"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
    
    def show_download_complete(self):
        """显示下载完成提示"""
        messagebox.showinfo("🎉 完成", "视频下载完成!\n\n文件保存在项目根目录的 downloads 文件夹中")
        self.show_url_input()


def main():
    """主函数"""
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
