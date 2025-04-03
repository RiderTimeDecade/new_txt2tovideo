import os
import requests
import json
import configparser
from openai import OpenAI
import time
from functools import wraps

def retry_on_failure(max_retries=5, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:  # 最后一次尝试
                        print(f"API 调用最终失败: {str(e)}")
                        return None
                    print(f"API 调用失败，正在进行第 {attempt + 1} 次重试: {str(e)}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


    #根据文本长度依次发送文本每2000字发送一次
    all_text = ""
    for i in range(0, len(text), 2000):
        text_optimization = guiji_optimization_text(text[i:i+2000])
        all_text += text_optimization + "|"
    return [x for x in all_text.split("|") if x.strip()]
#硅基流动接口
@retry_on_failure(max_retries=3, delay=2)
def guiji_optimization_text(
                            text,
                            prompt="""
                    # 能力
                    进行文本分段，一段不要超过30到40个字,使用|分割，不使用换行符
                    # 限制
                    只返回文案数据，不要有其他内容,不使用换行符
                    严格按照要求进行分段，不要有其他内容
                    """
                            ):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('../config/config.ini')
    token = config.get('DEFAULT', 'token')
    api_url = config.get('DEFAULT', 'api_url')
    
    # API 配置
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    textdata = text.replace("\n", " ")
    # 构建提示词
    print(len(textdata))
    
    modle_name = config.get('DEFAULT', 'modle_name')
    payload = {
        "model": modle_name,
        "messages": [
            {
                "role": "system",
                "content": f"""
                    {prompt}
                    # 文案
                    {textdata}
                    
                """
            }
        ],
        "stream": False,
        "max_tokens": 1024,
        "stop": None,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        translated_text = result['choices'][0]['message']['content']
        
        #print(translated_text)
        return translated_text
    except Exception as e:
        print(f"API 调用出错: {str(e)}")
        raise  # 重新抛出异常以触发重试机制

