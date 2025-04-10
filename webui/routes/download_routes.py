from flask import jsonify, send_file
from models.file_handler import FileHandler

class DownloadRoutes:
    def __init__(self, file_handler):
        self.file_handler = file_handler

    def download_video(self, file_id):
        """下载生成的视频"""
        try:
            video_path = self.file_handler.get_video_path(file_id)
            if not video_path:
                return jsonify({"error": "视频文件不存在"})
            
            return send_file(
                video_path,
                as_attachment=True,
                download_name=file_id,
                mimetype='video/mp4'
            )
            
        except Exception as e:
            return jsonify({"error": str(e)}) 