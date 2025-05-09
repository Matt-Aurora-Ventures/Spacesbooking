from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory user store for simplicity in this phase.
# In a production environment, this would be a database.
users_db = {}

class User(UserMixin):
    def __init__(self, id, username, password_hash, project_name, 
                 project_summary="", project_website="", project_x_social="", 
                 focus_topics="", is_admin=False): # Added is_admin flag
        self.id = id
        self.username = username # This will be the project name for login or admin username
        self.password_hash = password_hash
        self.project_name = project_name # To link to their specific todo file or data (None for admin)
        self.project_summary = project_summary
        self.project_website = project_website
        self.project_x_social = project_x_social
        self.focus_topics = focus_topics
        self.is_admin = is_admin # Store admin status

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        return users_db.get(user_id)

    @staticmethod
    def get_by_username(username):
        for user_id, user in users_db.items():
            if user.username == username:
                return user
        return None

    def update_info(self, summary, website, x_social):
        self.project_summary = summary
        self.project_website = website
        self.project_x_social = x_social

    def update_focus_topics(self, topics):
        self.focus_topics = topics

# Example: Create users for testing
def init_users():
    if not users_db: # Ensure this runs only once
        # Admin User
        admin_user = User(id="admin", 
                          username="aurora_admin", 
                          password_hash="", 
                          project_name=None, # No specific project for admin
                          is_admin=True)
        admin_user.set_password("supersecretadminpass") # Change this in a real scenario
        users_db["admin"] = admin_user

        # Client Users
        user1 = User(id="client1", 
                     username="ProjectAlpha", 
                     password_hash="", 
                     project_name="ProjectAlpha",
                     project_summary="Project Alpha is a revolutionary new platform for decentralized applications.",
                     project_website="https://projectalpha.example.com",
                     project_x_social="https://x.com/projectalpha")
        user1.set_password("passalpha")
        users_db["client1"] = user1

        user2 = User(id="client2", 
                     username="CaddyFinance", 
                     password_hash="", 
                     project_name="CaddyFinance",
                     project_summary="CaddyFinance offers innovative DeFi solutions for yield farming.",
                     project_website="https://caddyfinance.example.com",
                     project_x_social="https://x.com/caddyfinance")
        user2.set_password("passcaddy")
        users_db["client2"] = user2

        user3 = User(id="client3",
                     username="EncryptSim",
                     password_hash="",
                     project_name="EncryptSim",
                     project_summary="EncryptSIM, the world's first Web3-focused eSIM provider, offers encrypted eSIMs with no KYC, ensuring total privacy and security for users across 120+ countries.",
                     project_website="", # To be filled by client or research
                     project_x_social="") # To be filled by client or research
        user3.set_password("passencrypt") # Choose a secure password
        users_db["client3"] = user3
        
        print("Initialized admin and dummy client users with extended info for testing.")


