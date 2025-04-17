import os
import shutil
from werkzeug.utils import secure_filename

class FileHandler:
    def __init__(self, upload_folder, temp_folder):
        self.upload_folder = upload_folder
        self.temp_folder = temp_folder
        self.output_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)

    def save_text_file(self, text, file_id):
        """保存文本文件"""
        text_file = os.path.join(self.upload_folder, f"{file_id}.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        return text_file

    def save_image_file(self, image, file_id):
        """保存图片文件"""
        if image and image.filename:
            filename = secure_filename(image.filename)
            img_path = os.path.join(self.upload_folder, f"{file_id}_{filename}")
            image.save(img_path)
            return img_path
        return None

    def clear_temp_directory(self):
        """清空临时目录"""
        if os.path.exists(self.temp_folder):
            for file in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {str(e)}")

    def get_video_path(self, file_id):
        """获取视频文件路径"""
        # 先在临时目录中查找
        temp_path = os.path.join(self.temp_folder, file_id)
        if os.path.exists(temp_path):
            return temp_path
        
        # 如果在临时目录中找不到，尝试在输出目录中查找
        output_path = os.path.join('output', file_id)
        if os.path.exists(output_path):
            return output_path
        
        return None 