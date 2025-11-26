import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# Импортируем функции из utils
from utils import *

app = FastAPI()

# Глобальная переменная для стека
stack = list()

# Модели данных
class UserLogin(BaseModel):
    username: str
    password: str

class PushElement(BaseModel):
    value: int

class TokenData(BaseModel):
    username: str

# Зависимость для проверки аутентификации
async def get_current_user(token: Optional[str] = None):
    if token is None:
        raise HTTPException(status_code=401, detail="Токен не предоставлен")
    return verify_jwt_token(token)

# Эндпоинты для аутентификации с JWT
@app.post("/register")
async def register(user: UserLogin):
    """Регистрация нового пользователя"""
    if register_user(user.username, user.password):
        return {"message": f"Пользователь {user.username} зарегистрирован"}
    else:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

@app.post("/login")
async def login(user: UserLogin):
    """Безопасный вход с получением JWT токена"""
    if safe_login(user.username, user.password):
        token = create_jwt_token(user.username)
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": user.username
        }
    else:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

@app.post("/login/vulnerable")
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

@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Защищенный эндпоинт - требует JWT токен"""
    return {
        "username": current_user["username"],
        "message": "Это защищенный эндпоинт!",
        "access_granted": True
    }

@app.post("/verify-token")
async def verify_token(token: str):
    """Проверка валидности JWT токена"""
    user_data = verify_jwt_token(token)
    return {
        "valid": True,
        "username": user_data["username"],
        "message": "Токен валиден"
    }

# Эндпоинты стека с защитой JWT
@app.get('/pop')
async def pop_element(current_user: dict = Depends(get_current_user)):
    """Удалить элемент из стека (требует аутентификации)"""
    if not stack:
        raise HTTPException(status_code=404, detail="No elements in stack")
    
    return {
        "message": f"The last value is {stack.pop()}",
        "user": current_user["username"]
    }

@app.post('/push')
async def push_element(input: PushElement, current_user: dict = Depends(get_current_user)):
    """Добавить элемент в стек (требует аутентификации)"""
    stack.append(input.value)
    return {
        "message": f"{input.value} is added",
        "user": current_user["username"]
    }

@app.get('/size')
async def get_stack_size(current_user: dict = Depends(get_current_user)):
    """Получить размер стека (требует аутентификации)"""
    return {
        "stack_size": len(stack),
        "is_empty": len(stack) == 0,
        "user": current_user["username"]
    }

@app.delete('/clear')
async def clear_stack(current_user: dict = Depends(get_current_user)):
    """Очистить стек (требует аутентификации)"""
    stack.clear()
    return {
        "message": "Стек очищен",
        "user": current_user["username"]
    }

# Демонстрационные и учебные эндпоинты
@app.get("/demo/jwt-structure")
async def demo_jwt_structure():
    """Демонстрация структуры JWT токена"""
    example_token = create_jwt_token("demo_user", timedelta(minutes=5))
    
    try:
        import jwt
        from utils import JWT_SECRET, JWT_ALGORITHM
        decoded = jwt.decode(example_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        decoded = {"error": "cannot decode without verification"}
    
    return {
        "jwt_explanation": {
            "header": "Алгоритм шифрования и тип токена",
            "payload": "Данные пользователя + метаданные (exp, iat, sub)",
            "signature": "Цифровая подпись для проверки подлинности"
        },
        "example_token": example_token,
        "decoded_payload": decoded,
        "token_parts": example_token.split('.')
    }

@app.get("/demo/hash-irreversibility")
async def demo_hash_irreversibility():
    """Демонстрация необратимости хэшей"""
    results = demonstrate_hash_irreversibility()
    return {
        "message": "Демонстрация необратимости хэш-функций",
        "results": results,
        "conclusion": "Из хэша НЕВОЗМОЖНО восстановить исходный пароль!"
    }

@app.get("/demo/salt-protection")
async def demo_salt_protection():
    """Демонстрация защиты с помощью соли"""
    results = demonstrate_salt_protection()
    return {
        "message": "Демонстрация защиты от радужных таблиц с помощью соли",
        "users": results,
        "explanation": "Соль делает каждый хэш уникальным, даже для одинаковых паролей"
    }

@app.get("/demo/sql-injection")
async def demo_sql_injection():
    """Примеры SQL-инъекций для тестирования"""
    examples = {
        "Обход аутентификации": {
            "username": "admin' --",
            "password": "anything"
        },
        "Получение всех пользователей": {
            "username": "admin' OR '1'='1' --", 
            "password": "anything"
        },
        "Union-атака": {
            "username": "admin' UNION SELECT 1,2,3 --",
            "password": "anything"
        }
    }
    
    return {
        "message": "Примеры SQL-инъекций для тестирования уязвимого эндпоинта /login/vulnerable",
        "examples": examples,
        "warning": "НИКОГДА не используйте такие методы в реальных проектах!"
    }


@app.get("/demo/bcrypt-slowness")
async def demo_bcrypt_slowness():
    """Демонстрация медленной работы bcrypt как защиты"""
    results = demonstrate_bcrypt_slowness()
    return {
        "message": "Bcrypt специально медленный для защиты от перебора паролей",
        "results": results,
        "explanation": "Если хэширование занимает 0.1 сек, то подбор 10,000 паролей займет 1000 сек (16 минут!)"
    }

@app.get("/demo/bcrypt-salt-auto")
async def demo_bcrypt_salt_auto():
    """Демонстрация автоматической работы с солью в bcrypt"""
    results = demonstrate_bcrypt_salt_auto()
    return {
        "message": "Bcrypt автоматически генерирует и хранит соль",
        "demonstration": results,
        "advantage": "Не нужно вручную управлять солью - bcrypt делает всё автоматически"
    }


@app.get("/demo/compare-hashing")
async def demo_compare_hashing():
    """Сравнение разных алгоритмов хэширования"""
    results = compare_hashing_algorithms()
    return {
        "message": "Сравнение скорости хэш-функций",
        "results": results,
        "conclusion": "Для паролей нужны МЕДЛЕННЫЕ функции like bcrypt!"
    }


@app.get("/users")
async def get_users():
    """Получить список всех пользователей"""
    users = get_all_users()
    return {"users": [{"id": u[0], "username": u[1]} for u in users]}

@app.post("/init-db")
async def initialize_database():
    """Эндпоинт для инициализации базы данных"""
    init_db()
    return {"message": "База данных инициализирована"}

if __name__ == "__main__":
    print("🚀 Запуск демонстрации безопасности с JWT")
    print("📚 Доступные эндпоинты:")
    print("   POST /register        - Регистрация")
    print("   POST /login           - Вход с получением JWT") 
    print("   POST /login/vulnerable - Уязвимый вход (для демо)")
    print("   GET  /profile         - Защищенный профиль (требует JWT)")
    print("   GET  /demo/*          - Демонстрационные эндпоинты")
    print("\n🔐 Тестовые данные: username='admin', password='password123'")
    print("💡 Используйте Authorization: Bearer <token> для защищенных эндпоинтов")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
