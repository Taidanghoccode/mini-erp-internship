from app.db.db import db
from datetime import date

class InternProject(db.Model):
    __tablename__ = "intern_project"

    intern_id = db.Column(db.Integer, db.ForeignKey("interns.id"), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), primary_key=True)
    assigned_date = db.Column(db.Date, default=date.today)
    role_in_project = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Active")   
    progress = db.Column(db.Integer, default=0)          
    grade = db.Column(db.Float, nullable=True)

    intern = db.relationship("Intern", back_populates="intern_projects")
    project = db.relationship("Project", back_populates="project_interns")

    def to_dict(self):
        return {
            "intern_id": self.intern_id,
            "project_id": self.project_id,
            "assigned_date": str(self.assigned_date),
            "role_in_project": self.role_in_project,
            "status": self.status,
            "progress": self.progress,
            "grade": self.grade,
        }
