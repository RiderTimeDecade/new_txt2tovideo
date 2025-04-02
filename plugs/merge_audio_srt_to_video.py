import os
import subprocess
import shutil

def merge_to_video(audio_path, srt_path, effect_path, pic_path, output_path="output/final_video.mp4"):
    """使用 ffmpeg 合并音频、字幕、特效和图片到视频
    
    Args:
        audio_path (str): 音频文件路径
        srt_path (str): 字幕文件路径
        effect_path (str): 特效视频文件路径
        pic_path (str): 背景图片路径
        output_path (str): 输出视频路径
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 临时文件路径
        temp_video = "output/temp_video.mp4"
        os.makedirs("output", exist_ok=True)
        
        # 1. 首先将图片转换为视频
        # 获取音频时长
        duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{audio_path}"'
        duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
        
        # 将图片转换为视频
        img_to_video_cmd = f'ffmpeg -y -loop 1 -i "{pic_path}" -c:v libx264 -t {duration} -pix_fmt yuv420p -vf "scale=1920:1080" "{temp_video}"'
        subprocess.run(img_to_video_cmd, shell=True, check=True)
        
        # 2. 如果有特效视频，将其与背景合成
        if effect_path and os.path.exists(effect_path):
            temp_video_with_effect = "output/temp_video_with_effect.mp4"
            
            # 使用overlay直接叠加特效，使用更强的混合模式
            overlay_cmd = (
                f'ffmpeg -y -i "{temp_video}" -i "{effect_path}" '
                f'-filter_complex "[0:v][1:v]overlay=0:0:enable=\'between(t,0,{duration})\'" '
                f'-c:v libx264 -t {duration} "{temp_video_with_effect}"'
            )
            subprocess.run(overlay_cmd, shell=True, check=True)
            
            # 更新临时视频路径
            shutil.move(temp_video_with_effect, temp_video)
        
        # 3. 添加音频和字幕（调整字幕位置和样式）
        final_cmd = f'ffmpeg -y -i "{temp_video}" -i "{audio_path}" -vf "subtitles={srt_path}:force_style=\'FontName=PingFangSC-Regular,FontSize=30,PrimaryColour=&H00FFFF,OutlineColour=&H000000,Outline=3,MarginV=100\'" -c:v libx264 -c:a aac -shortest "{output_path}"'
        subprocess.run(final_cmd, shell=True, check=True)
        
        # 清理临时文件
        if os.path.exists(temp_video):
            os.remove(temp_video)
            
        print(f"视频已成功生成：{output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 命令执行失败：{str(e)}")
    except Exception as e:
        print(f"生成视频时出错：{str(e)}")
