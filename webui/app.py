from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
import uuid
from datetime import datetime
import threading
import queue
import time

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入项目模块
from models.generate_audio_srt_to_video import generate_audio_srt_to_video
from plugs.config import create_speech_config, DEFAULT_SUBSCRIPTION_KEY, DEFAULT_REGION

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('output/temp', exist_ok=True)

# 任务状态存储
tasks = {}
# 任务队列
task_queue = queue.Queue()
# 任务处理线程
worker_thread = None

def worker():
    """工作线程，处理任务队列中的任务"""
    global worker_thread
    while True:
        try:
            # 从队列中获取任务
            task = task_queue.get(block=True, timeout=1)
            if task is None:
                break
                
            task_id, text_file, voice_name = task
            print(f"工作线程开始处理任务: {task_id}")
            
            # 处理任务
            process_task(task_id, text_file, voice_name)
            
            # 标记任务完成
            task_queue.task_done()
            
        except queue.Empty:
            # 队列为空，继续等待
            continue
        except Exception as e:
            print(f"工作线程处理任务时出错: {str(e)}")
            # 标记任务失败
            if task_id in tasks:
                tasks[task_id]["status"] = "failed"
                tasks[task_id]["message"] = f"处理失败: {str(e)}"
    
    print("工作线程退出")
    worker_thread = None

def start_worker():
    """启动工作线程"""
    global worker_thread
    if worker_thread is None or not worker_thread.is_alive():
        worker_thread = threading.Thread(target=worker)
        worker_thread.daemon = True
        worker_thread.start()
        print("工作线程已启动")

# 启动工作线程
start_worker()

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """获取可用的语音列表"""
    try:
        with open('../config/voice/voices.json', 'r', encoding='utf-8') as f:
            voices_data = json.load(f)
        
        # 将嵌套的声音配置转换为列表格式
        voices = []
        for category, voice_dict in voices_data.items():
            for voice_name, voice_id in voice_dict.items():
                voices.append({
                    "id": voice_id,
                    "name": f"{category}-{voice_name}"
                })
        
        return jsonify({"voices": voices})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频的API端点"""
    try:
        # 获取请求数据
        data = request.json
        text = data.get('text', '')
        voice_name = data.get('voice', '')
        
        if not text:
            return jsonify({"success": False, "error": "文本不能为空"})
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        text_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.txt")
        
        # 保存文本到文件
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # 创建任务ID
        task_id = str(uuid.uuid4())
        tasks[task_id] = {
            "status": "queued",
            "progress": 0,
            "message": "任务已加入队列",
            "file_id": file_id,
            "created_at": datetime.now().isoformat(),
            "text": text[:50] + "..." if len(text) > 50 else text,  # 保存文本预览
            "voice": voice_name
        }
        
        # 将任务添加到队列
        task_queue.put((task_id, text_file, voice_name))
        
        # 确保工作线程正在运行
        start_worker()
        
        return jsonify({
            "success": True, 
            "task_id": task_id,
            "message": "任务已加入队列"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def process_task(task_id, text_file, voice_name):
    """处理生成视频的任务"""
    try:
        # 更新任务状态
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        tasks[task_id]["message"] = "正在准备处理环境..."
        
        # 清空临时目录
        temp_dir = 'output/temp'
        if os.path.exists(temp_dir):
            print(f"清空临时目录: {temp_dir}")
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {str(e)}")
        else:
            os.makedirs(temp_dir, exist_ok=True)
        
        # 更新任务状态
        tasks[task_id]["progress"] = 15
        tasks[task_id]["message"] = "正在生成音频和字幕..."
        
        # 生成音频和字幕
        print(f"开始处理任务 {task_id}")
        print(f"文本文件: {text_file}")
        print(f"语音名称: {voice_name}")
        
        # 更新任务状态
        tasks[task_id]["progress"] = 20
        tasks[task_id]["message"] = "正在生成视频..."
        
        # 调用生成函数
        output_path = generate_audio_srt_to_video(text_file, voice_name)
        print(f"生成的视频路径: {output_path}")
        
        # 获取生成的视频文件名（应该是类似 merged_20250403_145255.mp4 的格式）
        video_filename = os.path.basename(output_path)
        
        # 更新任务状态
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["message"] = "处理完成"
        tasks[task_id]["file_id"] = video_filename  # 使用新的文件名
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        
        print(f"任务 {task_id} 处理完成")
        print(f"输出文件: {output_path}")
        
    except Exception as e:
        # 更新任务状态为失败
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"处理失败: {str(e)}"
        tasks[task_id]["error"] = str(e)
        print(f"处理任务 {task_id} 出错: {str(e)}")

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({"success": False, "error": "任务不存在"})
    
    return jsonify({
        "success": True,
        "task": tasks[task_id]
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务列表"""
    # 按创建时间倒序排序
    sorted_tasks = sorted(
        [{"id": task_id, **task_data} for task_id, task_data in tasks.items()],
        key=lambda x: x["created_at"],
        reverse=True
    )
    
    return jsonify({
        "success": True,
        "tasks": sorted_tasks
    })

@app.route('/api/download/<file_id>', methods=['GET'])
def download_video(file_id):
    """下载生成的视频"""
    try:
        # 查找视频文件（先在 output/temp 目录中查找）
        temp_dir = 'output/temp'
        video_path = os.path.join(temp_dir, file_id)
        
        if not os.path.exists(video_path):
            # 如果在 temp 目录中找不到，尝试在 output 目录中查找
            output_dir = 'output'
            video_path = os.path.join(output_dir, file_id)
            if not os.path.exists(video_path):
                return jsonify({"error": "视频文件不存在"})
        
        # 发送文件，使用原始文件名作为下载文件名
        return send_file(
            video_path,
            as_attachment=True,
            download_name=file_id,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 