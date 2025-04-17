import os
import json
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file
        self._ensure_history_file()
        print(f"历史记录管理器初始化，文件路径: {self.history_file}")
    
    def _ensure_history_file(self):
        """确保历史记录文件存在"""
        if not os.path.exists(os.path.dirname(self.history_file)):
            os.makedirs(os.path.dirname(self.history_file))
            print(f"创建历史记录目录: {os.path.dirname(self.history_file)}")
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            print(f"创建新的历史记录文件: {self.history_file}")
    
    def add_record(self, task_id, text_content, voice_name, img_path, output_path):
        """添加新的历史记录"""
        try:
            print(f"开始添加历史记录: task_id={task_id}")
            
            # 确保历史文件存在
            self._ensure_history_file()
            
            # 读取现有历史记录
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # 创建新记录
            new_record = {
                "task_id": task_id,
                "text_preview": text_content[:100] + "..." if len(text_content) > 100 else text_content,
                "voice_name": voice_name,
                "img_path": img_path,
                "output_path": output_path,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"新历史记录: {new_record}")
            
            # 添加新记录
            history.append(new_record)
            
            # 保存更新后的历史记录
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            print(f"历史记录已保存到: {self.history_file}")
            return True
            
        except Exception as e:
            print(f"添加历史记录失败: {str(e)}")
            return False
    
    def get_history(self, limit=50):
        """获取历史记录"""
        try:
            print(f"获取历史记录，限制: {limit}")
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            result = history[-limit:]  # 返回最近的记录
            print(f"获取到 {len(result)} 条历史记录")
            return result
        except Exception as e:
            print(f"获取历史记录失败: {str(e)}")
            return [] 