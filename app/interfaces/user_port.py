from abc import ABC, abstractmethod

class UserRepoInterface(ABC):

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, user_id):
        pass

    @abstractmethod
    def get_by_email(self, email):
        pass

    @abstractmethod
    def get_by_username(self, username):
        pass

    @abstractmethod
    def create(self, data):
        pass

    @abstractmethod
    def update(self, user_id, data):
        pass

    @abstractmethod
    def delete(self, user_id, soft=True):
        pass
