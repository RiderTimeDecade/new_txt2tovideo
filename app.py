from flask import Flask, render_template, request, send_file, jsonify, session
import os
import json
import threading
from flask_session import Session
from models.generate_audio_srt_to_video import generate_audio_srt_to_video
import time
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key'
Session(app)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 任务状态存储
tasks = {}

# 读取可用的语音列表
def get_available_voices():
    with open('config/voice/voices.json', 'r', encoding='utf-8') as f:
        voices_data = json.load(f)
    
    # 将嵌套的声音配置扁平化为单层字典
    voices = {}
    for category, voice_dict in voices_data.items():
        for voice_name, voice_id in voice_dict.items():
            voices[f"{category}-{voice_name}"] = voice_id
    
    return voices

@app.route('/')
def index():
    voices = get_available_voices()
    return render_template('index.html', voices=voices)

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件上传
    if 'text_file' not in request.files:
        return jsonify({'error': '没有找到文件'}), 400
    
    file = request.files['text_file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    voice_name = request.form.get('voice_name')
    if not voice_name:
        return jsonify({'error': '没有选择语音'})
    
    # 生成唯一的任务ID
    task_id = str(uuid.uuid4())
    
    # 保存上传的文件
    filename = f"{task_id}.txt"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # 创建任务状态
    tasks[task_id] = {
        'status': 'processing',
        'progress': 0,
        'output_file': None,
        'start_time': time.time(),
        'text_path': filepath,
        'voice_name': voice_name
    }
    
    # 启动生成线程
    thread = threading.Thread(target=process_video, args=(task_id, filepath, voice_name))
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})

def process_video(task_id, text_path, voice_name):
    try:
        # 调用生成函数
        generate_audio_srt_to_video(text_path=text_path, voice_name=voice_name)
        
        # 生成成功，更新任务状态
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['progress'] = 100
        tasks[task_id]['output_file'] = 'output/output.mp4'
    except Exception as e:
        # 生成失败，更新任务状态
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)

@app.route('/status/<task_id>')
def task_status(task_id):
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    # 估算进度 (简单模拟，实际应用中可能需要更复杂的进度估算)
    task = tasks[task_id]
    if task['status'] == 'processing':
        elapsed_time = time.time() - task['start_time']
        # 假设整个过程大约需要30秒
        estimated_progress = min(95, int(elapsed_time / 30 * 100))
        task['progress'] = estimated_progress
    
    return jsonify({
        'status': task['status'],
        'progress': task['progress'],
        'output_file': task['output_file'] if task['status'] == 'completed' else None
    })

@app.route('/download/<task_id>')
def download_file(task_id):
    if task_id not in tasks or tasks[task_id]['status'] != 'completed':
        return jsonify({'error': '文件不可用'}), 404
    
    return send_file(tasks[task_id]['output_file'], as_attachment=True)

if __name__ == '__main__':
    # 创建模板目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 创建static目录
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True)
