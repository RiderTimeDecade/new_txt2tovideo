import subprocess

def get_standard_resolution(width, height):
    """
    根据输入分辨率计算最接近的标准16:9分辨率
    常见的16:9分辨率：1920x1080, 1280x720, 854x480
    """
    standard_resolutions = [
        (1920, 1080),
        (1280, 720),
        (854, 480)
    ]
    
    # 计算输入视频的面积
    input_area = width * height
    
    # 找到最接近的标准分辨率
    closest = min(standard_resolutions, 
                 key=lambda x: abs(x[0] * x[1] - input_area))
    
    return closest

def merge_videos_with_blend_lighten(input_files, output_file, watermark_text=None, watermark_position="right_top"):
    """
    使用 blend=lighten 滤镜合并视频，支持特效视频循环播放。
    第一个视频作为基础视频，第二个视频作为特效视频（将循环播放）。
    会自动调整为标准16:9分辨率。

    :param input_files: 输入视频文件路径列表 [基础视频, 特效视频]
    :param output_file: 输出视频文件路径
    :param watermark_text: 水印文字，不为None时添加文字水印
    :param watermark_position: 水印位置，可选：right_top, left_top, right_bottom, left_bottom, center
    """
    if len(input_files) < 2:
        raise ValueError("至少需要两个输入视频文件来应用 blend 滤镜。")

    try:
        # 获取基础视频的分辨率
        probe = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'json',
            input_files[0]
        ], capture_output=True, text=True)
        
        if probe.returncode != 0:
            raise RuntimeError(f"获取视频分辨率失败: {probe.stderr}")
        
        # 解析 JSON 输出
        import json
        try:
            probe_data = json.loads(probe.stdout)
            if not probe_data.get('streams'):
                raise ValueError("未找到视频流信息")
            
            stream = probe_data['streams'][0]
            orig_width = int(stream.get('width', 0))
            orig_height = int(stream.get('height', 0))
            
            if orig_width == 0 or orig_height == 0:
                raise ValueError("无法获取视频分辨率")
                
            print(f"原始视频分辨率: {orig_width}x{orig_height}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"解析视频信息失败: {str(e)}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"视频信息格式错误: {str(e)}")
        
        # 获取标准16:9分辨率
        width, height = get_standard_resolution(orig_width, orig_height)
        print(f"调整后的标准分辨率: {width}x{height}")

        # 水印位置参数
        positions = {
            "right_top": f"w-tw-70:50",
            "left_top": "10:10",
            "right_bottom": "w-tw-10:h-th-10",
            "left_bottom": "10:h-th-10",
            "center": "(w-tw)/2:(h-th)/2"
        }
        
        watermark_pos = positions.get(watermark_position, positions["right_top"])
        print("watermark_pos: ",watermark_pos)
        x, y = watermark_pos.split(":")

        # 构建基本 filter_complex
        filter_complex = (
            f'[0:v]scale={width}:{height},setsar=1[base];'
            f'[1:v]scale={width}:{height},format=yuva420p[scaled];'
            f'[scaled]loop=loop=-1:size=500,setpts=PTS-STARTPTS[loopv];'
            f'[base][loopv]blend=lighten'
        )
        
        # 如果需要添加水印，在blend后添加水印
        if watermark_text:
            # 美化的水印样式 - 橙色描边效果，匹配图片中的效果
            watermark_style = (
                f":fontsize=50"  # 字体尺寸
                f":fontcolor=white"  # 白色字体
                f":fontfile=../config/font/UNSII-2.ttf"  # 使用config/font目录下的字体
                f":borderw=2"  # 边框宽度
                f":bordercolor=0xFFA500"  # 橙色边框
                f":box=0"  # 关闭背景框
                f":shadowcolor=0xE67E22@0.5"  # 添加淡橙色阴影增强立体感
                f":shadowx=2:shadowy=2"  # 阴影偏移
            )
            filter_complex += f",drawtext=text='{watermark_text}':x={x}:y={y}{watermark_style}"
        
        # 添加最终输出标签
        filter_complex += "[outv]"

        # 构建 FFmpeg 命令数组
        command = [
            'ffmpeg',
            '-i', input_files[0],
            '-i', input_files[1],
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '0:a',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'veryfast',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-shortest',
            output_file
        ]
        
        print("执行的命令：", ' '.join(command))
        
        # 执行命令
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg 执行失败: {result.stderr}")
            
        print(f"视频合并成功！输出文件: {output_file}")
        
    except Exception as e:
        print("视频合并过程中出错:", str(e))
        raise

def get_video_duration(video_file):
    """
    获取视频时长（秒）
    """
    try:
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_file
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"获取视频时长失败: {result.stderr}")
        return float(result.stdout.strip())
    except Exception as e:
        print(f"获取视频时长出错: {str(e)}")
        raise

def get_video_info(video_file):
    """
    获取视频的基本信息
    """
    try:
        # 获取分辨率和帧率
        probe_res = subprocess.run([
            'ffprobe', 
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate',
            '-of', 'json',
            video_file
        ], capture_output=True, text=True)
        
        if probe_res.returncode != 0:
            raise RuntimeError(f"获取视频信息失败: {probe_res.stderr}")
        
        # 解析 JSON 输出
        import json
        try:
            probe_data = json.loads(probe_res.stdout)
            if not probe_data.get('streams'):
                raise ValueError("未找到视频流信息")
            
            stream = probe_data['streams'][0]
            width = int(stream.get('width', 0))
            height = int(stream.get('height', 0))
            
            if width == 0 or height == 0:
                raise ValueError("无法获取视频分辨率")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"解析视频信息失败: {str(e)}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"视频信息格式错误: {str(e)}")
        
        # 获取时长
        duration = get_video_duration(video_file)
        
        # 获取标准分辨率
        std_width, std_height = get_standard_resolution(width, height)
        
        return (f"原始分辨率: {width}x{height}, "
                f"标准分辨率: {std_width}x{std_height}, "
                f"时长: {duration:.2f}秒")
    except Exception as e:
        print(f"获取视频信息出错: {str(e)}")
        raise

if __name__ == "__main__":
    # 基础视频和特效视频
    base_video = "data/t.mp4"
    effect_video = "data/effect.mp4"
    output_file = "output_lighten.mp4"
    
    try:
        # 检查视频信息
        print("基础视频信息:", get_video_info(base_video))
        print("特效视频信息:", get_video_info(effect_video))
        
        # 合并视频并添加水印
        merge_videos_with_blend_lighten([base_video, effect_video], output_file, watermark_text="test")
    except Exception as e:
        print("处理失败:", str(e))