import base64
import mimetypes
import os
from google import genai
from google.genai import types
from typing import Optional

class ImageAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    def generate_image(self, prompt: str, output_filename: str = "output.png") -> str:
        """
        Generate an image from a text prompt using Gemini.
        
        Args:
            prompt (str): The text prompt for image generation.
            output_filename (str): The filename to save the image.
            
        Returns:
            str: Path to the generated image file.
        """
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                response_modalities=["IMAGE", "TEXT"],
            )

            # Generate the image
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=contents,
                config=generate_content_config,
            )

            # Extract and save the image data
            if (response.candidates and 
                response.candidates[0].content and 
                response.candidates[0].content.parts and
                response.candidates[0].content.parts[0].inline_data):
                
                inline_data = response.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                
                # Determine the file extension
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                
                # Ensure the output filename has the right extension
                if not output_filename.endswith(file_extension):
                    output_filename = os.path.splitext(output_filename)[0] + file_extension
                
                # Save the file
                with open(output_filename, "wb") as f:
                    f.write(data_buffer)
                
                print(f"Image saved to: {output_filename}")
                return output_filename
            else:
                raise ValueError("No image data found in response")
                
        except Exception as e:
            print(f"Error generating image: {e}")
            # Fallback: create an empty file to avoid breaking the pipeline
            with open(output_filename, "wb") as f:
                f.write(b"")
            return output_filename