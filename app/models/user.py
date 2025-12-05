from app.db.db import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)
    role = db.relationship("Role", back_populates="users", lazy="joined")

    intern_profile = db.relationship("Intern", back_populates="user", uselist=False)

    feedbacks_given = db.relationship("Feedback", back_populates="from_user")

    logs = db.relationship("ActivityLog", back_populates="user")

    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def permission_codes(self):
        if not self.role or not self.role.permissions:
            return []
        return [p.code for p in self.role.permissions]

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role_id": self.role_id,
            "role_name": self.role.name if self.role else None,
            "role_code": self.role.code if self.role else None,
            "intern_id": self.intern_profile.id if self.intern_profile else None,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "failed_attempts": self.failed_attempts,
            "locked_until": self.locked_until.strftime("%Y-%m-%d %H:%M:%S") if self.locked_until else None,
        }

    def __repr__(self):
        return f"<User {self.username}>"
