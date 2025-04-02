import os
import subprocess
from typing import Optional

def merge_to_video(audio_path: str, 
                  srt_path: Optional[str], 
                  effect_path: Optional[str], 
                  pic_path: str, 
                  output_path: str = "output/final_video.mp4") -> None:
    """
    使用 FFmpeg 合成视频（仅合成音频、图片和字幕）
    :param audio_path: 音频文件路径
    :param srt_path: 字幕文件路径（可选）
    :param effect_path: 特效视频路径
    :param pic_path: 背景图片路径
    :param output_path: 输出视频路径
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(pic_path):
            raise FileNotFoundError(f"图片文件 {pic_path} 不存在")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件 {audio_path} 不存在")
        if srt_path and not os.path.exists(srt_path):
            raise FileNotFoundError(f"字幕文件 {srt_path} 不存在")

        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 构建基本的 FFmpeg 命令
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',        # 循环播放图片
            '-framerate', '30',  # 设置帧率
            '-i', pic_path,      # 输入图片
            '-i', audio_path,    # 输入音频
        ]

        # 添加字幕滤镜（如果有字幕文件）
        if srt_path:
            vf = f"subtitles={srt_path}:force_style='FontName=SimHei,FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=1'"
            cmd.extend(['-vf', vf])

        # 添加输出参数
        cmd.extend([
            '-c:v', 'h264',        # 使用 h264 编码器
            '-profile:v', 'main',  # 使用 main profile
            '-preset', 'medium',   # 编码速度预设
            '-tune', 'stillimage', # 优化静态图片
            '-crf', '23',          # 视频质量（0-51，值越小质量越好）
            '-pix_fmt', 'yuv420p', # 使用更广泛支持的像素格式
            '-c:a', 'aac',         # 音频编码器
            '-b:a', '192k',        # 音频比特率
            '-shortest',           # 使用最短输入流的长度
            '-movflags', '+faststart',  # 优化网络播放
            output_path
        ])

        # 执行 FFmpeg 命令
        print("正在执行 FFmpeg 命令...")
        print(f"命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg 错误输出：{result.stderr}")
            raise RuntimeError("FFmpeg 命令执行失败")
        
        print(f"视频已成功生成：{output_path}")
        
    except Exception as e:
        print(f"生成视频时出错：{str(e)}")
        raise
