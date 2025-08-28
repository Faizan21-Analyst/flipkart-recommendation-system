# flipkart-recommendation-system

🛒 Product Recommendation System (Flask + ML)
📌 Project Overview

This project is a Product Recommendation Web Application built with Flask.
It provides personalized product recommendations for users, based on a dataset of Flipkart products.
The system combines content-based filtering, collaborative filtering, and hybrid recommendation methods to enhance the shopping experience.

We deployed the application on Render for free hosting.

📂 Dataset

Source: Flipkart Product Dataset (Kaggle)

Features used:

uniq_id → Unique product identifier

product_name → Product title

brand → Brand of product

price → Price in INR

rating → User ratings

product_url → Link to product page

image → Image URL for display

⚙️ Methods & Logic
1. Top-Rated Products

Homepage shows most popular products ranked by rating.

Acts as a fallback for new users without purchase history.

2. Purchase Logging

Every time a user clicks Buy, purchase data (user_id, uniq_id, product_name, product_url, timestamp) is logged in purchases.csv.

This dataset helps track user preferences.

3. Recommendation Engine

We implemented three strategies inside recommender.py:

Content-Based Filtering

Uses product features (name, brand, category, etc.)

Recommends items similar to the one viewed or purchased.

Collaborative Filtering (User-Based)

Uses purchase history of multiple users.

Suggests products that “similar users” bought.

Hybrid Recommendation

Combines both methods with a tunable weight parameter alpha.

Balances similarity with popularity.

4. Flask Web Application

index.html: Displays top products / recommendations.

buy route: Saves purchases.

recommend route: Returns personalized recommendations.

Templates styled with Bootstrap 5.

🚀 Deployment

Platform: Render

Procfile used for Gunicorn server.

Virtual Environment Requirements:

Flask

pandas

scikit-learn

gunicorn

numpy

📊 Project Flow

User visits homepage → sees Top Rated Products.

User enters a user_id and clicks Buy → purchase is stored.

System generates recommendations for that user (based on purchase + dataset).

User sees personalized recommendations on next visit.

📸 Screenshots

🏠 Homepage with top-rated products

🔍 Product details with "Buy" button

⭐ Recommended products page

🧑‍💻 Author

Faizan Shaikh

Aspiring Data Analyst | Data Science Enthusiast

Skills: Python, Flask, SQL, Power BI, Machine Learning
