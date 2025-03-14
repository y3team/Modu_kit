# ModuKit (模块化工具箱)

一个安静的模块化工具箱（开发中）

## 项目简介

ModuKit是一个高度模块化的工具箱应用，旨在提供一系列实用工具，帮助用户提高工作效率。每个工具都作为独立模块存在，用户可以根据自己的需求自由组合使用。

## 特点

- **模块化设计**：每个工具都是独立的模块，可以单独使用或组合使用
- **可扩展性**：支持自定义模块开发和导入
- **跨平台**：支持Windows、macOS和Linux系统
- **用户友好**：简洁直观的界面设计，易于上手
- **高效性能**：轻量级设计，占用资源少
- **多种运行模式**：支持CLI模式和GUI模式

## 包含模块

- 文件处理工具
- 文本编辑工具
- 图像处理工具
- 数据分析工具
- 系统优化工具
- 更多模块正在开发中...

## 技术栈

- 后端：Python
- 前端：HTML/CSS/JavaScript (使用PyWebView或Web浏览器)
- 数据存储：SQLite/JSON

## 安装与使用

```bash
# 克隆仓库
git clone https://github.com/yourusername/modukit.git

# 进入项目目录
cd modukit

# 安装依赖
pip install -r requirements.txt

# 运行应用（CLI模式，默认）
python main.py

# 运行应用（GUI模式，独立窗口）
python main.py --gui

# 调试模式
python main.py --debug
```

## 运行模式

ModuKit支持两种运行模式：

### CLI模式（默认）

命令行界面模式，提供简单的命令行交互，同时可以在浏览器中查看Web界面。

可用命令：
- `help` - 显示帮助信息
- `status` - 显示服务器状态
- `modules` - 列出可用模块
- `open` - 在浏览器中打开界面
- `exit` - 退出程序

### GUI模式

图形用户界面模式，使用PyWebView创建独立窗口，提供更好的用户体验。

启动方式：
```bash
python main.py --gui
```

## 贡献指南

欢迎贡献代码或提出建议！请参阅`CONTRIBUTING.md`文件了解详情。

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件
