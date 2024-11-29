import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    # Basic Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'restaurant.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)  # Session lifetime for "remember me"
    
    # Login Security
    MAX_LOGIN_ATTEMPTS = 5  # Maximum failed login attempts before temporary block
    LOGIN_ATTEMPT_PERIOD = 15  # Time window for counting login attempts (minutes)
    BLOCK_DURATION = 15  # Duration of temporary block after max attempts (minutes)
    
    # Password Policy
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_COMPLEXITY = {
        'UPPER': 1,  # Minimum uppercase letters
        'LOWER': 1,  # Minimum lowercase letters
        'DIGITS': 1,  # Minimum digits
        'SPECIAL': 1,  # Minimum special characters
    }
    PASSWORD_HISTORY_SIZE = 5  # Number of previous passwords to remember
    PASSWORD_EXPIRY_DAYS = 90  # Days until password expires
