from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class FeedbackRepoInterface(ABC):

    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def get_by_id(self, feedback_id: int) -> Optional[Any]:
        pass

    @abstractmethod
    def get_by_intern(self, intern_id: int) -> List[Any]:
        pass

    @abstractmethod
    def get_by_project(self, project_id: int) -> List[Any]:
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def update(self, feedback_id: int, data: Dict[str, Any]) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, feedback_id: int, soft: bool = True) -> Optional[bool]:
        pass
