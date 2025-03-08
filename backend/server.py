#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ModuKit - 后端服务器
提供API接口供前端调用
"""

import os
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
STATIC_DIR = ROOT_DIR / "static"

def create_app(debug=False):
    """创建Flask应用实例"""
    app = Flask(__name__, static_folder=str(STATIC_DIR))
    app.config['DEBUG'] = debug
    
    # 允许跨域请求
    CORS(app)
    
    # 注册路由
    register_routes(app)
    
    return app

def register_routes(app):
    """注册API路由"""
    
    @app.route('/')
    def index():
        """返回首页"""
        return send_from_directory(STATIC_DIR, 'index.html')
    
    @app.route('/static/<path:path>')
    def serve_static(path):
        """提供静态文件"""
        return send_from_directory(STATIC_DIR, path)
    
    @app.route('/api/status', methods=['GET'])
    def status():
        """返回服务器状态"""
        return jsonify({
            'status': 'running',
            'version': '0.1.0'
        })
    
    @app.route('/api/modules', methods=['GET'])
    def list_modules():
        """列出所有可用模块"""
        # 这里需要实现模块列表获取逻辑
        # 暂时返回示例数据
        modules = [
            {
                'id': 'file_tools',
                'name': '文件工具',
                'description': '文件处理相关工具集',
                'version': '0.1.0'
            },
            {
                'id': 'text_tools',
                'name': '文本工具',
                'description': '文本处理相关工具集',
                'version': '0.1.0'
            },
            {
                'id': 'image_tools',
                'name': '图像工具',
                'description': '图像处理相关工具集',
                'version': '0.1.0'
            },
            {
                'id': 'data_analysis',
                'name': '数据分析',
                'description': '数据分析相关工具集',
                'version': '0.1.0'
            }
        ]
        return jsonify(modules)
    
    @app.route('/api/modules/<module_id>', methods=['GET'])
    def get_module(module_id):
        """获取指定模块的详细信息"""
        # 这里需要实现模块详情获取逻辑
        # 暂时返回示例数据
        module = {
            'id': module_id,
            'name': f'{module_id}工具',
            'description': f'{module_id}相关工具集',
            'version': '0.1.0',
            'tools': [
                {
                    'id': f'{module_id}_tool1',
                    'name': '工具1',
                    'description': '示例工具1'
                },
                {
                    'id': f'{module_id}_tool2',
                    'name': '工具2',
                    'description': '示例工具2'
                }
            ]
        }
        return jsonify(module)

if __name__ == '__main__':
    app = create_app(debug=True)
    app.run(port=5000) 