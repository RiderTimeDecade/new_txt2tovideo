import subprocess

def merge_videos_with_blend_lighten(input_files, output_file):
    """
    使用 blend=lighten 滤镜合并视频，支持特效视频循环播放。
    第一个视频作为基础视频，第二个视频作为特效视频（将循环播放）。

    :param input_files: 输入视频文件路径列表 [基础视频, 特效视频]
    :param output_file: 输出视频文件路径
    """
    if len(input_files) < 2:
        raise ValueError("至少需要两个输入视频文件来应用 blend 滤镜。")

    # 获取基础视频的分辨率
    probe = subprocess.run([
        'ffprobe', 
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=s=x:p=0',
        input_files[0]
    ], capture_output=True, text=True)
    width, height = map(int, probe.stdout.strip().split('x'))

    # 构建输入参数
    input_args = "".join([f"-i \"{file}\" " for file in input_files])
    
    # 构建 filter_complex
    # 1. 调整特效视频的大小以匹配基础视频
    # 2. 使用 loop 滤镜使特效视频循环播放
    # 3. 使用 blend=lighten 合并视频
    filter_complex = f"""
        [1:v]scale={width}:{height},format=yuva420p[scaled];
        [scaled]loop=loop=-1:size=500,setpts=PTS-STARTPTS[loopv];
        [0:v][loopv]blend=lighten[outv]
    """

    # 构建完整的 FFmpeg 命令
    command = f"""ffmpeg {input_args} -filter_complex "{filter_complex}" \
            -map "[outv]" -map 0:a \
            -c:v libx264 -crf 23 -preset veryfast \
            -c:a aac -b:a 128k \
            -shortest \
            "{output_file}" """
    
    print("执行的命令：", command)
    
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"视频合并成功！输出文件: {output_file}")
    except subprocess.CalledProcessError as e:
        print("视频合并过程中出错:", e)

def get_video_duration(video_file):
    """
    获取视频时长（秒）
    """
    command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_file}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return float(result.stdout.strip())

def get_video_info(video_file):
    """
    获取视频的基本信息
    """
    # 获取分辨率
    probe_res = subprocess.run([
        'ffprobe', 
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate',
        '-of', 'json',
        video_file
    ], capture_output=True, text=True)
    
    # 获取时长
    duration = get_video_duration(video_file)
    
    return f"分辨率: {probe_res.stdout.strip()}, 时长: {duration:.2f}秒"

if __name__ == "__main__":
    # 基础视频和特效视频
    base_video = "data/t.mp4"
    effect_video = "data/effect.mp4"
    output_file = "output_lighten.mp4"
    
    # 检查视频信息
    print("基础视频信息:", get_video_info(base_video))
    print("特效视频信息:", get_video_info(effect_video))
    
    # 合并视频
    merge_videos_with_blend_lighten([base_video, effect_video], output_file)