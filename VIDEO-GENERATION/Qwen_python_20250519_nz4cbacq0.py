from moviepy.editor import VideoFileClip, AudioFileClip
import os

def get_file_path(prompt):
    while True:
        path = input(prompt).strip()
        if os.path.exists(path):
            return path
        else:
            print("❌ File not found. Please try again.")

def merge_audio_video(video_path, audio_path, output_path):
    try:
        audio = AudioFileClip(audio_path)
        required_duration = audio.duration + 5  # Add 5 seconds padding

        video = VideoFileClip(video_path).resize(height=720)

        # Loop video to match required duration
        looping_video = video.loop(duration=required_duration)

        # Set audio to looping video
        final_video = looping_video.set_audio(audio)

        # Write final video with MoviePy's built-in logger
        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",
            audio_bitrate="192k",
            fps=final_video.fps
        )

        print(f"\n✅ Successfully saved merged video to: {output_path}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    print("🎥 Welcome to the Audio-Video Merger (Loops video to fit audio + 5 sec)")
    
    mp3_file = get_file_path("🔊 Enter the full path to your MP3 file: ")

    use_default = input("🖼️ Use default 'video.mp4'? (y/n): ").lower().strip()
    if use_default == 'y':
        mp4_file = r"VIDEO-GENERATION\Video.mp4"
        if not os.path.exists(mp4_file):
            print(f"❌ Default video file '{mp4_file}' not found.")
            mp4_file = get_file_path("📹 Enter the full path to your MP4 video file: ")
    else:
        mp4_file = get_file_path("📹 Enter the full path to your MP4 video file: ")

    output_file = "output_720p.mp4"

    print("\n🔄 Merging audio and video...")
    merge_audio_video(mp4_file, mp3_file, output_file)
