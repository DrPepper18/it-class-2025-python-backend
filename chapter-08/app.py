import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from utils import *

app = FastAPI()



class UserLogin(BaseModel):
    username: str
    password: str

class PushElement(BaseModel):
    value: int

stack = list()

# Эндпоинты для демонстрации SQL-инъекций
@app.post('/login/vulnerable')
async def login_vulnerable(user: UserLogin):
    """
    УЯЗВИМЫЙ метод входа - демонстрация SQL-инъекции
    Попробуйте ввести:
    - username: admin' --
    - password: anything
    """
    if vulnerable_login(user.username, user.password):
        return {"message": "Успешный вход (уязвимый метод)"}
    else:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

@app.post('/login/safe')
async def login_safe(user: UserLogin):
    """
    БЕЗОПАСНЫЙ метод входа - параметризованные запросы
    """
    if safe_login(user.username, user.password):
        return {"message": "Успешный вход (безопасный метод)"}
    else:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

@app.post('/register')
async def register(user: UserLogin):
    """Регистрация нового пользователя"""
    if register_user(user.username, user.password):
        return {"message": f"Пользователь {user.username} зарегистрирован"}
    else:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

@app.get('/users')
async def get_users():
    """Получить список всех пользователей (для демонстрации)"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return {"users": [{"id": u[0], "username": u[1]} for u in users]}

# Оригинальные эндпоинты стека
@app.get('/pop')
async def pop_element():
    if not stack:
        raise HTTPException(status_code=404, detail="No elements in stack")
    
    return {"message": f"The last value is {stack.pop()}"}

@app.post('/push')
async def push_element(input: PushElement):
    stack.append(input.value)
    return {"message": f"{input.value} is added"}

@app.get('/size')
async def get_stack_size():
    return {
        "stack_size": len(stack),
        "is_empty": len(stack) == 0
    }

@app.delete('/clear')
def clear_stack():
    stack.clear()
    return {"message": "Стек очищен"}

# Демонстрационный эндпоинт для показа SQL-инъекций
@app.get('/demo/injection')
async def demo_injection():
    """
    Демонстрация различных типов SQL-инъекций
    """
    examples = {
        "Обход аутентификации": {
            "username": "admin' --",
            "password": "anything"
        },
        "Получение всех пользователей": {
            "username": "admin' OR '1'='1' --",
            "password": "anything"
        },
        "Удаление таблицы": {
            "username": "admin'; DROP TABLE users; --",
            "password": "anything"
        },
        "Union-атака": {
            "username": "admin' UNION SELECT 1,2,3 --",
            "password": "anything"
        }
    }
    
    return {
        "message": "Примеры SQL-инъекций для тестирования",
        "examples": examples,
        "warning": "НИКОГДА не используйте такие методы в реальных проектах!"
    }

if __name__ == "__main__":
    print("🚀 Запуск демонстрации SQL-инъекций")
    print("📚 Доступные эндпоинты:")
    print("   POST /login/vulnerable - Уязвимый вход (для демонстрации инъекций)")
    print("   POST /login/safe       - Безопасный вход")
    print("   POST /register         - Регистрация нового пользователя")
    print("   GET  /demo/injection   - Примеры SQL-инъекций")
    print("   GET  /users            - Список пользователей")
    print("\n🔐 Тестовые данные: username='admin', password='password123'")
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)