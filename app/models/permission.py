from app.db.db import db

class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, default=False) 

    roles = db.relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "is_deleted": self.is_deleted
        }
