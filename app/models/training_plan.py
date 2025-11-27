from app.db.db import db
from datetime import datetime, timezone

class TrainingPlan(db.Model):
    __tablename__ = "training_plans"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000))
    objective = db.Column(db.String(500))
    skills = db.Column(db.String(500))
    resources = db.Column(db.Text)
    timeline = db.Column(db.Text)
    progress = db.Column(db.Integer, default=0)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    intern_id = db.Column(db.Integer, db.ForeignKey("interns.id"), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default = lambda:datetime.now(timezone.utc), onupdate=lambda:datetime.now(timezone.utc))

    is_deleted = db.Column(db.Boolean, default=False)
    intern = db.relationship("Intern", back_populates="training_plans")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "objective": self.objective,
            "skills": self.skills,
            "resources": self.resources,
            "timeline": self.timeline,
            "progress": self.progress,
            "intern_id": self.intern_id,
            "is_deleted": self.is_deleted,
            "created_by": self.created_by,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }