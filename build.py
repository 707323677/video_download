"""
打包脚本 - 将B站视频下载工具打包成可执行文件

使用方法:
    python build.py          # 打包Windows exe
    python build.py clean    # 清理构建文件
"""
import sys
import shutil
import subprocess
from pathlib import Path


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent


def check_dependencies():
    """检查打包工具是否安装"""
    try:
        import PyInstaller
        print("[OK] PyInstaller 已安装")
        return True
    except ImportError:
        print("[ERR] PyInstaller 未安装")
        print("请运行以下命令安装:")
        print("    pip install pyinstaller")
        return False


def install_dependencies():
    """安装打包依赖"""
    print("📦 正在安装 PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✅ PyInstaller 安装完成")


def clean():
    """清理构建文件"""
    root = get_project_root()
    
    patterns = [
        "build",
        "dist",
        "*.spec",
        "__pycache__",
    ]
    
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_dir():
                print(f"🗑️  删除目录: {path}")
                shutil.rmtree(path)
            else:
                print(f"🗑️  删除文件: {path}")
                path.unlink()
    
    print("✅ 清理完成")


def build_windows():
    """打包Windows可执行文件"""
    root = get_project_root()
    
    print("=" * 50)
    print("🔨 开始打包 Windows 可执行文件")
    print("=" * 50)
    
    # 入口脚本路径
    main_script = root / "src" / "videos_download" / "main.py"
    
    # 输出目录
    dist_dir = root / "dist"
    
    # PyInstaller 命令参数
    args = [
        sys.executable, "-m", "PyInstaller",
        "--name=B站视频下载工具",
        "--onedir",  # 输出为目录形式（包含dll和依赖）
        # "--onefile",  # 取消注释可输出单个exe文件（但较大）
        f"--distpath={dist_dir}",
        f"--workpath={root / 'build'}",
        f"--specpath={root}",
        "--clean",
        # 窗口模式（不显示控制台窗口）
        "--windowed",
        "--add-data", f"{root / 'executables'}{';' if sys.platform == 'win32' else ':'}executables",
        "--icon=NONE",  # 可替换为图标文件路径
        "--noconfirm",  # 不询问确认，直接覆盖
        str(main_script),
    ]
    
    print(f"📂 主脚本: {main_script}")
    print(f"📂 输出目录: {dist_dir}")
    print()
    
    # 执行打包
    print("⏳ 正在打包，请稍候...")
    result = subprocess.run(args, capture_output=False)
    
    if result.returncode == 0:
        print()
        print("=" * 50)
        print("✅ 打包成功!")
        print("=" * 50)
        print(f"📦 输出目录: {dist_dir / 'B站视频下载工具'}")
        print()
        print("运行方式:")
        print(f"    {dist_dir / 'B站视频下载工具' / 'B站视频下载工具.exe'}")
        print()
        
        # 复制ffmpeg到输出目录
        exe_dir = dist_dir / "B站视频下载工具"
        ffmpeg_src = root / "executables" / "ffmpeg.exe"
        ffmpeg_dst = exe_dir / "executables" / "ffmpeg.exe"
        
        if ffmpeg_src.exists():
            ffmpeg_dst.parent.mkdir(exist_ok=True)
            shutil.copy2(ffmpeg_src, ffmpeg_dst)
            print("📋 已复制 ffmpeg.exe 到输出目录")
        
        print("=" * 50)
    else:
        print()
        print("=" * 50)
        print("❌ 打包失败!")
        print("=" * 50)
        sys.exit(1)


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean()
        return
    
    if not check_dependencies():
        response = input("\n是否自动安装 PyInstaller? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
        else:
            print("打包取消")
            sys.exit(0)
    
    build_windows()


if __name__ == "__main__":
    main()
