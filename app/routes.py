from flask import Blueprint, current_app, render_template, request, redirect, url_for
from app.utils import append_purchase, read_purchases
from datetime import datetime

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    # fresh start -> rating-based top products
    products = current_app.recommender.get_top_rated(n=12)
    return render_template("index.html", products=products)

@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = current_app.recommender.content_by_query(q, n=24) if q else []
    return render_template("search.html", query=q, results=results)

@bp.route("/recommend/<product_name>")
def recommend(product_name):
    prods = current_app.recommender.content_by_product_name(product_name, n=12)
    return render_template("recommendations.html", product_name=product_name, products=prods)

@bp.route("/buy", methods=["POST"])
def buy():
    """
    Form should post: user_id (optional), uniq_id, product_name, product_url
    """
    user_id = request.form.get("user_id", "").strip() or "anonymous"
    uniq_id = request.form.get("uniq_id", "")
    product_name = request.form.get("product_name", "")
    product_url = request.form.get("product_url", "")
    timestamp = datetime.utcnow().isoformat()

    append_purchase(
        current_app.config["PURCHASES_CSV"],
        {
            "user_id": user_id,
            "uniq_id": uniq_id,
            "product_name": product_name,
            "product_url": product_url,
            "timestamp": timestamp
        }
    )

    # After buying, show recommendations similar to this product
    return redirect(url_for("main.recommend", product_name=product_name))
