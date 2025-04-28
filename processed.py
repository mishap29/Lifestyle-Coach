import json
from pathlib import Path
from typing import Dict, Any

# Define the base processed data directory
DATA_DIR = Path("data/processed")

# Make sure the processed folder exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_user_data(filename: str) -> Dict[str, Any]:
    """
    Load user data (sleep, exercise, goals) from a JSON file.
    If file does not exist, returns an empty dictionary.
    """
    path = DATA_DIR / filename
    if not path.exists():
        # Initialize empty JSON file if not present
        save_user_data(filename, {})
        return {}

    try:
        with open(path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_user_data(filename: str, data: Dict[str, Any]) -> None:
    """
    Save user data (sleep, exercise, goals) into a JSON file.
    """
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)  # Ensure folder still exists
    with open(path, "w") as file:
        json.dump(data, file, indent=2)