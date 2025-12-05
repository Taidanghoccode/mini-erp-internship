from app.models.user import User
from app.db.db import db
from app.repo.base_repo import BaseRepo
from app.interfaces.user_port import UserRepoInterface
from sqlalchemy.orm import joinedload
from app.models.role import Role


class UserRepo(BaseRepo, UserRepoInterface):
    
    def get_all(self):
        return User.query.options(joinedload(User.role)).filter_by(is_deleted=False).all()

    def get_by_id(self, user_id):
        return (
            User.query.options(
                joinedload(User.role).joinedload(Role.permissions)
            )
            .filter_by(id=user_id, is_deleted=False)
            .first()
        )


    def get_by_email(self, email):
        return User.query.filter_by(email=email, is_deleted=False).first()

    def get_by_username(self, username):
        return User.query.filter_by(username=username, is_deleted=False).first()

    def create(self, data):
        try:
            print(f"Creating user: {data.get('username')}")
            user = User(
                username=data["username"],
                email=data["email"],
                is_active=True,
            )
            user.set_password(data["password"])
            db.session.add(user)
            db.session.commit()

            role_id = data.get("role_id")
            if role_id:
                print(f"Assigning role {role_id} to user {user.id}")
                return self.assign_role(user.id, role_id)

            return self.get_by_id(user.id)

            
        except Exception as e:
            print(f"CREATE USER ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise

    def update(self, user_id, data):
        try:
            user = self.get_by_id(user_id)
            if not user:
                print(f"User {user_id} not found")
                return None

            print(f"Updating user {user.username}")
            
            for key, value in data.items():
                if key == "password":
                    user.set_password(value)
                    print(f" Password updated for {user.username}")
                elif hasattr(user, key):
                    setattr(user, key, value)
                    print(f"{key} updated for {user.username}")

            db.session.commit()
            print(f"User {user.username} changes committed")
            
            db.session.refresh(user)
            
            return user
            
        except Exception as e:
            print(f" UPDATE USER ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise

    def delete(self, user_id, soft=True):
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"User {user_id} not found for deletion")
                return None

            if soft:
                print(f"Soft deleting user {user.username}")
                user.is_deleted = True
            else:
                print(f"Hard deleting user {user.username}")
                db.session.delete(user)

            db.session.commit()
            print(f" User {user_id} deleted successfully")
            return True
            
        except Exception as e:
            print(f"DELETE USER ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise

    def assign_role(self, user_id, role_id):
        user = User.query.get(user_id)
        if not user:
            return None

        user.role_id = role_id
        db.session.commit()

        return self.get_by_id(user_id)
