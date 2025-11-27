from app.models.feedback import Feedback
from app.db.db import db
from datetime import datetime

class FeedbackRepo:

    def create(self, data):
        fb = Feedback(**data)
        db.session.add(fb)
        db.session.commit()
        return fb

    def get_by_id(self, feedback_id):
        return Feedback.query.get(feedback_id)

    def get_for_intern(self, intern_id):
        return Feedback.query.filter_by(to_intern_id=intern_id, is_deleted=False).all()

    def get_for_project(self, project_id):
        return Feedback.query.filter_by(to_project_id=project_id).all()

    def get_by_user(self, user_id):
        return Feedback.query.filter_by(from_user_id=user_id).all()
    
    def get_by_user_and_intern(self, user_id, intern_id):
        return Feedback.query.filter_by(
            from_user_id=user_id,
            to_intern_id = intern_id, 
            is_deleted = False
        ).first()

    def update(self, feedback_id, data):
        fb = self.get_by_id(feedback_id)
        if not fb:
            return None
        for k, v in data.items():
            setattr(fb, k, v)
        db.session.commit()
        return fb
    def delete(self, feedback_id):
        fb = self.get_by_id(feedback_id)
        if not fb:
            return None
        db.session.delete(fb)
        db.session.commit()
        return True

    def filter_for_report(self, from_date=None, to_date=None, status=None):
        q = Feedback.query.filter_by(is_deleted=False)

        if from_date:
            f = datetime.strptime(from_date, "%Y-%m-%d")
            q = q.filter(Feedback.created_at >= f)

        if to_date:
            t = datetime.strptime(to_date, "%Y-%m-%d")
            q = q.filter(Feedback.created_at <= t)

        if status:
            q = q.filter(Feedback.type == status)

        return q.all()
    
    def get_all(self):
        return Feedback.query.filter_by(is_deleted=False).all()
