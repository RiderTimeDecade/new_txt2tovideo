import queue
import threading
import uuid
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.task_queue = queue.Queue()
        self.worker_thread = None

    def create_task(self, text, voice_name, file_id, img_path=None):
        """创建新任务"""
        task_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        self.tasks[task_id] = {
            "status": "queued",
            "progress": 0,
            "message": "任务已加入队列",
            "file_id": file_id,
            "created_at": current_time,
            "text": text[:50] + "..." if len(text) > 50 else text,
            "voice": voice_name,
            "has_image": bool(img_path)
        }
        
        return task_id

    def update_task_status(self, task_id, status, progress=None, message=None):
        """更新任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if progress is not None:
                self.tasks[task_id]["progress"] = progress
            if message is not None:
                self.tasks[task_id]["message"] = message

    def get_task(self, task_id):
        """获取任务信息"""
        return self.tasks.get(task_id)

    def get_all_tasks(self):
        """获取所有任务"""
        return self.tasks

    def start_worker(self, worker_func):
        """启动工作线程"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=worker_func)
            self.worker_thread.daemon = True
            self.worker_thread.start()

    def add_to_queue(self, task_data):
        """添加任务到队列"""
        self.task_queue.put(task_data)

    def get_from_queue(self, block=True, timeout=1):
        """从队列获取任务"""
        try:
            return self.task_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def task_done(self):
        """标记任务完成"""
        self.task_queue.task_done() 