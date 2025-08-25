import base64
import mimetypes
import os
import re
import struct
from google import genai
from google.genai import types
from typing import Optional

class TTSAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.voice_mapping = {
            "narrator": "Zephyr",
            "default": "Puck",
            "male": "Zephyr", 
            "female": "Puck",
            "robot": "Robot",
            "child": "Child"
        }
    
    def parse_audio_mime_type(self, mime_type: str) -> dict:
        """Parses bits per sample and rate from an audio MIME type string."""
        bits_per_sample = 16
        rate = 24000

        # Extract rate from parameters
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass

        return {"bits_per_sample": bits_per_sample, "rate": rate}
    
    def convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """Generates a WAV file header for the given audio data and parameters."""
        parameters = self.parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", chunk_size, b"WAVE", b"fmt ", 16, 1,
            num_channels, sample_rate, byte_rate, block_align,
            bits_per_sample, b"data", data_size
        )
        return header + audio_data
    
    def get_voice_config(self, character: Optional[str] = None):
        """Get the appropriate voice configuration based on character."""
        voice_name = self.voice_mapping.get(character, self.voice_mapping["default"])
        
        return types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker=character or "Speaker",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        ),
                    ),
                ]
            ),
        )
    
    def generate_speech(self, text: str, character: Optional[str] = None, output_filename: str = "output.wav") -> str:
        """
        Generate speech from text using Gemini TTS.
        
        Args:
            text (str): The text to convert to speech.
            character (str, optional): The character name to influence voice selection.
            output_filename (str): The filename to save the audio.
            
        Returns:
            str: Path to the generated audio file.
        """
        try:
            # Prepare the content with the character name if provided
            speech_text = f"{character}: {text}" if character else text
            
            # Generate content with TTS
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=speech_text),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=["audio"],
                speech_config=self.get_voice_config(character),
            )

            # Generate the audio
            response = self.client.models.generate_content(
                model="gemini-2.5-pro-preview-tts",
                contents=contents,
                config=generate_content_config,
            )

            # Extract and save the audio data
            if (response.candidates and 
                response.candidates[0].content and 
                response.candidates[0].content.parts and
                response.candidates[0].content.parts[0].inline_data):
                
                inline_data = response.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                
                # Convert to WAV if needed
                file_extension = mimetypes.guess_extension(inline_data.mime_type)
                if file_extension is None or file_extension != ".wav":
                    data_buffer = self.convert_to_wav(data_buffer, inline_data.mime_type)
                    file_extension = ".wav"
                
                # Ensure the output filename has the right extension
                if not output_filename.endswith(".wav"):
                    output_filename = os.path.splitext(output_filename)[0] + ".wav"
                
                # Save the file
                with open(output_filename, "wb") as f:
                    f.write(data_buffer)
                
                print(f"Audio saved to: {output_filename}")
                return output_filename
            else:
                raise ValueError("No audio data found in response")
                
        except Exception as e:
            print(f"Error generating speech: {e}")
            # Fallback: create an empty file to avoid breaking the pipeline
            with open(output_filename, "wb") as f:
                f.write(b"")
            return output_filename