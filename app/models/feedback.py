# app/models/feedback.py
from app.db.db import db
from datetime import datetime, timezone
import enum

class FeedbackType(enum.Enum):
    TRAINER_INTERN = "TRAINER_INTERN"
    INTERN_PROJECT = "INTERN_PROJECT"
    TRAINER_PROJECT = "TRAINER_PROJECT"

class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.Enum(FeedbackType), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(100))  

    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    to_intern_id = db.Column(db.Integer, db.ForeignKey("interns.id"))
    to_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    is_deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    from_user = db.relationship("User", back_populates="feedbacks_given")
    to_intern = db.relationship("Intern", back_populates="feedbacks")
    to_project = db.relationship("Project", back_populates="feedbacks")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "score": self.score,
            "comment": self.comment,
            "from_user_id": self.from_user_id,
            "from_user_name": self.from_user.username if self.from_user else None,
            "to_intern_id": self.to_intern_id,
            "to_project_id": self.to_project_id,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat()
        }
