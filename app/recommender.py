import os
import json
import threading
import time
from typing import List, Dict, Optional

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from app.utils import load_dataset


# Helper: safe check for image-like URL
def _looks_like_image_url(s: Optional[str]) -> bool:
    if not isinstance(s, str):
        return False
    s = s.strip()
    if not s:
        return False
    s_low = s.lower()
    if s_low.startswith("http") and any(ext in s_low for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
        return True
    if "cdn" in s_low or "images" in s_low:
        return True
    return False


class RecommendationEngine:
    def __init__(self, image_cache_path: str, placeholder_image: str, tfidf_min_df: int = 1):
        self.image_cache_path = image_cache_path
        self.placeholder_image = placeholder_image
        self.tfidf_min_df = max(1, int(tfidf_min_df))

        self._cache_lock = threading.Lock()
        self.image_cache = {}
        self._load_image_cache()

        # ✅ use utils.load_dataset() instead of reading CSV directly
        self.df = load_dataset()
        self._normalize_data()
        self._prepare_text_index()

    # ---------- normalize after loading ----------
    def _normalize_data(self):
        # normalize columns
        self.df.columns = [c.strip() for c in self.df.columns]

        expected = [
            "uniq_id", "crawl_timestamp", "product_url", "product_name", "product_category_tree",
            "pid", "retail_price", "discounted_price", "image", "is_FK_Advantage_product",
            "description", "product_rating", "overall_rating", "brand", "product_specifications"
        ]
        for c in expected:
            if c not in self.df.columns:
                self.df[c] = ""

        def _tofloat(x):
            try:
                return float(x)
            except Exception:
                return np.nan

        self.df["overall_rating_num"] = self.df["overall_rating"].apply(_tofloat)
        self.df["product_rating_num"] = self.df["product_rating"].apply(_tofloat)
        self.df["rating_final"] = self.df["overall_rating_num"].fillna(self.df["product_rating_num"]).fillna(0.0)
        self.df["review_count"] = 0
        self.df["name_lc"] = self.df["product_name"].str.lower()
        self.df["resolved_image"] = self.df["image"].apply(lambda s: s.strip() if _looks_like_image_url(str(s).strip()) else "")

    # ---------- image cache ----------
    def _load_image_cache(self):
        self.image_cache = {}
        if os.path.exists(self.image_cache_path):
            try:
                with open(self.image_cache_path, "r", encoding="utf-8") as f:
                    self.image_cache = json.load(f)
            except Exception:
                self.image_cache = {}

    def _save_image_cache(self):
        try:
            with self._cache_lock:
                os.makedirs(os.path.dirname(self.image_cache_path), exist_ok=True)
                with open(self.image_cache_path, "w", encoding="utf-8") as f:
                    json.dump(self.image_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _scrape_image_from_page(self, page_url: str) -> Optional[str]:
        """Lightweight scrape for og:image, JSON-LD image or first useful <img>. Returns URL or None."""
        if not page_url or not page_url.startswith("http"):
            return None
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; RecommenderBot/1.0)"}
            resp = requests.get(page_url, headers=headers, timeout=6)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, "html.parser")

            meta_og = soup.find("meta", property="og:image")
            if meta_og and meta_og.get("content"):
                img = meta_og["content"].strip()
                if _looks_like_image_url(img):
                    return img

            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string or "{}")
                    if isinstance(data, dict):
                        img = data.get("image") or data.get("@graph", {}).get("image")
                        if isinstance(img, str) and _looks_like_image_url(img):
                            return img
                        if isinstance(img, list) and img:
                            cand = img[0]
                            if isinstance(cand, str) and _looks_like_image_url(cand):
                                return cand
                except Exception:
                    continue

            imgs = soup.find_all("img", src=True)
            for tag in imgs:
                src = tag["src"].strip()
                if src.startswith("//"):
                    src = "https:" + src
                if src.startswith("/") and page_url:
                    from urllib.parse import urljoin
                    src = urljoin(page_url, src)
                if _looks_like_image_url(src):
                    return src
        except Exception:
            return None
        return None

    def get_image_for_row(self, row: pd.Series) -> str:
        img = str(row.get("resolved_image", "") or "").strip()
        if _looks_like_image_url(img):
            return img

        page_url_candidates = [row.get("product_url", ""), row.get("image", "")]
        for pu in page_url_candidates:
            pu = str(pu or "").strip()
            if not pu:
                continue
            if pu in self.image_cache:
                cached = self.image_cache[pu]
                if _looks_like_image_url(cached):
                    return cached
            scraped = self._scrape_image_from_page(pu)
            if scraped:
                with self._cache_lock:
                    self.image_cache[pu] = scraped
                    threading.Thread(target=self._save_image_cache, daemon=True).start()
                return scraped

        return self.placeholder_image

    # ---------- text index ----------
    def _prepare_text_index(self):
        combined = (
            self.df["product_name"].fillna("") + " " +
            self.df["brand"].fillna("") + " " +
            self.df["product_category_tree"].fillna("") + " " +
            self.df["product_specifications"].fillna("") + " " +
            self.df["description"].fillna("")
        ).str.lower()
        self.df["combined_text"] = combined

        texts = combined
        if texts.str.strip().replace("", pd.NA).dropna().empty:
            texts = self.df["product_name"].fillna("")

        try:
            self.vectorizer = TfidfVectorizer(stop_words="english", min_df=self.tfidf_min_df, ngram_range=(1,2))
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        except Exception:
            self.vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df["product_name"].fillna(""))

    # ---------- public API ----------
    def get_top_rated(self, n: int = 12, min_reviews: int = 0) -> List[Dict]:
        df = self.df.copy()
        if min_reviews > 0:
            df = df[df["review_count"].astype(int) >= min_reviews]
        df = df.sort_values(by=["rating_final", "review_count"], ascending=[False, False]).head(n).copy()
        return self._rows_to_cards(df)

    def content_by_query(self, query: str, n: int = 12) -> List[Dict]:
        q = (query or "").strip().lower()
        if not q:
            return self.get_top_rated(n)

        mask_exact = self.df["name_lc"] == q
        if mask_exact.any():
            idx = int(self.df[mask_exact].index[0])
            return self.content_by_index(idx, n)

        mask_contains = self.df["name_lc"].str.contains(q, na=False)
        if mask_contains.any():
            idx = int(self.df[mask_contains].index[0])
            return self.content_by_index(idx, n)

        try:
            q_vec = self.vectorizer.transform([q])
            sims = linear_kernel(q_vec, self.tfidf_matrix).flatten()
            if sims.max() <= 0:
                return self.get_top_rated(n)
            top_idx = sims.argsort()[::-1][:n]
            return self._rows_to_cards(self.df.iloc[top_idx])
        except Exception:
            return self.get_top_rated(n)

    def content_by_product_name(self, product_name: str, n: int = 12) -> List[Dict]:
        q = (product_name or "").strip().lower()
        if not q:
            return self.get_top_rated(n)
        mask_exact = self.df["name_lc"] == q
        if mask_exact.any():
            idx = int(self.df[mask_exact].index[0])
            return self.content_by_index(idx, n)
        mask_contains = self.df["name_lc"].str.contains(q, na=False)
        if mask_contains.any():
            idx = int(self.df[mask_contains].index[0])
            return self.content_by_index(idx, n)
        return self.get_top_rated(n)

    def content_by_index(self, idx: int, n: int = 12) -> List[Dict]:
        try:
            row_vec = self.tfidf_matrix[idx:idx+1]
            sims = linear_kernel(row_vec, self.tfidf_matrix).flatten()
            sorted_idx = sims.argsort()[::-1]
            sorted_idx = [i for i in sorted_idx if i != idx]
            top_idx = sorted_idx[:n]
            return self._rows_to_cards(self.df.iloc[top_idx])
        except Exception:
            return self.get_top_rated(n)

    # ---------- helpers ----------
    def _rows_to_cards(self, df_rows: pd.DataFrame) -> List[Dict]:
        out = []
        for _, r in df_rows.iterrows():
            image_url = r.get("resolved_image") or ""
            if not _looks_like_image_url(image_url):
                image_url = self.get_image_for_row(r)
            price = r.get("discounted_price") or r.get("retail_price") or ""
            try:
                price = float(price)
            except Exception:
                price = None
            out.append({
                "uniq_id": r.get("uniq_id", ""),
                "product_name": r.get("product_name", ""),
                "brand": r.get("brand", ""),
                "description": r.get("description", ""),
                "category": r.get("product_category_tree", ""),
                "price": price,
                "rating": float(r.get("rating_final", 0) or 0),
                "product_url": r.get("product_url", ""),
                "image": image_url
            })
        return out
