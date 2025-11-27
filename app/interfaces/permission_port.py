from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class PermissionRepoInterface(ABC):

    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def get_by_id(self, permission_id: int) -> Optional[Any]:
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def update(self, permission_id: int, data: Dict[str, Any]) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, permission_id: int, soft: bool = True) -> Optional[bool]:
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Any]:
        pass

