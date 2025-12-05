from app.repo.user_repo import UserRepo


class InternProjectUC:
    def __init__(self, intern_project_repo, intern_repo, project_repo, permission_repo, activitylog_uc):
        self.intern_project_repo = intern_project_repo
        self.intern_repo = intern_repo
        self.project_repo = project_repo
        self.permission_repo = permission_repo
        self.activitylog_uc = activitylog_uc

    def assign_project(self, user_id: int, intern_id: int, project_id: int, role: str = "Member"):        
        if not self.permission_repo.has_permission(user_id, "PROJECT_ASSIGN_INTERN"):
            raise PermissionError("You don't have permission to assign interns to projects")
        
        intern = self.intern_repo.get_by_id(intern_id)
        if not intern:
            raise ValueError(f"Intern with ID {intern_id} not found")
        
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        existing = self.intern_project_repo.get_by_intern_and_project(intern_id, project_id)
        if existing:
            raise ValueError(f"Intern is already assigned to this project")
        
        active_projects = []
        try:
            all_projects = self.intern_project_repo.get_projects_by_intern(intern_id)
            active_projects = [
                p for p in all_projects 
                if p.get('status', '').lower() == 'active' and p.get('project_id') != project_id
            ]
        except Exception as e:
            print(f"Warning: Could not check active projects: {e}")
        
        result = self.intern_project_repo.assign(intern_id, project_id, role)
        
        try:
            self.activitylog_uc.log_activity(
                user_id=user_id,
                action="ASSIGN_INTERN_PROJECT",
                details=f"Assigned intern {intern.name} (ID: {intern_id}) to project {project.title} (ID: {project_id}) as {role}"
            )
        except Exception as e:
            print(f"Warning: Could not log activity: {e}")
        
        response = {
            "success": True,
            "intern_id": intern_id,
            "project_id": project_id,
            "role": role,
            "message": f"Intern assigned successfully"
        }
        
        if active_projects:
            response["warning"] = f"This intern is already assigned to {len(active_projects)} active project(s)"
            response["active_projects"] = [
                p.get('title') or f"Project {p.get('project_id')}" 
                for p in active_projects
            ]
        
        return response

    def remove_project(self, user_id: int, intern_id: int, project_id: int) -> bool:        
        if not self.permission_repo.has_permission(user_id, "PROJECT_DELETE"):
            raise PermissionError("You don't have permission to remove interns from projects")
        
        intern = self.intern_repo.get_by_id(intern_id)
        project = self.project_repo.get_by_id(project_id)
        
        result = self.intern_project_repo.remove(intern_id, project_id)
        
        if result:
            try:
                intern_name = intern.name if intern else f"Intern {intern_id}"
                project_name = project.title if project else f"Project {project_id}"
                self.activitylog_uc.log_activity(
                    user_id=user_id,
                    action="REMOVE_INTERN_PROJECT",
                    details=f"Removed {intern_name} from {project_name}"
                )
            except Exception as e:
                print(f"Warning: Could not log activity: {e}")
        
        return result

    def get_projects_of_intern(self, user_id: int, intern_id: int):        
        if not self.permission_repo.has_permission(user_id, "INTERN_VIEW_PROJECTS"):
            raise PermissionError("You don't have permission to view intern projects")
        
        return self.intern_project_repo.get_projects_by_intern(intern_id)

    def get_interns_of_project(self, user_id: int, project_id: int):
        user = UserRepo().get_by_id(user_id)
        role = user.role.code if user and user.role else None

        if role in ["ADMIN", "MENTOR"]:
            return self.intern_project_repo.get_interns_by_project(project_id)

        if role == "INTERN":
            intern = user.intern_profile
            if not intern:
                raise PermissionError("Invalid intern profile")
            
            assigned = self.intern_project_repo.get_by_intern_and_project(intern.id, project_id)

            if not assigned:
                return []
            
            return self.intern_project_repo.get_interns_by_project(project_id)

        raise PermissionError("Role not supported")
