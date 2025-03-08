# 主文件
# 作者: @awa_boy 
# 版本: 1.0.0
# 更新时间: 2025-03-08
#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
ModuKit - 模块化工具箱
主程序入口文件，负责初始化PyWebView窗口和Flask后端服务
"""

import os
import sys
import argparse
import threading
import webview
import logging
from pathlib import Path
from datetime import datetime

# 设置项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(ROOT_DIR / "logs" / f"modukit_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ModuKit")

# 导入后端模块
sys.path.append(str(ROOT_DIR))
from backend.server import create_app
from backend.config_loader import ConfigLoader

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="ModuKit - 模块化工具箱")
    parser.add_argument("--port", type=int, default=5000, help="Flask服务端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--config", type=str, default=str(ROOT_DIR / "config" / "default.ini"), 
                        help="配置文件路径")
    return parser.parse_args()

def start_server(port, debug):
    """在单独线程中启动Flask服务器"""
    app = create_app(debug=debug)
    
    if debug:
        # 开发模式使用Flask内置服务器
        app.run(port=port, debug=True, use_reloader=False)
    else:
        # 生产模式使用waitress
        from waitress import serve
        serve(app, host="127.0.0.1", port=port)

def create_window(config, debug, server_port):
    """创建PyWebView窗口"""
    # 从配置中读取窗口设置
    window_title = config.get("window", "title", fallback="ModuKit - 模块化工具箱")
    window_width = config.getint("window", "width", fallback=1024)
    window_height = config.getint("window", "height", fallback=768)
    window_resizable = config.getboolean("window", "resizable", fallback=True)
    window_fullscreen = config.getboolean("window", "fullscreen", fallback=False)
    
    # 创建窗口
    window = webview.create_window(
        title=window_title,
        url=f"http://localhost:{server_port}",
        width=window_width,
        height=window_height,
        resizable=window_resizable,
        fullscreen=window_fullscreen,
        min_size=(800, 600),
        text_select=debug,  # 调试模式允许文本选择
        confirm_close=True
    )
    
    # 设置窗口关闭事件处理
    window.events.closed += on_window_close
    
    return window

def on_window_close():
    """窗口关闭事件处理"""
    logger.info("窗口已关闭，正在保存状态...")
    # 这里可以添加保存窗口状态的代码
    sys.exit(0)

def setup_tray(window):
    """设置系统托盘菜单"""
    if not webview.platforms.gtk.is_gtk:  # GTK平台不支持托盘
        tray_menu = [
            ('显示窗口', lambda: window.show()),
            ('隐藏窗口', lambda: window.hide()),
            webview.menu.MenuSeparator(),
            ('退出', lambda: window.destroy())
        ]
        webview.menu.create_tray_menu(tray_menu, "ModuKit")

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 确保配置目录存在
    config_dir = Path(args.config).parent
    config_dir.mkdir(exist_ok=True, parents=True)
    
    # 加载配置
    config_loader = ConfigLoader(args.config)
    config = config_loader.get_config()
    
    # 启动Flask服务器
    server_thread = threading.Thread(
        target=start_server,
        args=(args.port, args.debug),
        daemon=True
    )
    server_thread.start()
    
    # 创建窗口
    logger.info(f"正在启动ModuKit，端口: {args.port}, 调试模式: {args.debug}")
    window = create_window(config, args.debug, args.port)
    
    # 设置系统托盘
    setup_tray(window)
    
    # 启动GUI
    webview.start(debug=args.debug, gui="default")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 记录崩溃日志
        crash_log_path = ROOT_DIR / "logs" / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(crash_log_path, "w", encoding="utf-8") as f:
            import traceback
            f.write(f"ModuKit崩溃时间: {datetime.now()}\n")
            f.write(f"错误信息: {str(e)}\n")
            f.write(traceback.format_exc())
        logger.critical(f"程序崩溃: {str(e)}")
        sys.exit(1)



