from azure.cognitiveservices.speech import ResultReason
from plugs.merge_audio_srt_to_video import merge_to_video
from plugs.merge_videos_to_video import mult_to_one

# 导入插件模块
from plugs.config import create_speech_config, DEFAULT_SUBSCRIPTION_KEY, DEFAULT_REGION, DEFAULT_VOICE_NAME
from plugs.file_utils import read_text_file
from plugs.speech_synthesis import synthesize_speech_with_timestamps
from plugs.srt_generator import generate_srt_entries, write_srt_file
from plugs.sd_txt_to_pic import sd_to_pic


def generate_audio_srt_to_video(text_path,voice_name):
    """主函数"""
    # 读取文本
    text = read_text_file(text_path)
    #每 2000 个字符分割一次
    # 文生图
    
    #img_path = sd_to_pic(text[0:200],"output")
    

    img_path = "data/pic.png"


    text_chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    #file_name 为 for 循环的 index
    for i, text_chunk in enumerate(text_chunks):
        print(f"正在生成第 {i + 1} 个音频和字幕文件...")
        generate_audio_srt_chunk(text_chunk,i + 1,voice_name)
        #生成单个视频片段
        audio_path = f"output/temp/{i + 1}.wav"
        srt_path = f"output/temp/{i + 1}.srt"
        effect_path = f"config/effect/effect.mov"
        output_path = f"output/temp/{i + 1}.mp4"

        merge_to_video(audio_path, srt_path, effect_path, img_path, output_path)
        

    video_dir = "output/temp"
    mult_to_one(video_dir)
   

def generate_audio_srt_chunk(text_chunk,file_name,voice_name):
    speech_config = create_speech_config(
        subscription_key=DEFAULT_SUBSCRIPTION_KEY,
        region=DEFAULT_REGION,
        voice_name=voice_name
    )
    
    # 合成语音并获取时间戳
    result, timestamps = synthesize_speech_with_timestamps(text_chunk, speech_config,file_name)
    
    # 生成SRT条目
    srt_entries = generate_srt_entries(text_chunk, timestamps)
    
    # 写入SRT文件
    write_srt_file(srt_entries, f"output/temp/{file_name}.srt")