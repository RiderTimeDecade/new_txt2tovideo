from flask import jsonify, request
from models.task_manager import TaskManager
from models.file_handler import FileHandler
from models.video_processor import VideoProcessor
import uuid

class TaskRoutes:
    def __init__(self, task_manager, file_handler, video_processor, history_manager):
        self.task_manager = task_manager
        self.file_handler = file_handler
        self.video_processor = video_processor
        self.history_manager = history_manager

    def generate_video(self, request):
        """生成视频的API端点"""
        try:
            # 获取表单数据
            text = request.form.get('text', '')
            voice_name = request.form.get('voice', '')
            
            if not text:
                return jsonify({"error": "文本不能为空"})
            
            if not voice_name:
                return jsonify({"error": "请选择语音"})
            
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            
            # 保存文本文件
            text_file = self.file_handler.save_text_file(text, file_id)
            
            # 处理图片上传
            img_path = None
            if 'image' in request.files and request.files['image'].filename:
                img_path = self.file_handler.save_image_file(request.files['image'], file_id)
            
            # 创建任务
            task_id = self.task_manager.create_task(text, voice_name, file_id, img_path)
            
            # 将任务添加到队列
            self.task_manager.add_to_queue((task_id, text_file, voice_name, img_path))
            
            return jsonify({
                "task_id": task_id,
                "message": "任务已加入队列"
            })
        
        except Exception as e:
            print(f"生成视频时出错: {str(e)}")
            return jsonify({"error": str(e)})

    def get_task_status(self, task_id):
        """获取任务状态"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return jsonify({"success": False, "error": "任务不存在"})
        
        return jsonify({
            "success": True,
            "task": task
        })

    def get_tasks(self):
        """获取所有任务列表"""
        tasks = self.task_manager.get_all_tasks()
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