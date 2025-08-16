import csv
import os
from typing import Dict, List

def append_purchase(purchases_csv_path: str, record: Dict):
    """
    Append a purchase record to CSV. Creates file with header if missing.
    record keys: user_id, uniq_id, product_name, product_url, timestamp
    """
    header = ["user_id", "uniq_id", "product_name", "product_url", "timestamp"]
    exists = os.path.exists(purchases_csv_path)

    os.makedirs(os.path.dirname(purchases_csv_path), exist_ok=True)

    with open(purchases_csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not exists:
            writer.writeheader()
        row = {k: record.get(k, "") for k in header}
        writer.writerow(row)

def read_purchases(purchases_csv_path: str) -> List[Dict]:
    if not os.path.exists(purchases_csv_path):
        return []
    import pandas as pd
    try:
        df = pd.read_csv(purchases_csv_path)
        return df.to_dict(orient="records")
    except Exception:
        return []
