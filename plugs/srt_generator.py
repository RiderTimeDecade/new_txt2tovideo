def format_time(ms):
    """将毫秒格式化为SRT时间格式
    
    Args:
        ms (float): 毫秒时间
        
    Returns:
        str: 格式化的时间字符串，如 "00:00:01,500"
    """
    sec = ms / 1000
    mins, sec = divmod(sec, 60)
    hours, mins = divmod(mins, 60)
    return f"{int(hours):02}:{int(mins):02}:{int(sec):02},{int(ms%1000):03}"

def split_text_into_sentences(text):
    """将文本分割成合适的句子，处理引号和标点符号
    
    Args:
        text (str): 原始文本
        
    Returns:
        list: 句子列表
    """
    # 定义分句的标点符号
    delimiters = ['。', '！', '？', '…']
    sentences = []
    current_sentence = ""
    quote_stack = []  # 用于追踪引号
    
    for char in text:
        current_sentence += char
        
        # 处理引号
        if char == '「':
            quote_stack.append(char)
        elif char == '」':
            if quote_stack:
                quote_stack.pop()
                # 如果引号已配对完成，且句子以分隔符结尾，则分句
                if not quote_stack and len(current_sentence) > 1 and current_sentence[-2] in delimiters:
                    if current_sentence.strip():
                        sentences.append(current_sentence.strip())
                    current_sentence = ""
            
        # 处理其他分隔符
        elif char in delimiters and not quote_stack:  # 只在不在引号内时分句
            if current_sentence.strip():
                sentences.append(current_sentence.strip())
            current_sentence = ""
            
    # 处理最后一个句子
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
    
    return sentences

def find_sentence_timestamps(sentence, timestamps, start_idx):
    """查找句子对应的时间戳范围
    
    Args:
        sentence (str): 句子文本
        timestamps (list): 时间戳列表
        start_idx (int): 开始查找的索引
        
    Returns:
        tuple: (start_time, end_time, next_idx, matched_chars)
    """
    start_time = None
    end_time = None
    idx = start_idx
    matched_chars = []
    
    # 移除标点符号以便更好地匹配
    clean_sentence = ''.join(char for char in sentence if char not in ['。', '！', '？', '…', '「', '」'])
    sentence_chars = list(clean_sentence)
    current_pos = 0
    
    while idx < len(timestamps) and current_pos < len(sentence_chars):
        current_text = timestamps[idx]['text']
        
        # 检查当前时间戳的文本是否匹配句子中的下一个字符
        matched = False
        for char in current_text:
            if current_pos < len(sentence_chars) and char == sentence_chars[current_pos]:
                if start_time is None:
                    start_time = timestamps[idx]['offset']
                matched_chars.append(char)
                current_pos += 1
                matched = True
        
        if matched:
            end_time = timestamps[idx]['offset'] + timestamps[idx]['duration']
        elif start_time is not None and not any(char in sentence_chars[current_pos:] for char in current_text):
            # 如果已经开始匹配但当前时间戳不包含任何剩余字符，说明句子结束
            break
            
        idx += 1
    
    return start_time, end_time, idx, matched_chars

def generate_srt_entries(text, timestamps):
    """根据时间戳生成SRT条目
    
    Args:
        text (str): 原始文本
        timestamps (list): 时间戳列表
        
    Returns:
        list: SRT条目列表
    """
    sentences = split_text_into_sentences(text)
    srt_entries = []
    idx = 0
    last_end_time = None
    
    for sentence in sentences:
        if not sentence.strip() or idx >= len(timestamps):
            continue
            
        # 查找句子的时间戳
        start_time, end_time, next_idx, matched_chars = find_sentence_timestamps(sentence, timestamps, idx)
        
        if start_time is None or end_time is None:
            continue
            
        # 如果有上一个字幕的结束时间，使用它作为当前字幕的开始时间
        if last_end_time is not None:
            start_time = last_end_time
            
        # 如果有下一句，确保当前句子的结束时间不会超过下一句的开始时间
        if next_idx < len(timestamps):
            next_start = timestamps[next_idx]['offset']
            if next_start < end_time:
                end_time = next_start
            
        srt_entries.append({
            'index': len(srt_entries) + 1,
            'start': start_time,
            'end': end_time,
            'text': sentence.strip()
        })
        
        # 保存当前字幕的结束时间
        last_end_time = end_time
        idx = next_idx
    
    return srt_entries

def write_srt_file(entries, output_file="output.srt"):
    """将SRT条目写入文件
    
    Args:
        entries (list): SRT条目列表
        output_file (str): 输出文件路径
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"{entry['index']}\n")
            f.write(f"{format_time(entry['start'])} --> {format_time(entry['end'])}\n")
            f.write(f"{entry['text']}\n\n")
    print(f"SRT文件已保存至{output_file}") 