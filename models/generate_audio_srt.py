from azure.cognitiveservices.speech import ResultReason

# 导入插件模块
from plugs.config import create_speech_config, DEFAULT_SUBSCRIPTION_KEY, DEFAULT_REGION, DEFAULT_VOICE_NAME
from plugs.file_utils import read_text_file
from plugs.speech_synthesis import synthesize_speech_with_timestamps
from plugs.srt_generator import generate_srt_entries, write_srt_file

def generate_audio_srt(text_path):
    """主函数"""
    # 读取文本
    text = read_text_file(text_path)
    #每 2000 个字符分割一次
    text_chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    #file_name 为 for 循环的 index
    for i, text_chunk in enumerate(text_chunks):
        print(f"正在生成第 {i + 1} 个音频和字幕文件...")
        generate_audio_srt_chunk(text_chunk,i + 1)
    # 初始化配置
    

def generate_audio_srt_chunk(text_chunk,file_name):
    speech_config = create_speech_config(
        subscription_key=DEFAULT_SUBSCRIPTION_KEY,
        region=DEFAULT_REGION,
        voice_name=DEFAULT_VOICE_NAME
    )
    
    # 合成语音并获取时间戳
    result, timestamps = synthesize_speech_with_timestamps(text_chunk, speech_config,file_name)
    
    # 生成SRT条目
    srt_entries = generate_srt_entries(text_chunk, timestamps)
    
    # 写入SRT文件
    write_srt_file(srt_entries, f"output/temp/{file_name}.srt")