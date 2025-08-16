from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # instantiate recommender and attach to app
    from app.recommender import RecommendationEngine
    app.recommender = RecommendationEngine(
        csv_path=app.config["DATA_CSV"],
        image_cache_path=app.config["IMAGE_CACHE_JSON"],
        placeholder_image=app.config["PLACEHOLDER_IMAGE"],
        tfidf_min_df=app.config["TFIDF_MIN_DF"]
    )

    # register routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
