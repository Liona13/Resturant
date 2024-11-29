from app import db

class Role(db.Model):
    """User role model for role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON)  # Store permissions as JSON
    users = db.relationship('User', back_populates='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

    def has_permission(self, permission):
        """Check if role has a specific permission"""
        if not self.permissions:
            return False
        
        # Admin role has all permissions
        if 'all' in self.permissions.get('permissions', []):
            return True
            
        return permission in self.permissions.get('permissions', [])
