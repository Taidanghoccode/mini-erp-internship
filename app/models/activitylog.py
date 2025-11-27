from app.db.db import db
from datetime import datetime, timezone

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True, nullable=True)
    action = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "details": self.details,
            "timestamp": str(self.timestamp)
        }
