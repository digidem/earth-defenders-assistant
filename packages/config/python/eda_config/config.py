from pathlib import Path
from typing import Optional
import yaml
from .types import Config

class ConfigLoader:
    _instance: Optional[Config] = None
    
    @classmethod
    def get_config(cls) -> Config:
        if cls._instance is None:
            def find_project_root(start_path: Path) -> Optional[Path]:
                """Find project root by looking for config.yaml"""
                current = start_path
                while current != current.parent:
                    if (current / "config.yaml").exists():
                        return current
                    current = current.parent
                return None

            # Start searching from the current file's directory
            start_path = Path(__file__).resolve().parent
            project_root = find_project_root(start_path)

            if not project_root:
                raise FileNotFoundError(
                    f"Could not find config.yaml from {start_path}.\n"
                    f"Ensure config.yaml is located in the project root."
                )

            config_path = project_root / "config.yaml"

            with open(config_path) as f:
                config_data = yaml.safe_load(f)
                
            cls._instance = Config(**config_data)
        return cls._instance