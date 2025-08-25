from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from typing import List
import os

def compile_video(image_files: List[str], audio_files: List[str], output_filename: str, fps: int = 24) -> str:
    """
    Compile a video from a sequence of images and audio files.
    
    Args:
        image_files (List[str]): List of paths to image files (one per scene).
        audio_files (List[str]): List of paths to audio files (one per scene). Can be empty string for no audio.
        output_filename (str): The output video file path.
        fps (int): Frames per second for the video.
        
    Returns:
        str: The path to the compiled video.
    """
    clips = []
    for image_file, audio_file in zip(image_files, audio_files):
        # Create a clip for the image
        clip = ImageClip(image_file)
        
        # If there's an audio file for this scene, set its duration to the audio length
        if audio_file and os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            try:
                audio_clip = AudioFileClip(audio_file)
                clip = clip.set_duration(audio_clip.duration)
                clip = clip.set_audio(audio_clip)
            except Exception as e:
                print(f"Error processing audio {audio_file}: {e}")
                clip = clip.set_duration(3)  # Fallback duration
        else:
            # If no audio, set a fixed duration (e.g., 3 seconds)
            clip = clip.set_duration(3)
            
        clips.append(clip)
    
    # Concatenate all clips
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_filename, fps=fps)
    return output_filename