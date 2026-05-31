import os
import json

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, 'data')

def read_json(filename: str):
    """Read data from a local JSON database file"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        if filename in ('stats.json', 'poll.json'):
            return {}
        return []

def write_json(filename: str, data):
    """Write data to a local JSON database file"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing {filename}: {e}")
        return False
