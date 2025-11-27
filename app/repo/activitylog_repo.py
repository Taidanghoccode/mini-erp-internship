from app.models.activitylog import ActivityLog
from app.db.db import db
from app.repo.base_repo import BaseRepo
from datetime import datetime, timezone

class ActivityLogRepo(BaseRepo):

    def get_all(self):
        return ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()

    def get_by_id(self, log_id):
        return ActivityLog.query.get(log_id)

    def create(self, data):
        log = ActivityLog(**data)
        if "timestamp" not in data:
            log.timestamp = datetime.now(timezone.utc)
        db.session.add(log)
        db.session.commit()
        return log

    def update(self, log_id, data):
        log = self.get_by_id(log_id)
        if not log:
            return None
        for key, value in data.items():
            if hasattr(log, key):
                setattr(log, key, value)
        db.session.commit()
        return log

    def delete(self, log_id):
        log = self.get_by_id(log_id)
        if not log:
            return None
        db.session.delete(log)
        db.session.commit()
        return True

    #Lấy log của 1 user
    def get_by_user(self, user_id):
        return ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.timestamp.desc()).all()

    #Lấy log theo hành động cụ thể
    def get_by_action(self, action):
        return ActivityLog.query.filter_by(action=action).order_by(ActivityLog.timestamp.desc()).all()

    #Tạo nhanh log
    def quick_log(self, user_id, action, details):
        if not user_id or user_id == 0:
            user_id = None

        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        return log
    def get_logs_for_user(self, user_id):
        return ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.timestamp.desc())\
        .limit(20).all()