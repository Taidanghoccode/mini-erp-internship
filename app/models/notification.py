from datetime import datetime
from app.db.db import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=True)
    link_url = db.Column(db.String(255), nullable=True)
    meta = db.Column(db.JSON, nullable=True)

    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "link_url": self.link_url,
            "meta": self.meta,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
