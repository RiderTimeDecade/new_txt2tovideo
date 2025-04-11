# 文本转视频生成器

一个简单易用的工具，可将文本内容转换为带有语音和字幕的视频。支持批量处理、多种语音和自定义背景图片。

![文本转视频生成器](https://img.shields.io/badge/状态-开发中-brightgreen)

## 功能特点

- **文本转视频**：将输入文本转换为带有语音朗读和字幕的视频
- **多语音支持**：提供多种语音选择，满足不同场景需求
- **自定义背景**：支持上传自定义背景图片
- **批量处理**：支持文件夹批量处理，自动配对文本和图片
- **任务管理**：直观的任务状态跟踪和管理界面
- **时间统计**：详细记录任务创建、开始和完成时间，计算等待和处理时间

## 系统要求

- Python 3.8+
- Flask
- FFmpeg (用于视频处理)
- 微软语音合成API (语音生成)

## 安装指南

1. 克隆仓库
```bash
git clone https://github.com/yourusername/new_txt2tovideo.git
cd new_txt2tovideo
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置语音API
在 `config/voice/` 目录下创建配置文件，包含您的API密钥。

5. 确保安装了FFmpeg
请参考[FFmpeg官方文档](https://ffmpeg.org/download.html)安装FFmpeg。

## 使用说明

### 启动应用

```bash
cd webui
python app.py
```

应用将在 http://localhost:5000 运行。

### 单个任务生成

1. 在文本框中输入要转换的文本
2. 从下拉菜单中选择语音
3. 可选择上传背景图片
4. 点击"生成视频"按钮
5. 在任务完成后，点击"下载视频"按钮获取生成的视频

### 批量任务处理

1. 点击"批量文件夹模式"按钮
2. 选择包含文本文件(.txt)和图片文件的文件夹
   - 文本和图片文件名需匹配，例如：text1.txt 对应 text1.png
3. 从下拉菜单中选择语音
4. 点击"生成视频"按钮
5. 查看任务列表中的进度，等待所有任务完成
6. 在"已完成"选项卡中下载生成的视频

## 项目结构

```
new_txt2tovideo/
│
├── config/            # 配置文件目录
│   └── voice/         # 语音配置
│
├── data/              # 上传的文本和图片文件
│
├── models/            # 核心处理模块
│   └── generate_audio_srt_to_video.py    # 视频生成核心
│
├── output/            # 输出目录
│   └── temp/          # 临时文件目录
│
├── plugs/             # 插件和工具
│   └── config.py      # 配置处理
│
├── webui/             # Web界面
│   ├── models/        # 模型模块
│   ├── routes/        # 路由模块
│   ├── static/        # 静态资源
│   ├── templates/     # 模板文件
│   └── app.py         # 主应用文件
│
└── requirements.txt   # 依赖列表
```

## 常见问题

**Q: 为什么我的任务一直在"等待中"状态？**  
A: 可能是处理队列较长或系统资源不足。大型文本或批量任务可能需要较长处理时间。

**Q: 如何使用自己的语音API？**  
A: 在 `config/voice/` 目录下修改配置文件，添加您的API密钥和区域信息。

**Q: 支持哪些语言？**  
A: 支持的语言取决于您使用的语音API。目前微软语音合成API支持多种语言和方言。

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议。请先创建issue讨论您想要进行的更改。

## 许可证

MIT License

## 致谢

- 感谢微软提供语音合成API
- 感谢FFmpeg提供视频处理功能
