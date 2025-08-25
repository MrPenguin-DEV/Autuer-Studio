#!/usr/bin/env python3
"""
Example usage of Auteur Studio in Google Colab.
"""

import os
from auteur_studio import Project, config
from auteur_studio.utils.colab_utils import setup_comfyui, start_comfyui, setup_ngrok
from google.colab import files

def main():
    # Set your Gemini API key
    os.environ['GEMINI_API_KEY'] = 'your-api-key-here'
    
    # Load configuration
    cfg = config.load_config()
    
    # Set up ComfyUI (optional)
    # setup_comfyui()
    # comfyui_process = start_comfyui()
    # public_url = setup_ngrok()
    # print(f"ComfyUI is accessible at: {public_url}")
    
    # Create a project
    my_project = Project(name="my_animation", config=cfg)
    my_project.initialize()
    
    # Generate a story
    my_project.generate_story("A story about a robot discovering a flower on a barren planet")
    
    # Generate audio
    my_project.generate_audio()
    
    # Generate images (using Gemini Image Generation)
    my_project.generate_images()
    
    # Compile the final video
    video_path = my_project.compile_video()
    
    # Download the result
    files.download(video_path)

if __name__ == "__main__":
    main()