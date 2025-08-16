import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    # CSVs
    DATA_CSV = os.path.join(BASE_DIR, "data", "flipkart.csv")  # match utils.py
    PURCHASES_CSV = os.path.join(BASE_DIR, "data", "purchases.csv")
    IMAGE_CACHE_JSON = os.path.join(BASE_DIR, "data", "image_cache.json")
    # placeholder image (used if extraction fails)
    PLACEHOLDER_IMAGE = "https://via.placeholder.com/400x400?text=No+Image"
    # TF-IDF min_df
    TFIDF_MIN_DF = 1
