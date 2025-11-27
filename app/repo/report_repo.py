from app.models.intern import Intern
from app.models.project import Project
from app.models.feedback import Feedback
from app.db.db import db
from datetime import datetime


class ReportRepo:

    def get_interns(self, filters):
        """
        Lấy danh sách sinh viên thực tập với bộ lọc
        Filters: major, date_from, date_to
        """
        query = Intern.query.filter_by(is_deleted=False)

        # Lọc theo ngành
        if filters.get("major"):
            query = query.filter(Intern.major == filters["major"])

        # Lọc theo ngày bắt đầu
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
        """
        Lấy danh sách dự án với bộ lọc
        Filters: status, date_from, date_to
        """
        query = Project.query.filter_by(is_deleted=False)

        # Lọc theo trạng thái
        if filters.get("status"):
            query = query.filter(Project.status == filters["status"])

        # Lọc theo ngày tạo hoặc ngày bắt đầu (tùy model của bạn)
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
        """
        Lấy danh sách feedback với bộ lọc
        Filters: intern_id, project_id, date_from, date_to
        """
        query = Feedback.query.filter_by(is_deleted=False)

        # Lọc theo intern_id
        if filters.get("intern_id"):
            query = query.filter(Feedback.to_intern_id == filters["intern_id"])

        # Lọc theo project_id
        if filters.get("project_id"):
            query = query.filter(Feedback.to_project_id == filters["project_id"])

        # Lọc theo ngày tạo feedback
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