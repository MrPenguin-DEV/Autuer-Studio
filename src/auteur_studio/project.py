import os
import json
from typing import Dict, Any, List
from .agents.director_agent import DirectorAgent
from .agents.tts_agent import TTSAgent
from .agents.image_agent import ImageAgent
from .utils import comfyui_utils, video_utils

class Project:
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.project_root = os.path.join(config['paths']['project_root'], name)
        self.assets_dir = os.path.join(self.project_root, 'assets')
        self.script_path = os.path.join(self.project_root, 'script.json')
        self.story = None
        
        # Create directories
        os.makedirs(self.project_root, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Initialize agents
        self.director = DirectorAgent(api_key=config['gemini']['api_key'], model=config['gemini']['model'])
        self.tts_agent = TTSAgent(api_key=config['gemini']['api_key'])
        self.image_agent = ImageAgent(api_key=config['gemini']['api_key'])
    
    def initialize(self):
        """Initialize the project structure."""
        # We already created directories, so just ensure the script file is reset if it exists.
        if os.path.exists(self.script_path):
            os.remove(self.script_path)
    
    def generate_story(self, prompt: str):
        """Generate the story and save it to the project directory."""
        self.story = self.director.generate_story(prompt)
        with open(self.script_path, 'w') as f:
            json.dump(self.story, f, indent=2)
    
    def generate_audio(self):
        """Generate audio for all dialogue in the story."""
        if self.story is None:
            with open(self.script_path, 'r') as f:
                self.story = json.load(f)
        
        for scene in self.story['scenes']:
            scene_audio_files = []
            for i, line in enumerate(scene['dialogue']):
                # Assuming line is in format "character: text"
                if ':' in line:
                    character, text = line.split(':', 1)
                    audio_filename = f"scene_{scene['id']}_line_{i}.wav"
                    audio_path = os.path.join(self.assets_dir, audio_filename)
                    self.tts_agent.generate_speech(text=text.strip(), character=character.strip(), output_filename=audio_path)
                    scene_audio_files.append(audio_path)
            
            # Store the audio paths in the scene for later use
            scene['audio_files'] = scene_audio_files
        
        # Update the script with audio file paths
        with open(self.script_path, 'w') as f:
            json.dump(self.story, f, indent=2)
    
    def generate_images(self):
        """Generate images for each scene using Gemini Image Generation."""
        if self.story is None:
            with open(self.script_path, 'r') as f:
                self.story = json.load(f)
        
        for scene in self.story['scenes']:
            image_filename = f"scene_{scene['id']}.png"
            image_path = os.path.join(self.assets_dir, image_filename)
            
            # Use the image_prompt from the story, or fallback to description
            prompt = scene.get('image_prompt', scene['description'])
            self.image_agent.generate_image(prompt=prompt, output_filename=image_path)
            scene['image_file'] = image_path
        
        # Update the script with image file paths
        with open(self.script_path, 'w') as f:
            json.dump(self.story, f, indent=2)
    
    def generate_animation(self):
        """Generate animation frames for each scene using ComfyUI."""
        # This method now uses ComfyUI for more advanced animation if available
        # Fall back to simple image generation if ComfyUI is not configured
        if not self.config['comfyui'].get('enabled', False):
            return self.generate_images()
            
        if self.story is None:
            with open(self.script_path, 'r') as f:
                self.story = json.load(f)
        
        comfyui_base_url = self.config['comfyui']['base_url']
        
        # Check if ComfyUI is available
        if not comfyui_utils.connect_to_comfyui(comfyui_base_url):
            print("ComfyUI not available, falling back to simple image generation")
            return self.generate_images()
        
        workflow = comfyui_utils.load_workflow(self.config['comfyui']['workflow_api_json'])
        
        for scene in self.story['scenes']:
            # Modify the workflow with the scene's image_prompt
            # This is a placeholder: the actual modification will depend on the workflow structure
            prompt = scene.get('image_prompt', scene['description'])
            
            # Example modification (adjust based on your workflow structure)
            if '6' in workflow and 'inputs' in workflow['6'] and 'text' in workflow['6']['inputs']:
                workflow['6']['inputs']['text'] = prompt
            
            # Queue the prompt
            response = comfyui_utils.queue_prompt(workflow, comfyui_base_url)
            
            # Get the image filename from the response (this depends on the workflow)
            # Example: if the output node has id 14 and output image filename is in 'images'[0]['filename']
            if '14' in response and 'images' in response['14'] and response['14']['images']:
                image_filename = response['14']['images'][0]['filename']
                image_path = comfyui_utils.get_image(image_filename, comfyui_base_url, self.assets_dir)
                scene['image_file'] = image_path
            else:
                # Fallback to simple image generation
                image_filename = f"scene_{scene['id']}.png"
                image_path = os.path.join(self.assets_dir, image_filename)
                self.image_agent.generate_image(prompt=prompt, output_filename=image_path)
                scene['image_file'] = image_path
        
        # Update the script with image file paths
        with open(self.script_path, 'w') as f:
            json.dump(self.story, f, indent=2)
    
    def compile_video(self, output_filename: str = "final_video.mp4") -> str:
        """Compile the final video from all assets."""
        if self.story is None:
            with open(self.script_path, 'r') as f:
                self.story = json.load(f)
        
        image_files = []
        audio_files = []
        for scene in self.story['scenes']:
            image_files.append(scene.get('image_file', ''))
            # For audio, we might have multiple audio files per scene. We'll combine them?
            # For simplicity, we'll take the first audio file or none.
            audio_file = scene.get('audio_files', [])[0] if scene.get('audio_files') else ''
            audio_files.append(audio_file)
        
        output_path = os.path.join(self.project_root, output_filename)
        video_utils.compile_video(image_files, audio_files, output_path)
        return output_path