from app.models.intern import Intern
from app.models.project import Project
from app.models.feedback import Feedback
from app.db.db import db
from datetime import datetime


class ReportRepo:

    def get_interns(self, filters):
        query = Intern.query.filter_by(is_deleted=False)

        if filters.get("major"):
            query = query.filter(Intern.major == filters["major"])

        date_from = filters.get("date_from")
        if date_from and isinstance(date_from, str) and date_from.strip():
            try:
                df = datetime.fromisoformat(date_from)
                query = query.filter(Intern.start_date >= df)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error parsing date_from: {date_from}, error: {e}")

        date_to = filters.get("date_to")
        if date_to and isinstance(date_to, str) and date_to.strip():
            try:
                dt = datetime.fromisoformat(date_to)
                query = query.filter(Intern.start_date <= dt)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error parsing date_to: {date_to}, error: {e}")

        return query.all()

    def get_projects(self, filters):
        query = Project.query.filter_by(is_deleted=False)

        if filters.get("status"):
            query = query.filter(Project.status == filters["status"])

        if filters.get("date_from") and hasattr(Project, 'created_at'):
            try:
                df = datetime.fromisoformat(filters["date_from"])
                query = query.filter(Project.created_at >= df)
            except (ValueError, TypeError):
                pass

        if filters.get("date_to") and hasattr(Project, 'created_at'):
            try:
                dt = datetime.fromisoformat(filters["date_to"])
                query = query.filter(Project.created_at <= dt)
            except (ValueError, TypeError):
                pass

        return query.all()

    def get_feedback(self, filters):
        query = Feedback.query.filter_by(is_deleted=False)
        if filters.get("intern_id"):
            query = query.filter(Feedback.to_intern_id == filters["intern_id"])
        if filters.get("project_id"):
            query = query.filter(Feedback.to_project_id == filters["project_id"])

        if filters.get("date_from") and hasattr(Feedback, 'created_at'):
            try:
                df = datetime.fromisoformat(filters["date_from"])
                query = query.filter(Feedback.created_at >= df)
            except (ValueError, TypeError):
                pass

        if filters.get("date_to") and hasattr(Feedback, 'created_at'):
            try:
                dt = datetime.fromisoformat(filters["date_to"])
                query = query.filter(Feedback.created_at <= dt)
            except (ValueError, TypeError):
                pass

        return query.all()
    
    def get_distinct_majors(self):
        q = db.session.query(Intern.major).distinct().all()
        return [m[0] for m in q if m[0]]
