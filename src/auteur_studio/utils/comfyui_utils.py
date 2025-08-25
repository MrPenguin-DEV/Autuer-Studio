import requests
import json
import os
from typing import Dict, Any

def connect_to_comfyui(base_url: str) -> bool:
    """
    Check if ComfyUI server is running.
    
    Args:
        base_url (str): The base URL of the ComfyUI server.
        
    Returns:
        bool: True if connection is successful.
    """
    try:
        response = requests.get(base_url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def load_workflow(workflow_file: str) -> Dict[str, Any]:
    """
    Load a ComfyUI workflow from a JSON file.
    
    Args:
        workflow_file (str): Path to the JSON workflow file.
        
    Returns:
        Dict[str, Any]: The workflow as a dictionary.
    """
    with open(workflow_file, 'r') as file:
        workflow = json.load(file)
    return workflow

def queue_prompt(workflow: Dict[str, Any], comfyui_base_url: str) -> Dict[str, Any]:
    """
    Queue a prompt to ComfyUI.
    
    Args:
        workflow (Dict[str, Any]): The workflow definition.
        comfyui_base_url (str): The base URL of the ComfyUI server.
        
    Returns:
        Dict[str, Any]: The response from ComfyUI.
    """
    p = {"prompt": workflow}
    response = requests.post(f"{comfyui_base_url}/prompt", json=p)
    return response.json()

def get_image(filename: str, comfyui_base_url: str, output_dir: str) -> str:
    """
    Download an image from ComfyUI.
    
    Args:
        filename (str): The filename of the image on the ComfyUI server.
        comfyui_base_url (str): The base URL of the ComfyUI server.
        output_dir (str): The directory to save the image.
        
    Returns:
        str: The path to the downloaded image.
    """
    # ComfyUI serves images at /view?filename=filename.png
    response = requests.get(f"{comfyui_base_url}/view?filename={filename}")
    local_path = os.path.join(output_dir, filename)
    with open(local_path, 'wb') as f:
        f.write(response.content)
    return local_path