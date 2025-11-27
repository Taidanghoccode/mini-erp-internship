from app import create_app, db
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from werkzeug.security import generate_password_hash
from sqlalchemy import text


def seed():

    print("Dropping schema with CASCADE...")
    db.session.execute(text("DROP SCHEMA public CASCADE;"))
    db.session.execute(text("CREATE SCHEMA public;"))
    db.session.commit()

    print("Recreating tables...")
    db.create_all()

    print("Seeding roles...")
    role_admin = Role(name="Admin", code="ADMIN", description="System administrator")
    role_mentor = Role(name="Mentor", code="MENTOR", description="Trainer / Mentor")
    role_intern = Role(name="Intern", code="INTERN", description="Intern user")

    db.session.add_all([role_admin, role_mentor, role_intern])
    db.session.commit()

    print("Seeding permissions...")

    perms_data = [
        ("VIEW_DASHBOARD", "View dashboard"),

        ("EXPORT_REPORT", "Export report"),
        ("VIEW_STATISTIC", "View statistics"),
        ("VIEW_REPORT", "View report"),

        ("INTERN_CREATE", "Create intern"),
        ("INTERN_VIEW", "View intern list"),
        ("INTERN_UPDATE", "Update intern"),
        ("INTERN_DELETE", "Delete intern"),
        ("INTERN_VIEW_PROJECTS", "View projects of an intern"),

        ("PROJECT_CREATE", "Create project"),
        ("PROJECT_VIEW", "View project"),
        ("PROJECT_UPDATE", "Update project"),
        ("PROJECT_DELETE", "Delete project"),
        ("PROJECT_ASSIGN_INTERN", "Assign intern to project"),
        ("PROJECT_VIEW_INTERNS", "View interns of a project"),

        ("FEEDBACK_CREATE_PROJECT", "Intern feedback to project"),
        ("FEEDBACK_VIEW", "View feedback"),
        ("FEEDBACK_UPDATE", "Update feedback"),
        ("FEEDBACK_DELETE", "Delete feedback"),

        ("EVALUATE_INTERN", "Mentor evaluate intern"),
        ("EVALUATE_PROJECT", "Mentor evaluate project"),

        ("TRAININGPLAN_CREATE", "Create training plan"),
        ("TRAININGPLAN_VIEW", "View training plan"),
        ("TRAININGPLAN_UPDATE", "Update training plan"),
        ("TRAININGPLAN_DELETE", "Delete training plan"),

        ("USER_MANAGE", "Manage users"),
        ("ROLE_MANAGE", "Manage roles"),
        ("ACTIVITYLOG_VIEW", "View activity log"),
    ]

    perms = [Permission(code=c, name=n) for c, n in perms_data]
    db.session.add_all(perms)
    db.session.commit()

    print("Assigning permissions to roles...")

    # Admin full quyền
    role_admin.permissions = perms

    mentor_codes = [
        "VIEW_DASHBOARD",
        "EXPORT_REPORT",
        "VIEW_STATISTIC",
        "VIEW_REPORT",
        "INTERN_VIEW",
        "INTERN_VIEW_PROJECTS",
        "PROJECT_CREATE",
        "PROJECT_VIEW",
        "PROJECT_UPDATE",
        "PROJECT_ASSIGN_INTERN",
        "PROJECT_VIEW_INTERNS",
        "FEEDBACK_VIEW",
        "FEEDBACK_UPDATE",
        "EVALUATE_INTERN",
        "EVALUATE_PROJECT",
        "TRAININGPLAN_CREATE",
        "TRAININGPLAN_VIEW",
        "TRAININGPLAN_UPDATE",
    ]

    role_mentor.permissions = [
        Permission.query.filter_by(code=c).first() for c in mentor_codes
    ]

    intern_codes = [
        "VIEW_DASHBOARD",
        "PROJECT_VIEW",
        "FEEDBACK_VIEW",
        "FEEDBACK_CREATE_PROJECT",
        "INTERN_VIEW_PROJECTS",
        "TRAININGPLAN_VIEW",
    ]

    role_intern.permissions = [
        Permission.query.filter_by(code=c).first() for c in intern_codes
    ]

    db.session.commit()

    print("Creating admin user...")

    admin = User(
        username="admin",
        email="admin@gmail.com",
        password_hash=generate_password_hash("admin123"),
        role_id=role_admin.id,
    )
    db.session.add(admin)
    db.session.commit()

    # Reset SERIAL
    db.session.execute(
        text("SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users));")
    )
    db.session.commit()

    print("Database seeded successfully.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
