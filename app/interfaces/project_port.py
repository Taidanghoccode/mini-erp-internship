from abc import ABC, abstractmethod

class ProjectRepoInterface(ABC):

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, project_id):
        pass

    @abstractmethod
    def get_by_title(self, title):
        pass

    @abstractmethod
    def create(self, data):
        pass

    @abstractmethod
    def update(self, project_id, data):
        pass

    @abstractmethod
    def delete(self, project_id):
        pass
