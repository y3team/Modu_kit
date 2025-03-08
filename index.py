# 主文件
# 作者: @awa_boy 
# 版本: 1.0.0
# 更新时间: 2025-03-08
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 需要安装的库:
# pip install -r requires.txt
# requires.txt内容:
# flask==2.0.1
# pywebview==3.6.3
# pathlib==1.0.1
# argparse==1.4.0
# python-dotenv==0.19.0
# requests==2.26.0
# werkzeug==2.0.1
# jinja2==3.0.1
# itsdangerous==2.0.1
# click==8.0.1
""" 
ModuKit - 模块化工具箱
主程序入口文件，负责初始化PyWebView窗口和Flask后端服务
"""

import os
import sys
import argparse
import threading
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
    parser.add_argument("--cli", action="store_true", help="使用命令行模式，不启动GUI")
    parser.add_argument("--gui", action="store_true", help="使用GUI模式，启动独立窗口")
    return parser.parse_args()

def start_server(port, debug):
    """在单独线程中启动Flask服务器"""
    app = create_app(debug=debug)
    
    if debug:
        # 开发模式使用Flask内置服务器
        app.run(port=port, debug=True, use_reloader=False)
    else:
        # 生产模式使用waitress
        try:
            from waitress import serve
            serve(app, host="127.0.0.1", port=port)
        except ImportError:
            logger.warning("未安装waitress，使用Flask内置服务器")
            app.run(port=port, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"启动服务器失败: {str(e)}")
            sys.exit(1)

def create_window(config, debug, server_port):
    """创建PyWebView窗口"""
    try:
        import webview
        logger.info("成功导入PyWebView")
        
        # 从配置中读取窗口设置
        window_config = config.get('window', {})
        window_title = window_config.get('title', 'ModuKit - 模块化工具箱')
        
        # 尝试将字符串转换为整数
        try:
            window_width = int(window_config.get('width', 1024))
        except (ValueError, TypeError):
            window_width = 1024
            
        try:
            window_height = int(window_config.get('height', 768))
        except (ValueError, TypeError):
            window_height = 768
        
        # 尝试将字符串转换为布尔值
        window_resizable_str = window_config.get('resizable', 'true').lower()
        window_resizable = window_resizable_str in ('true', 'yes', '1', 'on')
        
        window_fullscreen_str = window_config.get('fullscreen', 'false').lower()
        window_fullscreen = window_fullscreen_str in ('true', 'yes', '1', 'on')
        
        logger.info(f"创建窗口: {window_title}, 大小: {window_width}x{window_height}")
        
        # 创建API类，用于JavaScript和Python之间的通信
        class Api:
            def __init__(self):
                self.window = None
            
            def set_window(self, window):
                self.window = window
            
            def get_status(self):
                """获取服务器状态"""
                return {
                    'status': 'running',
                    'version': config.get('app', {}).get('version', '0.1.0')
                }
            
            def get_modules(self):
                """获取模块列表"""
                modules_str = config.get('modules', {}).get('enabled', '')
                modules = [m.strip() for m in modules_str.split(',') if m.strip()]
                return modules
            
            def show_notification(self, title, message, timeout=5):
                """显示通知"""
                try:
                    from plyer import notification
                    notification.notify(
                        title=title,
                        message=message,
                        timeout=timeout,
                        app_icon=str(ROOT_DIR / "static" / "logo.ico"),
                        app_name="ModuKit"
                    )
                    return True
                except Exception as e:
                    logger.error(f"显示通知失败: {str(e)}")
                    return False
        
        # 创建API实例
        api = Api()
        
        # 获取静态文件路径
        static_dir = ROOT_DIR / "static"
        index_path = static_dir / "index.html"
        icon_path = static_dir / "logo.ico"
        
        # 确保路径存在
        if not index_path.exists():
            logger.error(f"HTML文件不存在: {index_path}")
            return None
        
        # 将路径转换为绝对路径字符串
        index_path_str = str(index_path.absolute())
        icon_path_str = str(icon_path.absolute()) if icon_path.exists() else None
        
        logger.info(f"加载HTML文件: {index_path_str}")
        if icon_path_str:
            logger.info(f"使用图标: {icon_path_str}")
        
        # 创建窗口 - 直接加载本地HTML文件，而不是通过HTTP服务器
        window = webview.create_window(
            title=window_title,
            url=index_path_str,  # 直接使用本地文件路径
            width=window_width,
            height=window_height,
            resizable=window_resizable,
            fullscreen=window_fullscreen,
            min_size=(800, 600),
            text_select=debug,  # 调试模式允许文本选择
            confirm_close=True,
            js_api=api,  # 添加JavaScript API
            icon=icon_path_str  # 添加图标
        )
        
        # 设置API实例的window属性
        api.set_window(window)
        
        logger.info("窗口创建成功")
        
        # 设置窗口关闭事件处理
        window.events.closed += on_window_close
        
        return window
    except ImportError as e:
        logger.error(f"未安装pywebview，无法创建GUI窗口: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"创建窗口失败: {str(e)}")
        return None

def on_window_close():
    """窗口关闭事件处理"""
    logger.info("窗口已关闭，正在保存状态...")
    # 这里可以添加保存窗口状态的代码
    sys.exit(0)

def setup_tray(window):
    """设置系统托盘菜单"""
    try:
        import webview
        
        # 尝试创建托盘菜单
        if hasattr(webview, 'menu'):
            tray_menu = [
                ('显示窗口', lambda: window.show()),
                ('隐藏窗口', lambda: window.hide()),
                webview.menu.MenuSeparator(),
                ('退出', lambda: window.destroy())
            ]
            webview.menu.create_tray_menu(tray_menu, "ModuKit")
    except Exception as e:
        # 如果不支持托盘，记录日志但不中断程序
        logger.warning(f"无法创建系统托盘: {str(e)}")

def run_cli_mode(config, server_port):
    """运行命令行模式"""
    print(f"\n欢迎使用 ModuKit 命令行模式!")
    print(f"API服务器运行在 http://localhost:{server_port}")
    print("输入 'help' 获取帮助，输入 'exit' 退出程序")
    
    # 询问是否在浏览器中打开界面
    try:
        open_browser = input("是否在浏览器中打开界面? (y/n): ").strip().lower()
        if open_browser in ('y', 'yes', '是'):
            import webbrowser
            webbrowser.open(f"http://localhost:{server_port}")
            print(f"已在浏览器中打开 http://localhost:{server_port}")
    except Exception as e:
        print(f"无法打开浏览器: {str(e)}")
    
    while True:
        try:
            cmd = input("\nModuKit> ").strip()
            
            if cmd == "exit":
                print("感谢使用 ModuKit，再见!")
                break
            elif cmd == "help":
                print("\n可用命令:")
                print("  help       - 显示帮助信息")
                print("  status     - 显示服务器状态")
                print("  modules    - 列出可用模块")
                print("  open       - 在浏览器中打开界面")
                print("  exit       - 退出程序")
            elif cmd == "status":
                print(f"服务器状态: 运行中")
                print(f"地址: http://localhost:{server_port}")
                print(f"版本: {config.get('app', {}).get('version', '0.1.0')}")
            elif cmd == "modules":
                modules_str = config.get('modules', {}).get('enabled', '')
                modules = [m.strip() for m in modules_str.split(',') if m.strip()]
                if modules:
                    print("\n可用模块:")
                    for module in modules:
                        print(f"  - {module}")
                else:
                    print("没有可用模块")
            elif cmd == "open":
                try:
                    import webbrowser
                    webbrowser.open(f"http://localhost:{server_port}")
                    print(f"已在浏览器中打开 http://localhost:{server_port}")
                except Exception as e:
                    print(f"无法打开浏览器: {str(e)}")
            else:
                print("未知命令，输入 'help' 获取帮助")
        except KeyboardInterrupt:
            print("\n感谢使用 ModuKit，再见!")
            break
        except Exception as e:
            print(f"错误: {str(e)}")

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
    
    # 默认使用CLI模式，除非指定了--gui参数
    if args.gui:
        # GUI模式 - 使用PyWebView创建独立窗口
        try:
            import webview
            # 获取版本信息（安全方式）
            webview_version = getattr(webview, '__version__', '未知')
            logger.info(f"PyWebView版本: {webview_version}")
            
            # 显示启动通知
            try:
                from plyer import notification
                notification.notify(
                    title='ModuKit',
                    message='正在启动，请稍候...',
                    timeout=5,
                    app_icon=str(ROOT_DIR / "static" / "logo.ico"),
                    app_name="ModuKit"
                )
            except Exception as e:
                logger.warning(f"显示通知失败: {str(e)}")
            
            # 创建窗口
            window = create_window(config, args.debug, None)  # 不需要服务器端口
            
            if window:
                # 设置系统托盘
                setup_tray(window)
                
                # 启动GUI
                logger.info("启动PyWebView")
                webview.start(debug=args.debug)
            else:
                # 如果窗口创建失败，回退到CLI模式
                logger.warning("GUI窗口创建失败，回退到命令行模式")
                # 启动Flask服务器
                server_thread = threading.Thread(
                    target=start_server,
                    args=(args.port, args.debug),
                    daemon=True
                )
                server_thread.start()
                run_cli_mode(config, args.port)
        except ImportError as e:
            logger.warning(f"未安装pywebview，使用命令行模式: {str(e)}")
            # 启动Flask服务器
            server_thread = threading.Thread(
                target=start_server,
                args=(args.port, args.debug),
                daemon=True
            )
            server_thread.start()
            run_cli_mode(config, args.port)
        except Exception as e:
            logger.error(f"启动GUI失败: {str(e)}")
            logger.warning("回退到命令行模式")
            # 启动Flask服务器
            server_thread = threading.Thread(
                target=start_server,
                args=(args.port, args.debug),
                daemon=True
            )
            server_thread.start()
            run_cli_mode(config, args.port)
    else:
        # CLI模式 - 启动Flask服务器
        logger.info(f"正在启动ModuKit，端口: {args.port}, 调试模式: {args.debug}")
        server_thread = threading.Thread(
            target=start_server,
            args=(args.port, args.debug),
            daemon=True
        )
        server_thread.start()
        run_cli_mode(config, args.port)

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



