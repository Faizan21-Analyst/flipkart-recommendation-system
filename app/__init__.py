import os
from flask import Flask
from app.recommender import RecommendationEngine
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Recommendation Engine correctly (no csv_path needed)
    app.recommender = RecommendationEngine(
        image_cache_path=Config.IMAGE_CACHE_JSON,
        placeholder_image=Config.PLACEHOLDER_IMAGE,
        tfidf_min_df=Config.TFIDF_MIN_DF
    )

    # Register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
