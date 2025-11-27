import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Role, Permission, role_permissions, ActivityLog

app = create_app()

with app.app_context():
    print("Starting User-Role-Permission")

    db.drop_all()
    db.create_all()
    print("Database Create successfully")

    admin_role = Role(name="Admin", description="Full access to system")
    mentor_role = Role(name="Mentor", description="Manage interns and feedback")
    db.session.add_all([admin_role, mentor_role])
    db.session.commit()
    print("Add Roles")

    perm_create = Permission(code="CREATE_USER", name="Create User", description="Can create users")
    perm_delete = Permission(code="DELETE_USER", name="Delete User", description="Can delete users")
    perm_view   = Permission(code="VIEW_DASHBOARD", name="View Dashboard", description="Can view dashboard")

    db.session.add_all([perm_create, perm_delete, perm_view])
    db.session.commit()
    print("Add Permissions")

    admin_role.permissions.append(perm_create)
    admin_role.permissions.append(perm_delete)
    admin_role.permissions.append(perm_view)

    mentor_role.permissions.append(perm_view)
    db.session.commit()
    print("Linked Roel <-> Permissions")

    admin_user = User(username="tai_admin", email="admin@demo.com", password="123456", role_id=admin_role.id)
    mentor_user = User(username="mentor_lam", email="lam@demo.com", password="123456", role_id=mentor_role.id)
    db.session.add_all([admin_user, mentor_user])
    db.session.commit()
    print("Added Users")

    log1 = ActivityLog(user_id=admin_user.id, action="CREATE", details="Created new intern record")
    log2 = ActivityLog(user_id=mentor_user.id, action="UPDATE", details="Update feedback score")
    db.session.add_all([log1, log2])
    db.session.commit()
    print("Logged Activities")

    print("\n Role", [r.name for r in Role.query.all()])
    print("Permissions:", [p.name for p in Permission.query.all()])
    print("Users:", [u.username for u in User.query.all()])
    print("Logs:", [l.details for l in ActivityLog.query.all()])

    print("\n All User-Role-Permission test passed successfuly")