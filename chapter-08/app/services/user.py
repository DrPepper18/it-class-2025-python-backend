from sqlalchemy import select
from database import async_session_maker
from models import User
import utils


# Регистрация нового пользователя
async def register_user(username: str, password: str):
    async with async_session_maker() as session:
        # Проверяем, существует ли пользователь
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return None  # Пользователь уже существует
        
        # Хэшируем пароль
        password_hash = await utils.create_password_hash(password)
        
        # Создаем нового пользователя
        new_user = User(username=username, password_hash=password_hash)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        return new_user


# Вход пользователя
async def login_user(username: str, password: str):
    async with async_session_maker() as session:
        # Ищем пользователя
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None  # Пользователь не найден
        
        # Проверяем пароль
        is_correct = await utils.is_password_correct(password, user.password_hash)
        
        if not is_correct:
            return None  # Неверный пароль
        
        return user


# Получение пользователя по username
async def get_user_by_username(username: str):
    async with async_session_maker() as session:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
