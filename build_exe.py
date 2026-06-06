
"""
调货助手自动打包脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("      调货助手 - 自动打包工具")
    print("=" * 60)
    print()
    
    # 检查当前目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # 检查是否有 PyInstaller
    print("[1/4] 检查打包工具...")
    try:
        import PyInstaller
        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "pyinstaller-hooks-contrib"])
    
    # 清理旧的打包文件
    print("\n[2/4] 清理旧文件...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
            print(f"已删除 {folder}/")
    
    # 打包命令
    print("\n[3/4] 开始打包 (这可能需要几分钟)...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "调货助手 v1.03",
        "--hidden-import", "PyQt6",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "openpyxl",
        "--hidden-import", "docx",
        "--hidden-import", "PIL",
        "run.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print("打包成功!")
    except subprocess.CalledProcessError as e:
        print(f"\n打包出错:")
        print(e.stderr or e.stdout)
        print("\n尝试升级 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller", "pyinstaller-hooks-contrib"])
        print("请重新运行此脚本。")
        return
    
    # 完成
    print("\n[4/4] 完成!")
    print("=" * 60)
    
    exe_path = project_dir / "dist" / "调货助手 v1.03.exe"
    if exe_path.exists():
        print(f"EXE 文件已生成: {exe_path}")
        print(f"  文件大小: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        print("\n你可以直接运行这个 EXE 文件，或者复制到其他电脑使用。")
    else:
        print("请检查 dist 文件夹。")

if __name__ == "__main__":
    main()

