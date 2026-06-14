from typing import Optional, List
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
            password_hash=model.password_hash,
            is_admin=model.is_admin,
            subscription_type=getattr(model, 'subscription_type', 'NONE'),
            subscription_duration_days=getattr(model, 'subscription_duration_days', None),
            subscription_end_date=getattr(model, 'subscription_end_date', None),
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
            password_hash=entity.password_hash,
            is_admin=entity.is_admin,
            subscription_type=entity.subscription_type,
            subscription_duration_days=entity.subscription_duration_days,
            subscription_end_date=entity.subscription_end_date,
            created_at=entity.created_at
        )

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        user_model = self.db.query(User).filter(User.username == username).first()
        if user_model:
            return self._to_entity(user_model)
        return None

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

    def get_all(self, skip: int = 0, limit: int = 50) -> List[UserEntity]:
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [self._to_entity(u) for u in users]

    def count(self) -> int:
        return self.db.query(User).count()
