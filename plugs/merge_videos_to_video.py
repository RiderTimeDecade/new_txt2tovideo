import os
import subprocess
import glob
from typing import List, Optional
import time
from .add_effect_video import merge_videos_with_blend_lighten



def mult_to_one(input_dir: str = "output", 
                output_file: str = "", 
                file_pattern: str = "[0-9]*.mp4",
                sort_by_number: bool = True) -> None:
    """
    将多个MP4视频文件合并为一个视频文件
    
    :param input_dir: 输入视频文件所在目录
    :param output_file: 输出视频文件路径
    :param file_pattern: 文件匹配模式
    :param sort_by_number: 是否按文件名中的数字排序
    """
    # 使用时间生成文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"output/temp/merged_{timestamp}.mp4"
    try:
        # 确保输出目录存在
        # os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 获取所有符合条件的视频文件
        video_files = glob.glob(os.path.join(input_dir, file_pattern))
        
        if not video_files:
            raise FileNotFoundError(f"没有找到符合 {file_pattern} 的视频文件")
        
        print(f"找到 {len(video_files)} 个视频文件")
        
        # 按文件名中的数字排序（如果需要）
        if sort_by_number:
            import re
            def extract_number(filename):
                # 从文件名中提取数字，专门处理"1-xx.mp4"格式
                match = re.search(r'^(\d+)', os.path.basename(filename))
                return int(match.group(1)) if match else 0
            
            video_files.sort(key=extract_number)
        else:
            # 普通字母顺序排序
            video_files.sort()
        
        # 创建临时文件列表
        temp_list_file = os.path.join(input_dir, "temp_file_list.txt")
        
        with open(temp_list_file, "w", encoding="utf-8") as f:
            for video_file in video_files:
                f.write(f"file '{os.path.abspath(video_file)}'\n")
        
        # 使用FFmpeg合并视频（使用concat demuxer方式，不会重新编码，速度快）
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', temp_list_file,
            '-c', 'copy',  # 直接复制流，不重新编码
            output_file
        ]
        
        print("正在合并视频...")
        print(f"命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 删除临时文件列表
        if os.path.exists(temp_list_file):
            os.remove(temp_list_file)
        
        if result.returncode != 0:
            print(f"FFmpeg错误输出: {result.stderr}")
            raise RuntimeError(f"视频合并失败: {result.stderr}")
        
        print(f"视频合并成功: {output_file}")
        
        merge_videos_with_blend_lighten([output_file,"../config/effect/effect.mp4"],f"output/{timestamp}.mp4",watermark_text="FULL")
        #print(f"合并了 {len(video_files)} 个视频文件")
        output_file = f"output/{timestamp}.mp4"
        return output_file
    except Exception as e:
        print(f"视频合并时出错: {str(e)}")
        raise


    

    pass