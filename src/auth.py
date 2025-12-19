import bcrypt
from src.database import DatabaseManager

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def hash_password(self, password):
        """Hashes a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password, password_hash):
        """Checks a password against a hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def login(self, username, password):
        """Authenticates a user."""
        user = self.db.get_user_by_username(username)
        if user and self.check_password(password, user['password_hash']):
            return user
        return None

    def register_user(self, username, password, role='agent'):
        """Registers a new user (admin only usually, but handled here)."""
        password_hash = self.hash_password(password)
        return self.db.add_user(username, password_hash, role)
