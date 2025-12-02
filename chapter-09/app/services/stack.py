from sqlalchemy import select, delete, func
from app.database import async_session_maker
from app.models import Stack


# PUSH - добавление элемента в стек
async def push(user_id: int, value: int):
    async with async_session_maker() as session:
        new_item = Stack(user_id=user_id, value=value)
        session.add(new_item)
        await session.commit()
        return new_item.id


# POP - извлечение верхнего элемента из стека
async def pop(user_id: int):
    async with async_session_maker() as session:
        stmt = (
            select(Stack)
            .where(Stack.user_id == user_id)
            .order_by(Stack.id.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        top_item = result.scalar_one_or_none()
        
        if top_item:
            value = top_item.value
            await session.delete(top_item)
            await session.commit()
            return value
        return None


# DELETE - удаление всех элементов из стека
async def delete_all(user_id: int):
    async with async_session_maker() as session:
        stmt = delete(Stack).where(Stack.user_id == user_id)
        await session.execute(stmt)
        await session.commit()
        return True


# GET_SIZE - получение размера стека
async def get_size(user_id: int):
    async with async_session_maker() as session:
        stmt = select(func.count(Stack.id)).where(Stack.user_id == user_id)
        result = await session.execute(stmt)
        size = result.scalar()
        return size

