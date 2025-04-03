#!/usr/bin/env python3
"""
Web UI 启动脚本
"""
import os
import sys
import webbrowser
from threading import Timer

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入 Flask 应用
from app import app

def open_browser():
    """在默认浏览器中打开应用"""
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # 设置端口
    port = 5000
    
    # 延迟 1.5 秒后打开浏览器
    Timer(1.5, open_browser).start()
    
    # 启动应用
    print(f"启动 Web UI，访问 http://127.0.0.1:{port}/")
    app.run(debug=True, host='0.0.0.0', port=port) 