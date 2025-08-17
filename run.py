import os
from app import create_app

# Create the Flask app via factory
app = create_app()

if __name__ == "__main__":
    # Render provides PORT dynamically
    port = int(os.environ.get("PORT", 5000))  # fallback for local
    app.run(host="0.0.0.0", port=port, debug=True)
