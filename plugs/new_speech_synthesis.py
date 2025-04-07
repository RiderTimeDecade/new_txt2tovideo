from azure.cognitiveservices.speech import SpeechSynthesizer, ResultReason, AudioConfig
from azure.cognitiveservices.speech import SpeechSynthesisWordBoundaryEventArgs
import os
from azure.cognitiveservices.speech import SpeechConfig
import azure.cognitiveservices.speech as speechsdk
import time
import re
# 默认配置信息

def text_to_ssml(text,speech_config):

    
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                     xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="{speech_config.speech_synthesis_voice_name[0:5]}">
                <voice name="{speech_config.speech_synthesis_voice_name}">
                    
                    <mstts:silence type="Sentenceboundary-exact" value="300ms"/>
                    <prosody rate="0.9">
                        {text}
                    </prosody>
                </voice>
            </speak>"""
    return ssml
def synthesize_speech_with_timestamps(text, speech_config,file_name, max_retries=10, retry_delay=2):
    """合成语音并返回时间戳，带有重试机制
    
    Args:
        text (str): 要合成的文本
        file_name (str): 输出文件名
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔（秒）
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
    os.makedirs("output/temp", exist_ok=True)
    
    # 创建音频配置
    audio_config = speechsdk.audio.AudioOutputConfig(filename=f"output/temp/{file_name}.wav")
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            # 清空之前的时间戳
            timestamps.clear()
            
            # 创建合成器并绑定事件
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            synthesizer.synthesis_word_boundary.connect(word_boundary_cb)
            
            # 使用SSML进行语音合成
            ssml = text_to_ssml(text,speech_config)
            result = synthesizer.speak_ssml_async(ssml).get()
            
            # 检查结果状态
            if result.reason == ResultReason.SynthesizingAudioCompleted:
                # 检查音频文件是否成功生成
                audio_file = f"output/temp/{file_name}.wav"
                if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:

                    print(f"音频成功生成: {audio_file}")
                    return result, timestamps
                else:
                    print(f"音频文件未生成或为空，尝试重试 ({attempt+1}/{max_retries})")
            else:
                print(f"语音合成失败，原因: {result.reason}，尝试重试 ({attempt+1}/{max_retries})")
                
        except Exception as e:
            print(f"语音合成出错: {str(e)}，尝试重试 ({attempt+1}/{max_retries})")
        
        # 如果不是最后一次尝试，则等待后重试
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    
    # 如果所有重试都失败，抛出异常
    raise RuntimeError(f"语音合成失败，已尝试 {max_retries} 次") 

