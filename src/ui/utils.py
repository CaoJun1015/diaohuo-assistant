"""工具函数"""
import os
import sys
import re
import traceback
from datetime import datetime


def _validate_date(date_str):
    """校验日期格式为 YYYY-MM-DD，返回 (is_valid, error_message)"""
    if not date_str:
        return False, "日期不能为空"
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str):
        return False, f"日期格式错误: {date_str}，应为 YYYY-MM-DD"
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, f"无效日期: {date_str}"


def _global_excepthook(exc_type, exc_value, exc_tb):
    """全局异常钩子：将未捕获异常写入 crash.log 并显示错误对话框"""
    from PyQt6.QtWidgets import QMessageBox
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    crash_msg = "".join(tb_lines)
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "crash.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CRASH\n")
            f.write(crash_msg)
    except Exception:
        print(crash_msg, file=sys.stderr)
    QMessageBox.critical(
        None, "程序异常",
        f"程序发生未处理的异常:\n\n{exc_value}\n\n详细信息已写入 crash.log"
    )