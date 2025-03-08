#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ModuKit - 模块化工具箱
主程序文件
"""

import os
import sys
import json
import importlib
from pathlib import Path

class ModuKit:
    """ModuKit主类，负责管理和加载模块"""
    
    def __init__(self):
        self.version = "0.1.0"
        self.modules = {}
        self.config = {}
        self.module_path = Path(__file__).parent / "modules"
        self.config_path = Path(__file__).parent / "config.json"
        
        # 创建必要的目录
        self._create_directories()
        
        # 加载配置
        self._load_config()
        
        # 加载模块
        self._load_modules()
        
    def _create_directories(self):
        """创建必要的目录结构"""
        directories = [
            self.module_path,
            Path(__file__).parent / "data",
            Path(__file__).parent / "logs",
            Path(__file__).parent / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            
    def _load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self.config = self._create_default_config()
        else:
            self.config = self._create_default_config()
            
    def _create_default_config(self):
        """创建默认配置"""
        default_config = {
            "version": self.version,
            "theme": "default",
            "language": "zh_CN",
            "enabled_modules": [],
            "user_settings": {}
        }
        
        # 保存默认配置
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
            
        return default_config
    
    def _load_modules(self):
        """加载所有模块"""
        if not self.module_path.exists():
            return
            
        # 遍历模块目录
        for module_dir in self.module_path.iterdir():
            if module_dir.is_dir() and (module_dir / "__init__.py").exists():
                module_name = module_dir.name
                try:
                    # 动态导入模块
                    module_path = f"modules.{module_name}"
                    module = importlib.import_module(module_path)
                    
                    # 检查模块是否有效
                    if hasattr(module, "ModuleInfo") and hasattr(module, "Module"):
                        self.modules[module_name] = {
                            "info": module.ModuleInfo,
                            "instance": module.Module()
                        }
                        print(f"成功加载模块: {module_name}")
                    else:
                        print(f"模块格式无效: {module_name}")
                except Exception as e:
                    print(f"加载模块 {module_name} 失败: {e}")
    
    def get_module(self, module_name):
        """获取指定名称的模块"""
        return self.modules.get(module_name, {}).get("instance")
    
    def list_modules(self):
        """列出所有已加载的模块"""
        return [
            {
                "name": name,
                "version": info["info"].version,
                "description": info["info"].description,
                "author": info["info"].author
            }
            for name, info in self.modules.items()
        ]
    
    def run(self):
        """运行ModuKit"""
        print(f"ModuKit v{self.version} 启动中...")
        print(f"已加载 {len(self.modules)} 个模块")
        
        # 这里可以启动GUI或CLI界面
        # 暂时使用简单的CLI演示
        self._run_cli()
    
    def _run_cli(self):
        """运行命令行界面"""
        print("\n欢迎使用 ModuKit!")
        print("输入 'help' 获取帮助，输入 'exit' 退出程序")
        
        while True:
            cmd = input("\nModuKit> ").strip()
            
            if cmd == "exit":
                print("感谢使用 ModuKit，再见!")
                break
            elif cmd == "help":
                self._show_help()
            elif cmd == "list":
                self._list_modules_cli()
            elif cmd.startswith("use "):
                module_name = cmd[4:].strip()
                self._use_module(module_name)
            else:
                print("未知命令，输入 'help' 获取帮助")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n可用命令:")
        print("  help       - 显示帮助信息")
        print("  list       - 列出所有可用模块")
        print("  use <模块>  - 使用指定模块")
        print("  exit       - 退出程序")
    
    def _list_modules_cli(self):
        """在CLI中列出所有模块"""
        modules = self.list_modules()
        
        if not modules:
            print("没有找到可用模块")
            return
            
        print("\n可用模块:")
        for module in modules:
            print(f"  {module['name']} (v{module['version']}) - {module['description']}")
    
    def _use_module(self, module_name):
        """使用指定模块"""
        module = self.get_module(module_name)
        
        if module is None:
            print(f"模块 '{module_name}' 不存在")
            return
            
        try:
            # 调用模块的主方法
            module.run()
        except Exception as e:
            print(f"运行模块时出错: {e}")

if __name__ == "__main__":
    app = ModuKit()
    app.run() 