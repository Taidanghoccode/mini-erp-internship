from app.models.permission import Permission
from app.models.user import User
from app.models.role import Role
from app.db.db import db
from app.interfaces.permission_port import PermissionRepoInterface
from sqlalchemy.orm import joinedload
from app.utils.exception import PermissionDenied


class PermissionRepo(PermissionRepoInterface):

    def get_all(self):
        return Permission.query.options(
            joinedload(Permission.roles)
        ).filter_by(is_deleted=False).all()

    def get_by_id(self, permission_id: int):
        perm = Permission.query.options(
            joinedload(Permission.roles)
        ).get(permission_id)
        return perm if perm and not perm.is_deleted else None

    def create(self, data):
        perm = Permission(
            code=data["code"],
            name=data["name"],
            description=data.get("description", "")
        )
        db.session.add(perm)
        db.session.commit()
        return perm

    def update(self, permission_id: int, data):
        perm = self.get_by_id(permission_id)
        if not perm:
            return None
        for key, value in data.items():
            if hasattr(perm, key):
                setattr(perm, key, value)
        db.session.commit()
        return perm

    def delete(self, permission_id: int, soft=True):
        perm = Permission.query.get(permission_id)
        if not perm:
            return None
        if soft:
            perm.is_deleted = True
        else:
            db.session.delete(perm)
        db.session.commit()
        return True

    def get_by_code(self, code: str):
        return Permission.query.filter_by(
            code=code,
            is_deleted=False
        ).first()

    def search_by_name(self, keyword: str):
        return Permission.query.filter(
            Permission.name.ilike(f"%{keyword}%"),
            Permission.is_deleted == False
        ).all()

    def user_has(self, user_id: int, perm_code: str) -> bool:
        user = User.query.options(
            joinedload(User.role).joinedload(Role.permissions)
        ).filter_by(id=user_id, is_deleted=False).first()

        if not user or not user.role:
            return False

        return any(perm.code == perm_code for perm in user.role.permissions)
    
    def has_permission(self, user_id: int, permission_code: str) -> bool:
       
        return self.user_has(user_id, permission_code)
    
    def get_user_permissions(self, user_id: int):
        user = User.query.options(
            joinedload(User.role).joinedload(Role.permissions)
        ).filter_by(id=user_id, is_deleted=False).first()
        
        if not user or not user.role:
            return []
        
        return [p.code for p in user.role.permissions if not p.is_deleted]
    
    def get_permissions_by_role(self, role_id: int):
        role = Role.query.options(
            joinedload(Role.permissions)
        ).filter_by(id=role_id, is_deleted=False).first()
        
        if not role:
            return []
        
        return [p for p in role.permissions if not p.is_deleted]
    
    def ensure (self, user_id: int, perm_code:str):
        if not self.user_has(user_id, perm_code):
            raise PermissionDenied(f"Missing permission:{perm_code}")