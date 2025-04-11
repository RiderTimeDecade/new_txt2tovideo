from models.generate_audio_srt_to_video import generate_audio_srt_to_video
from plugs.merge_videos_to_video import mult_to_one
from plugs.sd_txt_to_pic import sd_to_pic
import os
import shutil

if __name__ == "__main__":
    # 确保输出目录存在

    
    #先清空 temp目录文件
    if os.path.exists("output/temp"):
        # 移除目录下的所有文件和子目录
        shutil.rmtree("output/temp")
    
    #确保 temp目录存在
    os.makedirs("output/temp", exist_ok=True)
    
    # 一键生成视频
    generate_audio_srt_to_video(text_path="data/1.txt",voice_name="en-US-AriaNeural")

    
