from app import db
from datetime import datetime
import json

class AuditLog(db.Model):
    """Model for tracking user actions"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Allow null for failed logins
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    restaurant_name = db.Column(db.String(100), nullable=True)  # Allow null for failed logins
    target_type = db.Column(db.String(50))  # Type of entity being modified (e.g., 'menu_item', 'staff', etc.)
    target_id = db.Column(db.Integer)       # ID of the entity being modified
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    @staticmethod
    def log_action(user, action, details=None, ip_address=None, target_type=None, target_id=None):
        """Create a new audit log entry"""
        if isinstance(details, dict):
            # Ensure all values are JSON serializable
            details = json.loads(json.dumps(details))
        
        log = AuditLog(
            user_id=user.id if user else None,
            action=action,
            details=details,
            ip_address=ip_address,
            restaurant_name=user.restaurant_name if user else None,
            target_type=target_type,
            target_id=target_id
        )
        db.session.add(log)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error logging action: {e}")
            raise
            
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id} at {self.timestamp}>'
