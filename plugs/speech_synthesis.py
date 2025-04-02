from azure.cognitiveservices.speech import SpeechSynthesizer, ResultReason, AudioConfig
from azure.cognitiveservices.speech import SpeechSynthesisWordBoundaryEventArgs
import os
import azure.cognitiveservices.speech as speechsdk
def synthesize_speech_with_timestamps(text, speech_config,file_name):
    """合成语音并返回时间戳
    
    Args:
        text (str): 要合成的文本
        speech_config: 语音配置对象
        
    Returns:
        tuple: (result, timestamps) - 合成结果和时间戳列表
    """
    # 存储时间戳的列表
    timestamps = []
    
    def word_boundary_cb(evt: SpeechSynthesisWordBoundaryEventArgs):
        """捕获单词边界事件"""
        timestamps.append({
            'text': evt.text,
            'offset': evt.audio_offset / 10000,  # 转换为毫秒
            'duration': evt.duration.total_seconds() * 1000
        })
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    # 创建音频配置
    audio_config = speechsdk.audio.AudioOutputConfig(filename=f"output/temp/{file_name}.wav")
    
    # 创建合成器并绑定事件
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    synthesizer.synthesis_word_boundary.connect(word_boundary_cb)
    
    # 合成语音
    result = synthesizer.speak_text_async(text).get()
    
    return result, timestamps 