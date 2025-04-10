from datetime import datetime
from models.generate_audio_srt_to_video import generate_audio_srt_to_video
import os

class VideoProcessor:
    def __init__(self, task_manager):
        self.task_manager = task_manager

    def process_video(self, task_id, text_file, voice_name, img_path):
        """处理视频生成任务"""
        try:
            # 更新任务状态
            self.task_manager.update_task_status(
                task_id,
                "processing",
                progress=10,
                message="正在准备处理环境..."
            )
            self.task_manager.tasks[task_id]["started_at"] = datetime.now().isoformat()

            # 更新任务状态
            self.task_manager.update_task_status(
                task_id,
                "processing",
                progress=15,
                message="正在生成音频和字幕..."
            )

            # 更新任务状态
            self.task_manager.update_task_status(
                task_id,
                "processing",
                progress=20,
                message="正在生成视频..."
            )

            # 生成视频
            output_path = generate_audio_srt_to_video(text_file, voice_name, img_path)
            video_filename = os.path.basename(output_path)

            # 更新任务状态
            self.task_manager.update_task_status(
                task_id,
                "completed",
                progress=100,
                message="处理完成"
            )
            self.task_manager.tasks[task_id]["file_id"] = video_filename
            self.task_manager.tasks[task_id]["completed_at"] = datetime.now().isoformat()

            return output_path

        except Exception as e:
            # 更新任务状态为失败
            self.task_manager.update_task_status(
                task_id,
                "failed",
                message=f"处理失败: {str(e)}"
            )
            self.task_manager.tasks[task_id]["error"] = str(e)
            raise 