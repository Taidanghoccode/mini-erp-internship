import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.intern import Intern
from app.models.project import Project
from app.models.feedback import Feedback
from app.models.intern_project import InternProject

app = create_app()

with app.app_context():
    print("Model test") 
    
    db.drop_all()
    db.create_all()
    print("DB create successfully")

    intern = Intern(
        name="Nguyen Huu Tai", 
        email="huutai0207.dev@gmail.com",
        major="SE"
    )

    db.session.add(intern)
    db.session.commit()

    print(f"Add intern:{intern.name}")

    project = Project(
        title="Mini ERP Intership",
        description="ERD webapp for managing intern"
    )
    db.session.add(project)
    db.session.commit()

    print(f"Add project:{project.title}")
    

    feedback = Feedback(
        intern_id=intern.id,
        project_id=project.id,
        rating=5, 
        comment="Good"
    )

    db.session.add(feedback)
    db.session.commit()
    print("Add feedback successfully")

    print("\n Data intern")
    print("Intern:", [i.name for i in Intern.query.all()])
    print("Project:", [p.title for p in project.query.all()])
    print("Feedbacks:", [f.comment for f in Feedback.query.all()])

    intern.major = "Computer Science"
    db.session.commit()
    print("Update intern major")

    db.session.delete(feedback)
    db.session.commit()
    print("Delete feedback")
    print("CRUD test successfully")
