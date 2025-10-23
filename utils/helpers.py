import bcrypt
import jwt
import os
from datetime import datetime

SECRET_KEY = os.getenv("SECRET_KEY", "your_jwt_secret_key_here")

# ==========================
# 🔐 Password Utilities
# ==========================
def hash_password(password: str) -> str:
    """Generate a bcrypt hash for a given password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Check a plain password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ==========================
# 🔑 Token Utilities
# ==========================
def decode_token(token: str):
    """Decode JWT token to extract payload."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ==========================
# 🕒 Misc Helpers
# ==========================
def format_timestamp():
    """Return current timestamp as a readable string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
