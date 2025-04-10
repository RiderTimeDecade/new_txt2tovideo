import json
from flask import jsonify

class VoiceRoutes:
    def get_voices(self):
        """获取可用的语音列表"""
        try:
            with open('../config/voice/voices.json', 'r', encoding='utf-8') as f:
                voices_data = json.load(f)
            
            # 将嵌套的声音配置转换为列表格式
            voices = []
            for category, voice_dict in voices_data.items():
                for voice_name, voice_id in voice_dict.items():
                    voices.append({
                        "id": voice_id,
                        "name": f"{category}-{voice_name}"
                    })
            
            return jsonify({"voices": voices})
        except Exception as e:
            return jsonify({"error": str(e)}) 