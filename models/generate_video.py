from plugs.merge_audio_srt_to_video import merge_to_video

def generate_video(audio_path, srt_path, effect_path, pic_path, output_path):
    """生成视频的入口函数
    
    Args:
        audio_path (str): 音频文件路径
        srt_path (str): 字幕文件路径
        effect_path (str): 特效视频文件路径
        pic_path (str): 背景图片路径
        output_path (str): 输出视频路径
    """
    merge_to_video(audio_path, srt_path, effect_path, pic_path, output_path)

