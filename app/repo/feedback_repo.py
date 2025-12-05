from app.models.feedback import Feedback
from app.db.db import db
from datetime import datetime

from app.models.user import User


class FeedbackRepo:

    def create(self, data):
        fb = Feedback(**data)
        db.session.add(fb)
        db.session.commit()
        return fb
    
    def get_all(self):
        # CHUẨN — chỉ lấy feedback chưa xoá
        return Feedback.query.filter_by(is_deleted=False).all()

    def get_by_id(self, feedback_id):
        return Feedback.query.get(feedback_id)

    def get_for_intern(self, intern_id):
        return Feedback.query.filter_by(
            to_intern_id=intern_id,
            is_deleted=False
        ).all()

    def get_for_project(self, project_id):
        return Feedback.query.filter_by(
            to_project_id=project_id,
            is_deleted=False
        ).all()


    def get_by_user(self, user_id):
        return Feedback.query.filter_by(
            from_user_id=user_id
        ).all()

    def get_by_user_and_intern(self, user_id, intern_id):
        return Feedback.query.filter_by(
            from_user_id=user_id,
            to_intern_id=intern_id,
            is_deleted=False
        ).first()

    def get_by_user_and_project(self, user_id, project_id):
        return Feedback.query.filter_by(
            from_user_id=user_id,
            to_project_id=project_id,
            is_deleted=False
        ).first()

    def update(self, feedback_id, data):
        fb = self.get_by_id(feedback_id)
        if not fb:
            return None
        for k, v in data.items():
            setattr(fb, k, v)
        fb.updated_at = datetime.utcnow()
        db.session.commit()
        return fb

    def soft_delete(self, feedback_id):
        fb = self.get_by_id(feedback_id)
        if not fb:
            return None
        fb.is_deleted = True
        fb.updated_at = datetime.utcnow()
        db.session.commit()
        return True
