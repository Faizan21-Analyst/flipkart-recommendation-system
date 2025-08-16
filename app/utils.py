import os
import pandas as pd
import requests

DATA_PATH = os.path.join("data", "your_products.csv")

# Google Drive direct download link (replace with your file ID)
DATA_URL = "https://drive.google.com/uc?export=download&id=1_itNCEJGGXwVKYW33MWS9lQHU_HPvTq1"

def ensure_dataset():
    """Download dataset if not already available."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        print("Downloading dataset from Google Drive...")
        r = requests.get(DATA_URL, stream=True)
        with open(DATA_PATH, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return DATA_PATH

def load_dataset():
    """Load dataset as DataFrame."""
    ensure_dataset()
    return pd.read_csv(DATA_PATH)
