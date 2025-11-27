from app.db.db import db
from app.models.training_plan import TrainingPlan
from app.interfaces.tranining_plan_port import TrainingPlanRepoInterface

class TrainingPlanRepo(TrainingPlanRepoInterface):
    
    def get_all(self):
        return TrainingPlan.query.filter_by(is_deleted=False).all()
    
    def get_by_id(self, tp_id):
        tp = TrainingPlan.query.get(tp_id)
        return tp if tp and not tp.is_deleted else None
    
    def get_for_intern(self, intern_id):
        return TrainingPlan.query.filter_by(intern_id=intern_id, is_deleted=False).all()
    
    def create(self, data):
        tp = TrainingPlan(**data)
        db.session.add(tp)
        db.session.commit()
        return tp
    
    def update(self, tp_id, data):
        tp = self.get_by_id(tp_id)
        if not tp: 
            return None
        for k, v in data.items():
            if hasattr(tp, k):
                setattr(tp, k, v)
        db.session.commit()

        return tp
    
    def delete(self, tp_id, soft=True):
        tp = self.get_by_id(tp_id)
        if not tp:
            return None
        if soft:
            tp.is_deleted =True
        else:
            db.session.delete(tp)
        db.session.commit()
        return True