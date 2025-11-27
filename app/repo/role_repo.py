from app.models.role import Role
from app.models.permission import Permission
from app.db.db import db
from app.interfaces.role_port import RoleRepoInterface
from sqlalchemy.orm import joinedload


class RoleRepo(RoleRepoInterface):
    def get_all(self):
        return Role.query.options(joinedload(Role.permissions)).filter_by(is_deleted=False).all()
    
    def get_by_id(self, role_id):
        role = Role.query.options(joinedload(Role.permissions)).get(role_id)
        return role if role and not role.is_deleted else None
     
    def get_by_code(self, code):
        return Role.query.filter_by(code=code, is_deleted=False).first()

    def create(self, data):
        try:
            role = Role(name=data["name"],
                    code=data["code"],
                    description = data.get("description", ""))
            db.session.add(role)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            print("❌ Create role error:", e)
            raise

    def update(self, role_id: int, data):
        try:
            role = self.get_by_id(role_id)
            if not role:
                return None
            for key, value in data.items():
                if hasattr(role, key):
                    setattr(role, key, value)

            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            print("❌ Update role error:", e)
            raise

    def delete(self, role_id, soft = True):
        try:
            role = Role.query.get(role_id)
            if not role: return None

            if soft:
                role.is_deleted = True
            else:
                db.session.delete(role)

            db.session.commit()
            return True
        
        except Exception as e:
            db.session.rollback()
            print("❌ Delete error:",e)
            raise
        
    def assign_permission(self, role_id, permission_id):
        try:
            role = self.get_by_id(role_id)
            if not role:
                raise ValueError("Role not found")
            permission = Permission.query.get(permission_id)
            if not permission:
                raise ValueError("Permission not found")
            if permission in role.permissions:
                return role
            role.permissions.append(permission)
            db.session.commit()
            return role 
        except Exception as e:
            db.session.rollback()
            print("Assign Permission Error:", e)
            raise

    def remove_permission(self, role_id, permission_id):
        try:
            role = self.get_by_id(role_id)
            if not role:
                raise ValueError("Role not found")
            permission = Permission.query.get(permission_id)
            if not permission:
                raise ValueError("Permission not found")
            if permission not in role.permissions:
                return role
            role.permissions.remove(permission)
            db.session.commit()
            return role
        except Exception as e:
            db.session.rollback()
            print("Remove permission error:", e)

            raise