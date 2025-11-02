# 🎯 Keyboard Typer

<div align="center">

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Language](https://img.shields.io/badge/language-中文-red)

**一个全中文界面的键盘模拟输入器，适用于那些不支持复制粘贴的网站或应用程序**

[功能特点](#-功能特点) • [快速开始](#-快速开始) • [使用说明](#-使用说明) • [技术栈](#-技术栈)

</div>

## 📸 预览

<div align="center">

![应用主界面](https://via.placeholder.com/800x500/2d3748/ffffff?text=Keyboard+Typer+主界面)

*战术风格的深色主题界面，专业而酷炫*

</div>

## ✨ 功能特点

- 🖥️ **现代化桌面应用** - 基于 Electron 的跨平台桌面应用
- ⌨️ **真实键盘模拟** - 逐字符模拟真实键盘输入，绕过复制粘贴限制
- 🎛️ **灵活参数配置** - 可调节输入速度、延时、抖动等参数
- ⏰ **智能倒计时** - 提供切换窗口的缓冲时间
- 🎲 **随机延时抖动** - 模拟真实打字节奏，更加自然
- 🛑 **实时控制** - 支持随时停止输入操作
- 📝 **多语言支持** - 完美支持中英文及特殊字符
- 🔧 **输入法自动切换** - 智能识别并切换中英文输入法
- 💻 **IDE模式优化** - 专为代码编辑器优化的输入模式

## 🎬 功能演示

<div align="center">

![功能演示](https://via.placeholder.com/600x400/4a5568/ffffff?text=功能演示+GIF)

*实时键盘模拟输入演示*

</div>

## 🚀 快速开始

### 环境要求

- **Windows** 操作系统
- **Python** 3.8+ ([下载地址](https://www.python.org/))
- **Node.js** 14+ ([下载地址](https://nodejs.org/))

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/username/keyboard-typer.git
   cd keyboard-typer
   ```

2. **安装依赖**
   ```bash
   # 安装 Node.js 依赖
   cd config
   npm install
   cd ..
   
   # 安装 Python 依赖
   pip install -r config/requirements.txt
   ```

3. **启动应用**
   ```bash
   # 使用集成启动器（推荐）
   python launcher.py
   
   # 或直接启动
   python src/backend/start_app.py
   ```

### 一键启动器

项目提供了功能强大的集成启动器：

```bash
python launcher.py              # 启动应用（包含系统检查）
python launcher.py --no-check   # 跳过系统检查直接启动
python launcher.py --dev        # 开发模式（打开调试工具）
python launcher.py --fix        # 自动修复环境问题
python launcher.py --shortcuts  # 创建桌面快捷方式
```

## 📖 使用说明

### 基本操作

1. **输入文本** - 在左侧文本框中输入要模拟的内容
2. **调整参数** - 根据需要调整右侧的配置选项
3. **开始输入** - 点击"启动"按钮开始倒计时
4. **切换窗口** - 在倒计时期间切换到目标应用
5. **自动输入** - 程序将自动开始模拟键盘输入

### 参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| **速度 (WPM)** | 每分钟字数，控制输入速度 | 60-180 |
| **延迟 (秒)** | 启动前的倒计时时间 | 3-5秒 |
| **抖动 (%)** | 随机延时百分比，模拟真实打字 | 5-15% |

### 高级选项

- ✅ **发送回车键** - 输入完成后自动发送回车
- ✅ **自动切换输入法** - 智能切换中英文输入法
- ✅ **IDE模式** - 针对代码编辑器的特殊优化

## 🏗️ 技术架构

```
┌─────────────────┐
│   Electron UI   │  ← 用户界面 (HTML/CSS/JS)
│   Port: Window  │
└────────┬────────┘
         │ HTTP REST API
         │ (localhost:5000)
┌────────┴────────┐
│  Flask Backend  │  ← Python 后端服务
│   Port: 5000    │
└────────┬────────┘
         │ pynput + win32api
         │
┌────────┴────────┐
│  Windows API    │  ← 系统级键盘模拟
│  Keyboard Input │
└─────────────────┘
```

## 🔧 技术栈

### 前端技术
- **Electron** - 跨平台桌面应用框架
- **HTML5/CSS3** - 现代化界面构建
- **Tailwind CSS** - 实用优先的CSS框架
- **JavaScript ES6+** - 现代JavaScript特性

### 后端技术
- **Python 3.8+** - 核心开发语言
- **Flask** - 轻量级Web框架
- **pynput** - 跨平台键盘鼠标控制
- **pywin32** - Windows系统API调用

## 📁 项目结构

```
keyboard-typer/
├── src/                    # 源代码
│   ├── frontend/          # 前端界面
│   └── backend/           # 后端服务
├── assets/                # 静态资源
├── config/                # 配置文件
├── docs/                  # 项目文档
├── launcher.py            # 集成启动器
└── README.md             # 项目说明
```

## 🎯 使用场景

- 📝 **在线表单填写** - 绕过禁止粘贴的网站表单
- 💻 **代码输入** - 在不支持导入的在线编程环境中输入代码
- 📋 **考试系统** - 在限制复制粘贴的考试平台中输入答案
- 🎮 **游戏内输入** - 在游戏聊天框中输入预设文本
- 📱 **远程桌面** - 通过远程桌面向目标机器输入文本

## ⚠️ 注意事项

- 仅支持 Windows 操作系统
- 请确保在倒计时期间将光标定位到目标输入框
- 建议先用较慢的速度测试效果
- 某些特殊字符在部分应用程序中可能显示异常

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=username/keyboard-typer&type=Date)](https://star-history.com/#username/keyboard-typer&Date)

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

Made with ❤️ by Keyboard Typer Team

</div>