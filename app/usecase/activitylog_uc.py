from app.repo.activitylog_repo import ActivityLogRepo


class ActivityLogUC:

    def __init__(self, activitylog_repo=None):
        self.activitylog_repo = activitylog_repo or ActivityLogRepo()

    def log_action(self, user_id, action, details):
        log = self.activitylog_repo.quick_log(user_id, action, details)
        return log.to_dict()

    def get_logs_by_user(self, user_id):
        logs = self.activitylog_repo.get_by_user(user_id)
        return [l.to_dict() for l in logs]

    def get_all_logs(self):
        logs = self.activitylog_repo.get_all()
        return [l.to_dict() for l in logs]


    def get_logs_by_action(self, action):
        logs = self.activitylog_repo.get_by_action(action)
        return [l.to_dict() for l in logs]
