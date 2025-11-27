from app.models.project import Project
from app.db.db import db
from app.repo.base_repo import BaseRepo
from app.interfaces.project_port import ProjectRepoInterface
from datetime import datetime

class ProjectRepo(BaseRepo, ProjectRepoInterface):

    def get_all(self):
        return Project.query.filter_by(is_deleted=False).all()

    def get_by_id(self, project_id):
        project = Project.query.get(project_id)
        return project if project and not project.is_deleted else None

    def get_by_title(self, title):
        return Project.query.filter_by(title=title, is_deleted=False).first()

    def create(self, data):
        project = Project(**data)
        db.session.add(project)
        db.session.commit()
        return project

    def update(self, project_id, data):
        project = self.get_by_id(project_id)
        if not project:
            return None

        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)

        db.session.commit()
        return project

    def delete(self, project_id, soft=True):
        project = self.get_by_id(project_id)
        if not project:
            return None

        if soft:
            project.is_deleted = True
        else:
            db.session.delete(project)

        db.session.commit()
        return True

    def get_overview(self):
        return Project.query.filter_by(is_deleted=False).all()

    def filter_for_report(self, from_date=None, to_date=None, status=None):
        q = Project.query.filter_by(is_deleted=False)

        if from_date:
            f = datetime.strptime(from_date, "%Y-%m-%d").date()
            q = q.filter(Project.start_date >= f)

        if to_date:
            t = datetime.strptime(to_date, "%Y-%m-%d").date()
            q = q.filter(Project.start_date <= t)

        if status:
            s = status.lower()
            if s == "active":
                q = q.filter(Project.status.in_(["new", "in_progress"]))
            elif s == "completed":
                q = q.filter(Project.status == "done")

        return q.all()

