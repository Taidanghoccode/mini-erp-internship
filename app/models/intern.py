from datetime import date
from app.db.db import db

class Intern(db.Model):
    __tablename__ = "interns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    university = db.Column(db.String(120))
    major = db.Column(db.String(100))
    start_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)

    intern_projects = db.relationship("InternProject", back_populates="intern")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    user = db.relationship("User", back_populates="intern_profile")

    feedbacks = db.relationship("Feedback", back_populates="to_intern")
    training_plans = db.relationship("TrainingPlan", back_populates="intern")

    def to_dict(self, with_counts=False):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "university": self.university,
            "major": self.major,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date) if self.end_date else None,
            "is_deleted": self.is_deleted,
            "user_id": self.user_id
        }

        if with_counts:
            data["project_count"] = len(self.intern_projects or [])
            valid = [f.score for f in self.feedbacks if not f.is_deleted]
            data["avg_rating"] = round(sum(valid) / len(valid), 1) if valid else None

        return data
