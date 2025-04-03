#调用stable diffusion进行文生图
import requests
import json
import base64
import os
import time
import configparser
from datetime import datetime
from .ai_api import guiji_optimization_text,retry_on_failure


def get_sd_prompt(text):
    prompt =  """
            
            # 能力
            1. 能够根据输入的文本生成标准的文成图英文提示词
            2. 突出文本的关键特征（人物，场景，衣服特征，时间，镜头）
            3. 人物的权重总是最大，其次是场景
            4. 我需要你生成一个高质量的文成图提示词，不要有其他内容,不要有其他的标点符号
            5. 需要描绘出一个场景，根据输入的有限的文本，在原文的意思上扩展内容
            6. 提示词格式示例必须是英文: （人物特征 1.0），(特征 0.5)， 。。。。

            # 限制：
            1. 只返回文成图英文提示词，不要有其他内容,不要有其他的标点符号
            2. Stable Diffusion提示词标准格式采用分层结构，通过英文逗号分隔关键词并控制权重，包含质量强化、主体特征、环境氛围等模块，使用括号( )增强权重、中括号[ ]降权、冒号:自定义权重值，总词数建议≤75个
            3. 总是头部追加提示词：mxiandaij,best quality, ultra detailed,highres,colorful,incredibly absurdres
"""
    text = guiji_optimization_text(text,prompt)
    return text

@retry_on_failure(max_retries=5, delay=2)
def sd_to_pic(text,output_path):
    output_path = output_path + '/temp'
    prompt = get_sd_prompt(text)
    print(f"生成的提示词: {prompt}")
    
    # 调用SD API生成图像
    try:
        image_path = sd_api(prompt,output_path)
        if image_path:
            print(f"成功生成图片: {image_path}")
            return image_path
        else:
            print("图片生成失败，返回None")
            return None
    except Exception as e:
        print(f"图片生成失败: {str(e)}")
        return None

@retry_on_failure(max_retries=3, delay=2)
def sd_api(prompt,output_path):
    #调用sd api进行文生图
    
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    
    #从DEFAULT获取sd_api_url
    sd_api_url = config.get('DEFAULT', 'sd_api_url') + "/sdapi/v1/txt2img"
    
    # 构建请求参数
    payload = {
        "prompt": prompt,
        "negative_prompt": "Low resolution,bad anatomy,bad hand,text,error,missing finger,not missing hand,extra digit,less digit,crop,worst quality,watermark,username,blur,Low resolution,Bad anatomy,bad hand,text,error,extra digit,less digit,crop,worst quality,Low quality,Normal quality,jpeg Workpiece,Signature,watermark,username,blurry,ugly,pregnant,vore,copy,sick,mut ilated,tran nsexual,androgynous,long neck,mutated hand,poorly painted hand,poorly painted face,mutated,deformed,blurred,anatomically bad,deformed limb,redundant limb,cloned face,disfigured,Rough proportion,(((lack of arms))),(((lack of leg)), (arm) (extra)),((extra legs)),((extra legs)),pubic hair,plump,bad leg,the wrong leg,the user name,fuzzy,bad foot,(anatomy:1.3),(extra limbs:1.35),(draw well face:1.4),(Signature :1.2),(Artist name :1.2),(Watermark :1.2),EasyNegative,Painting,drawing,(worst quality :2),(Low quality :2),(Normal quality :2),low resolution,Normal quality,((Monochrome)),((Grayscale)),skin spots,Acne,skin blemishes,age spots,Glans head,more fingers,less fingers,odd fingers,bad hands,bad legs,more legs,missing clitoris,bad clitoris,fused crotch,bad muscle crotch,bad stomach,bad belly,easy negative (squint :1.2) Easy negative,coat,coat,coat,",
        "width": 1280,
        "height": 720,
        "num_inference_steps": 20,
        "guidance_scale": 7,
        "seed": -1,  # -1表示随机种子
        "sampler_index": " Euler a",
        # 高分辨率修复配置
        # "enable_hr": True,  # 启用高分辨率修复
        # "hr_scale": 2.0,    # 放大倍数
        
 
    }
    
    try:
        # 发送请求
        response = requests.post(sd_api_url, json=payload)
        response.raise_for_status()
        r = response.json()
        
        # 创建保存图片的目录
        output_dir = output_path
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存图片
        for i, img_data in enumerate(r['images']):
            # 解码图片数据
            image = base64.b64decode(img_data)
            
            # 生成文件名（使用时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_file = os.path.join(output_dir, f"sd_generated_{timestamp}_{i}.png")
            
            # 保存图片
            with open(img_file, "wb") as f:
                f.write(image)
            
            print(f"已保存图片: {img_file}")
        return img_file
        
    except Exception as e:
        print(f"Stable Diffusion API 调用出错: {str(e)}")
        raise  # 重新抛出异常以触发重试机制


