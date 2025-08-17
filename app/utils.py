# app/utils.py
import os
import pandas as pd
import gdown

DATA_PATH = os.path.join("data", "your_products.csv")

FILE_ID = "1_itNCEJGGXwVKYW33MWS9lQHU_HPvTq1"
DATA_URL = f"https://drive.google.com/uc?id={FILE_ID}"


def ensure_dataset():
    """Download dataset from Google Drive if not already available."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        print("Downloading dataset from Google Drive...")
        gdown.download(DATA_URL, DATA_PATH, quiet=False)
    return DATA_PATH


def load_dataset():
    """Load and clean dataset as DataFrame."""
    path = ensure_dataset()
    
    # Skip bad rows that break parsing
    df = pd.read_csv(path, on_bad_lines="skip", low_memory=False)

    if "product_name" not in df.columns:
        raise ValueError(
            f"'product_name' column not found! Available columns: {list(df.columns)}"
        )

    df["product_name"] = (
        df["product_name"]
        .fillna("")      # remove NaN
        .astype(str)     # force string
        .str.strip()     # trim spaces
    )

    # Drop rows with empty product names
    df = df[df["product_name"] != ""].reset_index(drop=True)

    if df.empty:
        raise ValueError("Dataset has no valid product names after cleaning!")

    return df
