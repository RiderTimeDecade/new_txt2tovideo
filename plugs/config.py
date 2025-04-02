from azure.cognitiveservices.speech import SpeechConfig

# 默认配置信息
DEFAULT_SUBSCRIPTION_KEY = "2d8d0e6c7e634cd099d47386085ffc9d"
DEFAULT_REGION = "eastus"
DEFAULT_LANGUAGE = "zh-CN"
DEFAULT_VOICE_NAME = "zh-CN-XiaoxiaoNeural"

def create_speech_config(subscription_key=DEFAULT_SUBSCRIPTION_KEY, 
                         region=DEFAULT_REGION, 
                         voice_name=DEFAULT_VOICE_NAME):
    """创建语音配置
    
    Args:
        subscription_key (str): Azure语音服务订阅密钥
        region (str): Azure区域，例如 "eastus"
        voice_name (str): 语音名称，例如 "zh-CN-XiaoxiaoNeural"
        
    Returns:
        SpeechConfig: 语音配置对象
    """
    speech_config = SpeechConfig(subscription=subscription_key, region=region)
    speech_config.speech_synthesis_voice_name = voice_name
    return speech_config 