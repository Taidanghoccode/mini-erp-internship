from app.db.db import db

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, default=False)

    permissions = db.relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )
    
    users = db.relationship("User", back_populates="role")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "permissions": [p.code for p in self.permissions],
            "is_deleted": self.is_deleted
        }
