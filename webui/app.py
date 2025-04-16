from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import uuid
import json

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入自定义模块
from models.task_manager import TaskManager
from models.file_handler import FileHandler
from models.video_processor import VideoProcessor
from routes.task_routes import TaskRoutes
from routes.download_routes import DownloadRoutes
from routes.voice_routes import VoiceRoutes

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'webui/data')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 初始化管理器
task_manager = TaskManager()
file_handler = FileHandler(
    app.config['UPLOAD_FOLDER'], 
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'webui/output/temp')
)
file_handler.clear_temp_directory()
print(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'webui/output/temp'))

video_processor = VideoProcessor(task_manager)

# 初始化路由处理器
task_routes = TaskRoutes(task_manager, file_handler, video_processor)
download_routes = DownloadRoutes(file_handler)
voice_routes = VoiceRoutes()

def worker():
    """工作线程，处理任务队列中的任务"""
    while True:
        try:
            # 从队列中获取任务
            task_data = task_manager.get_from_queue()
            if task_data is None:
                continue
                
            task_id, text_file, voice_name, img_path = task_data
            print(f"工作线程开始处理任务: {task_id}")
            
            # 更新任务状态为处理中
            task_manager.update_task_status(
                task_id,
                "processing",
                progress=0,
                message="任务开始处理..."
            )
            
            # 处理任务
            video_processor.process_video(task_id, text_file, voice_name, img_path)
            
            file_handler.clear_temp_directory()
            # 标记任务完成
            task_manager.task_done()
            
        except Exception as e:
            print(f"工作线程处理任务时出错: {str(e)}")

# 启动工作线程
task_manager.start_worker(worker)

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频的API端点"""
    return task_routes.generate_video(request)

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    return task_routes.get_task_status(task_id)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务列表"""
    return task_routes.get_tasks()

@app.route('/api/download/<file_id>', methods=['GET'])
def download_video(file_id):
    """下载生成的视频"""
    return download_routes.download_video(file_id)

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """获取可用的语音列表"""
    return voice_routes.get_voices()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 