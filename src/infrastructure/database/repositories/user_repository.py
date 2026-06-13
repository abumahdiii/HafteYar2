from typing import Optional
from sqlalchemy.orm import Session
from src.application.interfaces.repositories import IUserRepository
from src.domain.entities.user import UserEntity, UserAccountEntity
from src.infrastructure.database.models.user import User, UserAccount

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            username=model.username,
            email=model.email,
            phone=model.phone,
            created_at=model.created_at,
            accounts=[
                UserAccountEntity(
                    id=acc.id,
                    user_id=acc.user_id,
                    provider=acc.provider,
                    provider_id=acc.provider_id
                ) for acc in model.accounts
            ]
        )

    def _to_model(self, entity: UserEntity) -> User:
        return User(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            phone=entity.phone,
            created_at=entity.created_at
        )

    def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        user_model = self.db.query(User).filter(User.id == user_id).first()
        if user_model:
            return self._to_entity(user_model)
        return None

    def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        user_model = self.db.query(User).filter(User.phone == phone).first()
        if user_model:
            return self._to_entity(user_model)
        return None

    def create(self, user: UserEntity) -> UserEntity:
        user_model = self._to_model(user)
        self.db.add(user_model)
        
        for acc in user.accounts:
            acc_model = UserAccount(
                id=acc.id,
                user_id=acc.user_id,
                provider=acc.provider,
                provider_id=acc.provider_id
            )
            self.db.add(acc_model)
            
        self.db.commit()
        self.db.refresh(user_model)
        return self._to_entity(user_model)
