#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ModuKit - 配置加载器
负责加载和管理应用配置
"""

import os
import json
import configparser
from pathlib import Path

class ConfigLoader:
    """配置加载器类，负责加载和管理应用配置"""
    
    def __init__(self, config_path=None):
        """初始化配置加载器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.root_dir = Path(__file__).parent.parent.absolute()
        
        if config_path is None:
            self.config_path = self.root_dir / "config" / "default.ini"
        else:
            self.config_path = Path(config_path)
            
        # 确保配置目录存在
        os.makedirs(self.config_path.parent, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置文件
        
        Returns:
            dict: 配置字典
        """
        # 检查配置文件是否存在
        if not self.config_path.exists():
            # 创建默认配置
            return self._create_default_config()
            
        # 根据文件扩展名选择加载方式
        if self.config_path.suffix.lower() == '.json':
            return self._load_json_config()
        elif self.config_path.suffix.lower() == '.ini':
            return self._load_ini_config()
        else:
            raise ValueError(f"不支持的配置文件格式: {self.config_path.suffix}")
            
    def _load_json_config(self):
        """加载JSON格式配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON配置文件失败: {e}")
            return self._create_default_config()
            
    def _load_ini_config(self):
        """加载INI格式配置文件"""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path, encoding='utf-8')
            
            # 将ConfigParser对象转换为字典
            result = {}
            for section in config.sections():
                result[section] = {}
                for key, value in config[section].items():
                    result[section][key] = value
                    
            return result
        except Exception as e:
            print(f"加载INI配置文件失败: {e}")
            return self._create_default_config()
            
    def _create_default_config(self):
        """创建默认配置"""
        default_config = {
            'app': {
                'name': 'ModuKit',
                'version': '0.1.0',
                'debug': 'false',
                'theme': 'default',
                'language': 'zh_CN'
            },
            'server': {
                'host': '127.0.0.1',
                'port': '5000'
            },
            'modules': {
                'enabled': 'file_tools,text_tools'
            }
        }
        
        # 保存默认配置
        self._save_config(default_config)
        
        return default_config
        
    def _save_config(self, config):
        """保存配置到文件"""
        # 确保配置目录存在
        os.makedirs(self.config_path.parent, exist_ok=True)
        
        # 根据文件扩展名选择保存方式
        if self.config_path.suffix.lower() == '.json':
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        elif self.config_path.suffix.lower() == '.ini':
            config_parser = configparser.ConfigParser()
            
            for section, items in config.items():
                config_parser[section] = {}
                for key, value in items.items():
                    config_parser[section][key] = str(value)
                    
            with open(self.config_path, 'w', encoding='utf-8') as f:
                config_parser.write(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {self.config_path.suffix}")
            
    def get(self, section, key, default=None):
        """获取配置项
        
        Args:
            section: 配置节
            key: 配置键
            default: 默认值，如果配置不存在则返回此值
            
        Returns:
            配置值或默认值
        """
        try:
            return self.config[section][key]
        except (KeyError, TypeError):
            return default
            
    def set(self, section, key, value):
        """设置配置项
        
        Args:
            section: 配置节
            key: 配置键
            value: 配置值
        """
        # 确保配置节存在
        if section not in self.config:
            self.config[section] = {}
            
        # 设置配置值
        self.config[section][key] = value
        
        # 保存配置
        self._save_config(self.config)
        
    def get_sections(self):
        """获取所有配置节
        
        Returns:
            list: 配置节列表
        """
        return list(self.config.keys())
        
    def get_section(self, section, default=None):
        """获取指定配置节的所有配置
        
        Args:
            section: 配置节
            default: 默认值，如果配置节不存在则返回此值
            
        Returns:
            dict: 配置字典或默认值
        """
        return self.config.get(section, default)
        
    def get_config(self):
        """获取整个配置
        
        Returns:
            dict: 配置字典
        """
        return self.config 