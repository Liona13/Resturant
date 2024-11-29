from datetime import datetime, timedelta
from app import db

class LoginAttempt(db.Model):
    """Track login attempts for security"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 can be up to 45 chars
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    successful = db.Column(db.Boolean, nullable=False, default=False)
    user_agent = db.Column(db.String(255))
    restaurant_name = db.Column(db.String(100), nullable=False)

    @classmethod
    def cleanup_old_attempts(cls, older_than_hours=24):
        """Remove login attempts older than specified hours"""
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        cls.query.filter(cls.timestamp < cutoff).delete()
        db.session.commit()

    @classmethod
    def get_recent_attempts(cls, email, ip_address, minutes=15):
        """Get number of recent failed attempts for email and IP"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        
        # Get attempts by email
        email_attempts = cls.query.filter(
            cls.email == email,
            cls.successful == False,
            cls.timestamp > cutoff
        ).count()

        # Get attempts by IP
        ip_attempts = cls.query.filter(
            cls.ip_address == ip_address,
            cls.successful == False,
            cls.timestamp > cutoff
        ).count()

        return email_attempts, ip_attempts

    @classmethod
    def is_blocked(cls, email, ip_address):
        """Check if login should be blocked based on recent attempts"""
        email_attempts, ip_attempts = cls.get_recent_attempts(email, ip_address)
        
        # Block if more than 5 failed attempts by email or IP in the last 15 minutes
        return email_attempts >= 5 or ip_attempts >= 10

    @classmethod
    def get_block_duration(cls, email, ip_address):
        """Get remaining block duration in minutes"""
        email_attempts, ip_attempts = cls.get_recent_attempts(email, ip_address)
        
        if not cls.is_blocked(email, ip_address):
            return 0
        
        # Find the most recent failed attempt
        latest_attempt = cls.query.filter(
            ((cls.email == email) | (cls.ip_address == ip_address)),
            cls.successful == False
        ).order_by(cls.timestamp.desc()).first()
        
        if latest_attempt:
            block_end = latest_attempt.timestamp + timedelta(minutes=15)
            remaining = block_end - datetime.utcnow()
            return max(0, int(remaining.total_seconds() / 60))
        
        return 0

    def __repr__(self):
        return f'<LoginAttempt {self.email} from {self.ip_address} at {self.timestamp}>'
