from sqlalchemy.exc import IntegrityError
from app.models.intern import Intern
from app.db.db import db
from app.interfaces.intern_port import InternRepoInterface
from datetime import datetime

class InternRepo(InternRepoInterface):

    def get_all(self):
        return Intern.query.filter_by(is_deleted=False).all()

    def get_by_id(self, intern_id):
        intern = Intern.query.get(intern_id)
        return intern if intern and not intern.is_deleted else None

    def create(self, data):
        intern = Intern(**data)
        db.session.add(intern)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Intern with email '{data.get('email')}' already exists")
        return intern

    def update(self, intern_id, data):
        intern = self.get_by_id(intern_id)
        if not intern:
            return None
        for key, value in data.items():
            if hasattr(intern, key):
                setattr(intern, key, value)
        db.session.commit()
        return intern

    def delete(self, intern_id, soft=True):
        intern = self.get_by_id(intern_id)
        if not intern:
            return None

        if soft:
            intern.is_deleted = True
        else:
            db.session.delete(intern)

        db.session.commit()
        return True

    def get_by_email(self, email):
        return Intern.query.filter_by(email=email, is_deleted=False).first()

    def get_any_by_email(self, email):
        return Intern.query.filter_by(email=email).first()

    def filter_for_report(self, from_date=None, to_date=None, status=None):
        q = Intern.query.filter_by(is_deleted=False)

        if from_date:
            f = datetime.strptime(from_date, "%Y-%m-%d").date()
            q = q.filter(Intern.start_date >= f)

        if to_date:
            t = datetime.strptime(to_date, "%Y-%m-%d").date()
            q = q.filter(Intern.start_date <= t)

        return q.all()
