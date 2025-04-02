def read_text_file(file_path, default_text="这是一个示例文本，用于测试Azure文本转语音服务。"):
    """读取文本文件，如果文件不存在则创建并写入默认文本
    
    Args:
        file_path (str): 文本文件路径
        default_text (str): 默认文本，当文件不存在时使用
        
    Returns:
        str: 文件内容
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(default_text)
        return default_text

