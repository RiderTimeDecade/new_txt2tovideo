from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
import uuid
from datetime import datetime

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
        
        # 将嵌套的声音配置扁平化为单层字典
        voices = {}
        for category, voice_dict in voices_data.items():
            for voice_name, voice_id in voice_dict.items():
                voices[f"{category}-{voice_name}"] = voice_id
        
        return jsonify({"success": True, "voices": voices})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

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
            "status": "processing",
            "progress": 0,
            "message": "正在处理...",
            "file_id": file_id,
            "created_at": datetime.now().isoformat()
        }
        
        # 启动异步任务
        from threading import Thread
        thread = Thread(target=process_task, args=(task_id, text_file, voice_name))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True, 
            "task_id": task_id,
            "message": "任务已提交"
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
        output_file = generate_audio_srt_to_video(text_file, voice_name)
        
        # 更新任务状态
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["message"] = "处理完成"
        tasks[task_id]["file_id"] = os.path.basename(output_file)
        
        print(f"任务 {task_id} 处理完成")
        print(f"输出文件: {output_file}")
        
    except Exception as e:
        # 更新任务状态为失败
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"处理失败: {str(e)}"
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

@app.route('/api/download/<file_id>', methods=['GET'])
def download_video(file_id):
    """下载生成的视频"""
    try:
        # 查找视频文件
        output_dir = 'output'
        video_path = os.path.join(output_dir, file_id)
        
        if not os.path.exists(video_path):
            return jsonify({"success": False, "error": "视频文件不存在"})
        
        # 发送文件
        return send_file(video_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 