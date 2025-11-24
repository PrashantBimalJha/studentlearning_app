# Utils package for Learning App

import os
import yaml
from pathlib import Path

def load_env_from_yaml(yaml_file_path=None):
    """
    Load environment variables from a YAML file
    
    Args:
        yaml_file_path: Path to the YAML file. If None, looks for env.yaml in the project root.
    
    Returns:
        dict: Dictionary of environment variables
    """
    if yaml_file_path is None:
        # Get the project root directory (parent of utils directory)
        project_root = Path(__file__).parent.parent
        yaml_file_path = project_root / "env.yaml"
    
    try:
        with open(yaml_file_path, 'r') as file:
            env_vars = yaml.safe_load(file)
        
        # Set environment variables
        for key, value in env_vars.items():
            if value is not None:
                os.environ[key] = str(value)
        
        return env_vars
    except FileNotFoundError:
        print(f"Warning: Environment file {yaml_file_path} not found")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {yaml_file_path}: {e}")
        return {}
    except Exception as e:
        print(f"Error loading environment from {yaml_file_path}: {e}")
        return {}
