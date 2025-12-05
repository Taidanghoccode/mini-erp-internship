from app.db.db import db
from app.models.intern import Intern
from sqlalchemy.exc import SQLAlchemyError

class InternRepo:

    def get_all(self):
        return Intern.query.filter_by(is_deleted=False).all()

    def get_by_id(self, intern_id):
        return Intern.query.filter_by(id=intern_id, is_deleted=False).first()

    def get_by_email(self, email):
        return Intern.query.filter_by(email=email, is_deleted=False).first()

    def get_any_by_email(self, email):
        # check cả deleted
        return Intern.query.filter_by(email=email).first()

    def get_by_user_id(self, user_id):
        return Intern.query.filter_by(user_id=user_id, is_deleted=False).first()

    def create(self, data: dict):
        try:
            intern = Intern(**data)
            db.session.add(intern)
            db.session.commit()
            return intern
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def update(self, intern):
        """CHỈ commit object, không dùng intern.__dict__ để tránh lỗi."""
        try:
            db.session.commit()
            return intern
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self, intern_id, soft=True):
        intern = self.get_by_id(intern_id)
        if not intern:
            return False

        try:
            if soft:
                intern.is_deleted = True
            else:
                db.session.delete(intern)

            db.session.commit()
            return True

        except SQLAlchemyError:
            db.session.rollback()
            return False
