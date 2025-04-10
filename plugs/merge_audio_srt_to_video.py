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

        # 一步到位处理所有元素
        cmd = ['ffmpeg', '-y']
        
        # 添加输入
        cmd.extend(['-loop', '1', '-i', pic_path])  # 图片
        cmd.extend(['-i', audio_path])  # 音频
        
        # 如果有特效，添加特效
        filter_complex = []
        # 暂时关闭特效合成功能
        # if effect_path:
        #     cmd.extend(['-stream_loop', '-1', '-i', effect_path])  # 特效
        #     # 确保背景图片转为视频格式
        #     filter_complex.append('[0:v]format=yuv420p[bg]')
        #     # 处理MOV格式特效，保留alpha通道
        #     filter_complex.append('[2:v]scale=1280:720,format=yuva420p[fx]')
        #     # 使用overlay直接叠加特效，自动利用alpha通道
        #     filter_complex.append('[bg][fx]overlay=0:0:format=auto[video]')
        # else:
        filter_complex.append('[0:v]format=yuv420p[video]')
        
        # 如果有字幕，添加字幕
        if srt_path:
            srt_path = srt_path.replace('\\', '/').replace(':', '\\:')
            filter_complex[-1] = filter_complex[-1].replace('[video]', '[videotmp]')
            filter_complex.append(f'[videotmp]subtitles={srt_path}:force_style=\'FontName=Arial Black,FontSize=30,Bold=10,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=3,MarginV=20\'[video]')
        
        # 添加滤镜链
        cmd.extend(['-filter_complex', ';'.join(filter_complex)])
        
        # 设置输出参数
        cmd.extend([
            '-map', '[video]',      # 视频流
            '-map', '1:a',          # 音频流
            '-c:v', 'libx264',      # 视频编码器
            '-preset', 'medium',    # 平衡速度和质量 
            '-tune', 'film',        # 电影内容优化
            '-profile:v', 'high',   # 高质量配置
            '-crf', '18',           # 更高视频质量（值越小质量越高）
            '-color_primaries', 'bt709', # 使用标准色彩原色
            '-color_trc', 'bt709',       # 使用标准传输特性
            '-colorspace', 'bt709',      # 使用标准色彩空间
            '-c:a', 'aac',          # 音频编码器
            '-b:a', '192k',         # 提高音频比特率
            '-pix_fmt', 'yuv420p',  # 像素格式
            '-shortest',            # 使用最短的输入流长度
            '-t', str(audio_duration),  # 视频时长
            output_path
        ])
        
        # 执行命令
        print("正在执行FFmpeg命令...")
        print(f"命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg错误输出: {result.stderr}")
            print(f"FFmpeg标准输出: {result.stdout}")
            raise RuntimeError(f"视频生成失败: {result.stderr}")
        
        print(f"视频已成功生成：{output_path}")
        
    except Exception as e:
        print(f"生成视频时出错：{str(e)}")
        raise
