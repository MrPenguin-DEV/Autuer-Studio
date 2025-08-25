import google.generativeai as genai
from google.genai import types
from typing import Dict, Any
import json
import re

class DirectorAgent:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model
        self.client = genai.Client(api_key=api_key)
    
    def generate_story(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a structured story from a prompt.
        
        Args:
            prompt (str): The story prompt.
            
        Returns:
            Dict[str, Any]: A JSON object with the story structure.
        """
        # Create a detailed prompt for the model to generate structured JSON
        structured_prompt = f"""
        You are a storytelling AI. Generate a short animated story based on the following prompt: {prompt}
        
        The story should be broken down into 3-5 scenes. Each scene should have:
        - id: A unique identifier (number).
        - description: A detailed description of the scene's visuals.
        - dialogue: A list of dialogue lines (if any) for the scene. Each line should be in the format "character: line".
        - image_prompt: A detailed text prompt that could be used by an image generation model to create this scene.
        - character_prompt: (Optional) For scenes focusing on a character, a more specific prompt for character image generation.
        
        Output the story in JSON format with the following structure:
        {{
          "title": "Story Title",
          "scenes": [
            {{
              "id": 1,
              "description": "Scene description",
              "dialogue": ["character: line"],
              "image_prompt": "Prompt for image generation",
              "character_prompt": ""
            }}
          ]
        }}
        
        Make sure the output is valid JSON that can be parsed by Python's json.loads() function.
        """
        
        # Use the client with thinking budget for complex reasoning
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=structured_prompt),
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,  # Unlimited thinking
                ),
            ),
        )
        
        # Extract the text from the response
        response_text = response.text
        
        # Attempt to parse the response as JSON
        try:
            # First, try to parse directly
            story_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            # If direct parsing fails, try to extract JSON from markdown code block
            try:
                pattern = r'```json\s*(.*?)\s*```'
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    story_json = json.loads(match.group(1))
                else:
                    # Try to find JSON object in the text
                    pattern = r'\{.*\}'
                    match = re.search(pattern, response_text, re.DOTALL)
                    if match:
                        story_json = json.loads(match.group(0))
                    else:
                        raise ValueError("Failed to parse model response as JSON.") from e
            except (json.JSONDecodeError, AttributeError) as e2:
                # If all else fails, create a simple fallback story
                print(f"Failed to parse JSON response: {e2}")
                print(f"Response was: {response_text}")
                story_json = {
                    "title": "Fallback Story",
                    "scenes": [
                        {
                            "id": 1,
                            "description": "A simple scene",
                            "dialogue": ["Narrator: This is a fallback scene."],
                            "image_prompt": "A simple scene",
                            "character_prompt": ""
                        }
                    ]
                }
                
        return story_json