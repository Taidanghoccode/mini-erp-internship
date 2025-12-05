import json
import random
from datetime import datetime, date, timezone
from app import create_app, db
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.models.intern import Intern
from app.models.project import Project
from app.models.training_plan import TrainingPlan
from app.models.feedback import Feedback, FeedbackType
from app.models.activitylog import ActivityLog
from app.models.intern_project import InternProject
from werkzeug.security import generate_password_hash
from sqlalchemy import text


def seed():
    # RESET DB
    db.session.execute(text("DROP SCHEMA public CASCADE;"))
    db.session.execute(text("CREATE SCHEMA public;"))
    db.session.commit()

    db.create_all()

    # ROLES
    admin_role = Role(name="Admin", code="ADMIN", description="System administrator")
    mentor_role = Role(name="Mentor", code="MENTOR", description="Trainer")
    intern_role = Role(name="Intern", code="INTERN", description="Intern user")

    db.session.add_all([admin_role, mentor_role, intern_role])
    db.session.commit()

    # CORRECT PERMISSIONS
    perm_codes = [
        ("USER_MANAGE", "Manage users"),
        ("TRAININGPLAN_DELETE", "Delete training plan"),
        ("INTERN_DELETE", "Delete intern"),
        ("EXPORT_REPORT", "Export report"),
        ("FEEDBACK_UPDATE", "Update feedback"),
        ("TRAININGPLAN_VIEW", "View training plan"),
        ("FEEDBACK_VIEW", "View feedback"),
        ("FEEDBACK_CREATE_PROJECT", "Intern feedback to project"),
        ("PROJECT_CREATE", "Create project"),
        ("PROJECT_VIEW", "View project"),
        ("ACTIVITYLOG_VIEW", "View activity log"),
        ("PROJECT_ASSIGN_INTERN", "Assign intern to project"),
        ("PROJECT_VIEW_INTERNS", "View interns of a project"),
        ("EVALUATE_INTERN", "Mentor evaluate intern"),
        ("INTERN_CREATE", "Create intern"),
        ("INTERN_UPDATE", "Update intern"),
        ("FEEDBACK_DELETE", "Delete feedback"),
        ("PROJECT_UPDATE", "Update project"),
        ("PROJECT_DELETE", "Delete project"),
        ("ROLE_MANAGE", "Manage roles"),
        ("VIEW_DASHBOARD", "View dashboard"),
        ("INTERN_VIEW", "View intern list"),
        ("VIEW_STATISTIC", "View statistics"),
        ("EVALUATE_PROJECT", "Mentor evaluate project"),
        ("TRAININGPLAN_CREATE", "Create training plan"),
        ("INTERN_VIEW_PROJECTS", "View intern projects"),
        ("VIEW_REPORT", "View report"),
        ("TRAININGPLAN_UPDATE", "Update training plan"),
        ("FEEDBACK_CREATE_INTERN", "Feedback to intern"),
    ]

    perms = [Permission(code=c, name=n) for c, n in perm_codes]
    db.session.add_all(perms)
    db.session.commit()

    # ROLE → PERMISSION ASSIGN
    admin_role.permissions = perms

    mentor_role.permissions = [
        Permission.query.filter_by(code=c).first()
        for c in [
            "VIEW_DASHBOARD", "INTERN_VIEW", "PROJECT_VIEW", "INTERN_VIEW_PROJECTS",
            "TRAININGPLAN_VIEW", "TRAININGPLAN_CREATE", "TRAININGPLAN_UPDATE",
            "FEEDBACK_VIEW", "EXPORT_REPORT", "VIEW_STATISTIC",
            "EVALUATE_INTERN", "EVALUATE_PROJECT", "REPORT_VIEW"
        ]
    ]

    intern_role.permissions = [
        Permission.query.filter_by(code=c).first()
        for c in [
            "VIEW_DASHBOARD", "PROJECT_VIEW", "FEEDBACK_VIEW",
            "FEEDBACK_CREATE_PROJECT", "INTERN_VIEW_PROJECTS", "TRAININGPLAN_VIEW"
        ]
    ]

    db.session.commit()

    # ADMIN ACCOUNT
    admin_user = User(
        username="admin",
        email="admin@gmail.com",
        password_hash=generate_password_hash("Aa@12345"),
        role_id=admin_role.id,
    )
    db.session.add(admin_user)
    db.session.commit()

    # RANDOM USERS
    users = []
    for i in range(10):
        role_choice = random.choice([mentor_role.id, intern_role.id])
        users.append(
            User(
                username=f"user{i}",
                email=f"user{i}@gmail.com",
                password_hash=generate_password_hash("Aa@12345"),
                role_id=role_choice,
            )
        )

    db.session.add_all(users)
    db.session.commit()

    # INTERNS
    majors = ["Software Engineering", "AI Engineering", "Business Analytics"]
    interns = []

    for u in users:
        if u.role_id == intern_role.id:
            interns.append(
                Intern(
                    user_id=u.id,
                    name=u.username.capitalize(),
                    email=u.email,
                    university="FPT University",
                    major=random.choice(majors),
                )
            )

    db.session.add_all(interns)
    db.session.commit()

    # PROJECTS
    project_templates = [
        ("ERP Internship System", "A mini ERP module for intern management"),
        ("AI Chatbot Assistant", "NLP chatbot answering questions"),
        ("Sales Analytics Dashboard", "Real-time business KPIs"),
        ("IoT Smart Controller", "IoT hub with MQTT"),
        ("Recruitment Ranking AI", "Machine learning scoring system"),
    ]

    projects = [
        Project(title=title, description=desc, status="progress")
        for title, desc in project_templates
    ]

    db.session.add_all(projects)
    db.session.commit()

    # ASSIGN
    for intern in interns:
        for project in random.sample(projects, 2):
            db.session.add(InternProject(intern_id=intern.id, project_id=project.id))

    db.session.commit()

    mentor_users = [u for u in users if u.role_id == mentor_role.id]

    feedback_sentences = [
        "Shows excellent weekly improvement.",
        "Great teamwork skill.",
        "Strong understanding of core concepts.",
        "Needs to practice more consistently.",
        "Very active and communicates well.",
    ]

    for intern in interns:
        db.session.add(
            Feedback(
                type=FeedbackType.TRAINER_INTERN,
                score=random.randint(3, 5),
                comment=random.choice(feedback_sentences),
                from_user_id=random.choice(mentor_users).id,
                to_intern_id=intern.id,
            )
        )

    db.session.commit()

    # ✅ TRAINING PLAN TEMPLATES - Sử dụng JSON
    tp_templates = [
        (
            "Web Fundamentals",
            "Learn HTML/CSS/JS basics",
            "Master core web foundations",
            "HTML, CSS, JavaScript",
            json.dumps({
                "docs": [
                    "https://www.freecodecamp.org/learn/responsive-web-design/",
                    "https://www.w3schools.com/html/",
                    "https://developer.mozilla.org/en-US/docs/Web/HTML"
                ],
                "videos": [
                    "https://www.youtube.com/watch?v=UB1O30fR-EE",
                    "https://www.youtube.com/watch?v=1PnVor36_40"
                ]
            }),
            json.dumps([
                {"date": "2025-01-06", "title": "HTML Basics", "note": "Learn HTML tags and structure"},
                {"date": "2025-01-13", "title": "CSS Styling", "note": "Master CSS layout and flexbox"},
                {"date": "2025-01-20", "title": "JavaScript Intro", "note": "Variables, functions, DOM manipulation"}
            ])
        ),
        (
            "Python Backend",
            "Build REST APIs using Flask",
            "Understand backend development",
            "Python, Flask, SQLAlchemy",
            json.dumps({
                "docs": [
                    "https://flask.palletsprojects.com/",
                    "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world",
                    "https://www.sqlalchemy.org/library.html"
                ],
                "videos": [
                    "https://www.youtube.com/watch?v=Z1RJmh_OqeA",
                    "https://www.udemy.com/course/rest-api-flask-and-python/"
                ]
            }),
            json.dumps([
                {"date": "2025-01-27", "title": "Flask Basics", "note": "Routes, templates, forms"},
                {"date": "2025-02-03", "title": "Database & ORM", "note": "SQLAlchemy models and migrations"},
                {"date": "2025-02-10", "title": "REST API & Auth", "note": "JWT authentication and API design"}
            ])
        ),
        (
            "Database Design",
            "SQL + ERD modeling",
            "Design normalized DB schema",
            "PostgreSQL, SQL, Database Design",
            json.dumps({
                "docs": [
                    "https://www.postgresql.org/docs/current/",
                    "https://vertabelo.com/blog/",
                    "https://www.sqlstyle.guide/"
                ],
                "videos": [
                    "https://www.youtube.com/watch?v=ztHopE5Wnpc",
                    "https://www.youtube.com/watch?v=SpbjXJHT6Fk"
                ]
            }),
            json.dumps([
                {"date": "2025-02-17", "title": "SQL Queries", "note": "SELECT, JOIN, subqueries"},
                {"date": "2025-02-24", "title": "ERD Design", "note": "Entity relationship diagrams"},
                {"date": "2025-03-03", "title": "Normalization & Optimization", "note": "Normal forms and indexing"}
            ])
        ),
    ]

    for intern in interns:
        for title, desc, obj, skills, res, tl in tp_templates:
            db.session.add(
                TrainingPlan(
                    title=f"{title} - {intern.name}",
                    description=desc,
                    objective=obj,
                    skills=skills,
                    resources=res,  # ✅ Đã là JSON string
                    timeline=tl,    # ✅ Đã là JSON string
                    created_by=random.choice(mentor_users).id,
                    intern_id=intern.id,
                )
            )

    db.session.commit()

    # ACTIVITY LOG
    for u in users:
        db.session.add(
            ActivityLog(user_id=u.id, action="LOGIN", details="User logged in")
        )

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()