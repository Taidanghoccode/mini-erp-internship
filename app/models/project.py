from app.db.db import db
from datetime import date

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default="in_progress")

    project_interns = db.relationship("InternProject", back_populates="project")
    feedbacks = db.relationship("Feedback", back_populates="to_project")

    def to_dict(self, with_counts=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date) if self.end_date else None,
            "status": self.status,
            "is_deleted": self.is_deleted,
        }

        if with_counts:
            data["intern_count"] = len(self.project_interns or [])
            data["feedback_count"] = len(self.feedbacks or [])
            data["avg_rating"] = (
    round(sum(f.score for f in self.feedbacks) / len(self.feedbacks), 1)
) if self.feedbacks else None



        return data
