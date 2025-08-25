import subprocess
import os
from pyngrok import ngrok

def setup_comfyui(comfyui_dir: str = "/content/ComfyUI", install_script: str = None) -> None:
    """
    Set up ComfyUI in a Colab environment.
    
    Args:
        comfyui_dir (str): The directory to install ComfyUI.
        install_script (str): Path to a shell script that installs ComfyUI and dependencies.
    """
    if install_script and os.path.exists(install_script):
        subprocess.run(["bash", install_script], check=True)
    else:
        # Default installation steps
        subprocess.run(["git", "clone", "https://github.com/comfyanonymous/ComfyUI", comfyui_dir], check=True)
        os.chdir(comfyui_dir)
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

def start_comfyui(comfyui_dir: str = "/content/ComfyUI", port: int = 8188) -> subprocess.Popen:
    """
    Start the ComfyUI server.
    
    Args:
        comfyui_dir (str): The ComfyUI directory.
        port (int): The port to run ComfyUI on.
        
    Returns:
        subprocess.Popen: The process running ComfyUI.
    """
    os.chdir(comfyui_dir)
    process = subprocess.Popen(["python", "main.py", "--port", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def setup_ngrok(port: int = 8188) -> str:
    """
    Set up an ngrok tunnel to the ComfyUI server.
    
    Args:
        port (int): The port ngrok should tunnel to.
        
    Returns:
        str: The public URL of the ngrok tunnel.
    """
    # Set your ngrok auth token if required (you can set it in environment variables)
    # ngrok.set_auth_token("your_ngrok_token")
    tunnel = ngrok.connect(port, bind_tls=True)
    return tunnel.public_url