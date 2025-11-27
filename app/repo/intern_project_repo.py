# app/repo/intern_project_repo.py

from app.models.intern_project import InternProject
from app.models.intern import Intern
from app.models.project import Project
from app.db.db import db
from sqlalchemy.orm import joinedload
from datetime import datetime


class InternProjectRepo:
    
    def assign(self, intern_id: int, project_id: int, role: str = "Member"):
        """Assign an intern to a project"""
        intern_project = InternProject(
            intern_id=intern_id,
            project_id=project_id,
            role_in_project=role,
            assigned_date=datetime.utcnow()
        )
        db.session.add(intern_project)
        db.session.commit()
        return intern_project
    
    def remove(self, intern_id: int, project_id: int) -> bool:
        """Remove an intern from a project"""
        intern_project = InternProject.query.filter_by(
            intern_id=intern_id,
            project_id=project_id
        ).first()
        
        if not intern_project:
            return False
        
        db.session.delete(intern_project)
        db.session.commit()
        return True
    
    def get_by_intern_and_project(self, intern_id: int, project_id: int):
        """Get a specific intern-project assignment"""
        return InternProject.query.filter_by(
            intern_id=intern_id,
            project_id=project_id
        ).first()
    
    def get_projects_by_intern(self, intern_id: int):
        """Get all projects for a specific intern"""
        assignments = InternProject.query.filter_by(
            intern_id=intern_id
        ).options(
            joinedload(InternProject.project)
        ).all()
        
        result = []
        for assignment in assignments:
            if assignment.project and not getattr(assignment.project, 'is_deleted', False):
                result.append({
                    'project_id': assignment.project_id,
                    'title': assignment.project.title,
                    'description': assignment.project.description,
                    'status': assignment.project.status,
                    'start_date': str(assignment.project.start_date) if assignment.project.start_date else None,
                    'end_date': str(assignment.project.end_date) if assignment.project.end_date else None,
                    'role_in_project': assignment.role_in_project,
                    'assigned_date': str(assignment.assigned_date) if assignment.assigned_date else None
                })
        
        return result
    
    def get_interns_by_project(self, project_id: int):
        """Get all interns assigned to a specific project"""
        assignments = InternProject.query.filter_by(
            project_id=project_id
        ).options(
            joinedload(InternProject.intern)
        ).all()
        
        result = []
        for assignment in assignments:
            if assignment.intern and not getattr(assignment.intern, 'is_deleted', False):
                result.append({
                    'id': assignment.intern_id,
                    'name': assignment.intern.name,
                    'email': assignment.intern.email,
                    'phone': getattr(assignment.intern, 'phone', None),
                    'university': getattr(assignment.intern, 'university', None),
                    'major': getattr(assignment.intern, 'major', None),
                    'role_in_project': assignment.role_in_project,
                    'assigned_date': str(assignment.assigned_date) if assignment.assigned_date else None
                })
        
        return result
    
    def get_all_assignments(self):
        return InternProject.query.options(
            joinedload(InternProject.intern),
            joinedload(InternProject.project)
        ).all()
    
    def update_role(self, intern_id: int, project_id: int, new_role: str) -> bool:
        assignment = self.get_by_intern_and_project(intern_id, project_id)
        
        if not assignment:
            return False
        
        assignment.role_in_project = new_role
        db.session.commit()
        return True
    
    def get_interns_count_by_project(self, project_id: int) -> int:
        return InternProject.query.filter_by(project_id=project_id).count()
    
    def get_projects_count_by_intern(self, intern_id: int) -> int:
        return InternProject.query.filter_by(intern_id=intern_id).count()