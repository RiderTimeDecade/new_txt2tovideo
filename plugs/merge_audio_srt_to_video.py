import os
import subprocess
from typing import Optional

def merge_to_video(audio_path: str, 
                  srt_path: Optional[str], 
                  effect_path: Optional[str], 
                  pic_path: str, 
                  output_path: str = "output/final_video.mp4") -> None:
    """
    使用 FFmpeg 合成视频（支持背景图片、音频、字幕和透明特效）
    :param audio_path: 音频文件路径
    :param srt_path: 字幕文件路径（可选）
    :param effect_path: 特效视频路径（可选，需要是带Alpha通道的视频）
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
        if effect_path and not os.path.exists(effect_path):
            raise FileNotFoundError(f"特效文件 {effect_path} 不存在")

        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 先获取音频时长
        probe_cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            audio_path
        ]
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("获取音频时长失败")
        
        try:
            audio_duration = float(result.stdout.strip())
        except ValueError:
            raise RuntimeError(f"无法解析音频时长: {result.stdout}")
        
        print(f"音频时长: {audio_duration} 秒")

        # 构建基本的 FFmpeg 命令
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',         # 循环播放图片
            '-i', pic_path,       # 输入图片
            '-i', audio_path,     # 输入音频
        ]

        # 如果有特效，添加特效输入
        if effect_path:
            cmd.extend([
                '-stream_loop', '-1',  # 循环播放特效
                '-i', effect_path
            ])

        # 构建滤镜链
        filter_complex = ""
        
        # 处理背景图片和特效
        if effect_path:
            # 创建滤色混合
            filter_complex = (
                # 背景图片格式转换
                '[0:v]format=rgba[bg];'
                # 特效格式转换和缩放
                '[2:v]format=rgba,scale=1280:720:flags=lanczos[fx];'
                # 应用滤色混合
                '[bg][fx]blend=all_mode=screen:all_opacity=1:eof_action=repeat'
            )
            
            # 如果有字幕，添加字幕
            if srt_path:
                srt_path = srt_path.replace('\\', '/').replace(':', '\\:')
                filter_complex += f"[blend];[blend]subtitles='{srt_path}':force_style='FontName=SimHei,FontSize=24'"
                
            # 添加最终输出标签
            filter_complex += '[v]'
        else:
            # 只有背景和字幕
            if srt_path:
                srt_path = srt_path.replace('\\', '/').replace(':', '\\:')
                filter_complex = f"[0:v]format=yuv420p,subtitles='{srt_path}':force_style='FontName=SimHei,FontSize=24'[v]"
            else:
                filter_complex = "[0:v]format=yuv420p[v]"

        # 添加滤镜链到命令
        cmd.extend(['-filter_complex', filter_complex])

        # 指定输出流映射
        cmd.extend([
            '-map', '[v]',
            '-map', '1:a'
        ])

        # 添加输出参数
        cmd.extend([
            '-c:v', 'libx264',     # 视频编码器
            '-tune', 'stillimage', # 优化静态图片
            '-c:a', 'aac',        # 音频编码器
            '-b:a', '192k',       # 音频比特率
            '-pix_fmt', 'yuv420p',# 像素格式
            '-t', str(audio_duration),  # 设置输出视频的时长与音频相同
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
