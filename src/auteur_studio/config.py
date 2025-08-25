import yaml
import os
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path (str): Path to the config file. If None, tries to load from default location.
        
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    if config_path is None:
        # Try to find the config file in various locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'default_config.yaml'),
            os.path.join(os.path.dirname(__file__), '..', 'configs', 'default_config.yaml'),
            'configs/default_config.yaml',
            '/content/auteur-studio/configs/default_config.yaml'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
        else:
            raise FileNotFoundError("Could not find default config file")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Override with environment variables if set
    if 'GEMINI_API_KEY' in os.environ:
        config['gemini']['api_key'] = os.environ['GEMINI_API_KEY']
    
    return config