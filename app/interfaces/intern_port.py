from abc import ABC, abstractmethod

class InternRepoInterface(ABC):

    @abstractmethod
    def get_all(self): pass

    @abstractmethod
    def get_by_id(self, intern_id): pass

    @abstractmethod
    def create(self, data): pass

    @abstractmethod
    def update(self, intern_id, data): pass

    @abstractmethod
    def delete(self, intern_id, soft=True): pass

    @abstractmethod
    def get_by_email(self, email): pass
