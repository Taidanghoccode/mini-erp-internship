import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Role, Permission, role_permissions
from app.repo.role_permission_repo import RolePermissionRepo


app = create_app()

with app.app_context():
    print("Start testing RolePermissionRepo")

    db.drop_all()
    db.create_all()
    print("Database reset done")

    role_admin = Role(name="Admin", description="Full access")
    role_mentor = Role(name="Mentor", description="Manage interns")

    perm_view = Permission(code="VIEW_DASHBOARD", name="View Dashboard", description="Can view dashboard")
    perm_edit = Permission(code="EDIT_DATA", name="Edit Data", description="Can edit records")
    perm_delete = Permission(code="DELETE_USER", name="Delete User", description="Can delete users")

    db.session.add_all([role_admin, role_mentor, perm_view, perm_edit, perm_delete])
    db.session.commit()
    print("Created roles and permissions")

    repo = RolePermissionRepo()

    repo.assign_permission(role_admin.id, perm_view.id)
    repo.assign_permission(role_admin.id, perm_edit.id)
    repo.assign_permission(role_admin.id, perm_delete.id)
    print("Assigned permissions to Admin")

    repo.assign_permission(role_mentor.id, perm_view.id)
    print(" Assigned permission to Mentor")

    admin_perms = repo.get_permissions_by_role(role_admin.id)
    mentor_perms = repo.get_permissions_by_role(role_mentor.id)
    print(" Admin permissions:", admin_perms)
    print(" Mentor permissions:", mentor_perms)

    view_roles = repo.get_roles_by_permission(perm_view.id)
    print("Roles that have 'View Dashboard':", view_roles)

    repo.remove_permission(role_admin.id, perm_delete.id)
    updated_perms = repo.get_permissions_by_role(role_admin.id)
    print("Admin permissions after remove:", updated_perms)

    all_links = repo.get_all()
    print("All Role-Permission links:", all_links)

    print("\nAll RolePermissionRepo tests passed successfully!")
