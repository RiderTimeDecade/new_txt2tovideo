from azure.cognitiveservices.speech import ResultReason
from plugs.merge_audio_srt_to_video import merge_to_video
from plugs.merge_videos_to_video import mult_to_one

# 导入插件模块
from plugs.config import create_speech_config, DEFAULT_SUBSCRIPTION_KEY, DEFAULT_REGION, DEFAULT_VOICE_NAME
from plugs.file_utils import read_text_file
from plugs.speech_synthesis import synthesize_speech_with_timestamps
from plugs.srt_generator import generate_srt_entries, write_srt_file
from plugs.sd_txt_to_pic import sd_to_pic
import os


def generate_audio_srt_to_video(text_path,voice_name,img_path=None):
    """主函数"""
    try:
        # 读取文本
        text = read_text_file(text_path)
        print(f"成功读取文本文件: {text_path}")
        
        # 确保输出目录存在
        os.makedirs("output/temp", exist_ok=True)
        
        # # 文生图
        if not (img_path):
            print("正在生成背景图片...")
            img_path = sd_to_pic(text[0:200],"output")
            print(f"背景图片路径: {img_path}")
        else:
            print("使用传入图片")
        # 每 2000 个字符分割一次
        text_chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
        print(f"文本已分割为 {len(text_chunks)} 个片段")
        
        # 生成视频片段
        for i, text_chunk in enumerate(text_chunks):
            print(f"正在生成第 {i + 1} 个音频和字幕文件...")
            generate_audio_srt_chunk(text_chunk, i + 1, voice_name)
            
            # 生成单个视频片段
            audio_path = f"output/temp/{i + 1}.wav"
            srt_path = f"output/temp/{i + 1}.srt"
            effect_path = None  # 不使用特效
            output_path = f"output/temp/{i + 1}.mp4"
            
            print(f"正在生成视频片段 {i + 1}...")
            print(f"音频路径: {audio_path}")
            print(f"字幕路径: {srt_path}")
            print(f"图片路径: {img_path}")
            print(f"输出路径: {output_path}")
            
            merge_to_video(audio_path, srt_path, effect_path, img_path, output_path)
            print(f"视频片段 {i + 1} 生成完成")
        
        # 合并所有视频片段
        print("正在合并所有视频片段...")
        video_dir = "output/temp"
        #output_file = "output/final_video.mp4"
        video_path = mult_to_one(video_dir)
        #print(f"视频合并完成: {output_file}")
        
        return video_path
        
    except Exception as e:
        print(f"生成视频时出错: {str(e)}")
        raise

def generate_audio_srt_chunk(text_chunk,file_name,voice_name):
    speech_config = create_speech_config(
        subscription_key=DEFAULT_SUBSCRIPTION_KEY,
        region=DEFAULT_REGION,
        voice_name=voice_name
    )
    text_chunk = text_chunk.replace("\n", " ")
    
    # 合成语音并获取时间戳
    result, timestamps = synthesize_speech_with_timestamps(text_chunk, speech_config,file_name)
    
    # 生成SRT条目
    srt_entries = generate_srt_entries(text_chunk, timestamps,voice_name)
    
    # 写入SRT文件
    write_srt_file(srt_entries, f"output/temp/{file_name}.srt")