from abc import ABC, abstractmethod

class TrainingPlanRepoInterface(ABC):
    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, tp_id):
        pass

    @abstractmethod
    def create(self, data):
        pass
    @abstractmethod
    def update(sefl,tp_id, data):
        pass
    @abstractmethod
    def delete (self, tp_id, soft=True):
        pass
    @abstractmethod
    def get_for_intern(self, intern_id):
        pass

