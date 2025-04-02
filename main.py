from models.generate_audio_srt import generate_audio_srt
from models.generate_video import generate_video





if __name__ == "__main__":
    #generate_audio_srt(text_path="data/1.txt")
    generate_video("output/temp/1.wav", "output/temp/1.srt", "config/effect/effect.mov", "data/pic.png", "output/final_video.mp4")