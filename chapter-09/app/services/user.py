from sqlalchemy import select
from app.database import async_session_maker
from app.models import User
import app.utils as utils


# Регистрация нового пользователя
async def register_user(username: str, password: str):
    async with async_session_maker() as session:
        # Проверяем, существует ли пользователь
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return None

        # синхронная функция — без await
        password_hash = utils.create_password_hash(password)

        new_user = User(username=username, password_hash=password_hash)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user


# Вход пользователя
async def login_user(username: str, password: str):
    async with async_session_maker() as session:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        # синхронная функция — без await
        is_correct = utils.is_password_correct(password, user.password_hash)

        if not is_correct:
            return None

        return user


# Получение пользователя по username
async def get_user_by_username(username: str):
    async with async_session_maker() as session:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
