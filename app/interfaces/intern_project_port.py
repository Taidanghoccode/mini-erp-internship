from abc import ABC, abstractmethod

class InternProjectRepoInterface(ABC):

    @abstractmethod
    def get_link(self, intern_id, project_id):
        pass

    @abstractmethod
    def create_link(self, intern_id, project_id, role):
        pass

    @abstractmethod
    def remove_link(self, intern_id, project_id):
        pass

    @abstractmethod
    def get_projects_of_intern(self, intern_id):
        pass

    @abstractmethod
    def get_interns_of_project(self, project_id):
        pass

    @abstractmethod
    def get_all_links(self):
        pass
