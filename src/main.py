import os
import sys

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_login import LoginManager

from src.models.user import User, init_users # Import User and init_users
from src.routes.main import main_bp # Import the main blueprint

# Ensure the outreach_engagements directory exists
ENGAGEMENT_DIR_PATH = "/home/ubuntu/client_portal_project/client_portal/src/engagements"
print(f"Runtime ENGAGEMENT_DIR_PATH: {ENGAGEMENT_DIR_PATH}")
if not os.path.exists(ENGAGEMENT_DIR_PATH):
    try:
        os.makedirs(ENGAGEMENT_DIR_PATH)
        print(f"Successfully created directory: {ENGAGEMENT_DIR_PATH}")
    except Exception as e:
        print(f"Error creating directory {ENGAGEMENT_DIR_PATH}: {e}")

# __name__ will be 'src.main' if run as 'python -m src.main' or similar,
# or '__main__' if 'src/main.py' is run directly.
# app.root_path will be the 'src' directory if main.py is in 'src'.
app = Flask(__name__, 
            template_folder="templates",  # Relative to app.root_path (src/)
            static_folder="static",      # Relative to app.root_path (src/)
            static_url_path="/static")   # Explicitly set URL path for static files

app.config["SECRET_KEY"] = "YOUR_VERY_SECRET_KEY_CHANGE_THIS" # Change this!

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "main.login"  # The route for the login page (blueprint_name.route_function_name)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Register Blueprints
app.register_blueprint(main_bp) # Register the main blueprint from src.routes.main

# Initialize dummy users (for testing)
with app.app_context():
    init_users()

if __name__ == "__main__":
    # This ensures that if the script is run directly (e.g. python src/main.py),
    # app.root_path is correctly set to the directory containing main.py (i.e., 'src').
    # The static and template folders will be resolved relative to this 'src' directory.
    app.run(host="0.0.0.0", port=5000, debug=True)

