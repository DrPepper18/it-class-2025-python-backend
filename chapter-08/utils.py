import sqlite3
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
import bcrypt

# Секретный ключ для JWT (в реальном приложении хранить в env переменных)
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    try:
        # Хэшируем пароль с помощью bcrypt
        password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ('admin', password_hash)
        )
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

# JWT функции
def create_jwt_token(username: str, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token: str):
    """Проверка JWT токена"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return {"username": username}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")

# Функции для работы с пользователями (с bcrypt)
def safe_login(username: str, password: str):
    """Безопасный вход с проверкой пароля через bcrypt"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if not result:
        return False
    
    stored_hash = result[0]
    
    # bcrypt автоматически проверяет пароль и соль
    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    
    conn.close()
    return is_valid

def register_user(username: str, password: str):
    """Регистрация нового пользователя с bcrypt"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # bcrypt автоматически генерирует соль и хэширует пароль
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    
    conn.close()
    return success

def get_all_users():
    """Получить всех пользователей"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# Уязвимые функции для демонстрации SQL-инъекций
def vulnerable_login(username: str, password: str):
    """НЕБЕЗОПАСНО: уязвимый метод с SQL-инъекцией"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # ОПАСНО: прямое склеивание строк!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    print(f"Выполняется уязвимый запрос: {query}")
    
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Эмулируем "проверку пароля" - в реальности это было бы небезопасно
        return True
    return False


def demonstrate_hash_irreversibility():
    """Демонстрация необратимости хэшей"""
    passwords = [
        "password123",
        "password124",
        "hello world", 
        "Привет123!"
    ]
    
    results = []
    for pwd in passwords:
        hash_obj = hashlib.sha256(pwd.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        results.append({
            "password": pwd,
            "hash": hash_hex[:32] + "...",
            "input_length": len(pwd),
            "hash_length": len(hash_hex)
        })
    
    return results


# Функции для демонстрации хэширования с bcrypt
def demonstrate_bcrypt_slowness():
    """Демонстрация медленной работы bcrypt"""
    import time
    
    passwords = ["password123", "simple", "complex_P@ssw0rd!"]
    
    results = []
    for pwd in passwords:
        start_time = time.time()
        
        # Хэширование с bcrypt
        hash_start = time.time()
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        hash_time = time.time() - hash_start
        
        # Проверка пароля
        check_start = time.time()
        bcrypt.checkpw(pwd.encode('utf-8'), hashed)
        check_time = time.time() - check_start
        
        results.append({
            "password": pwd,
            "hash": hashed.decode('utf-8'),
            "hash_time_seconds": round(hash_time, 4),
            "check_time_seconds": round(check_time, 4),
            "protection": "Медленная работа защищает от перебора"
        })
    
    return results

def demonstrate_bcrypt_salt_auto():
    """Демонстрация автоматической работы с солью в bcrypt"""
    password = "my_password"
    
    # Генерируем несколько хэшей для одного пароля
    hashes = []
    for i in range(3):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashes.append({
            "attempt": i + 1,
            "hash": hashed.decode('utf-8'),
            "is_same": hashed == hashes[0]['hash'] if hashes else False
        })
    
    return {
        "original_password": password,
        "hashes": hashes,
        "explanation": "Bcrypt автоматически генерирует уникальную соль для каждого хэша"
    }

# Функция для сравнения разных алгоритмов хэширования
def compare_hashing_algorithms():
    """Сравнение скорости разных алгоритмов хэширования"""
    import time
    import hashlib
    
    password = "test_password_123"
    results = []
    
    # MD5 (очень быстрый, небезопасный)
    start = time.time()
    for _ in range(10000):
        hashlib.md5(password.encode()).hexdigest()
    md5_time = time.time() - start
    
    # SHA256 (быстрый, не для паролей)
    start = time.time()
    for _ in range(10000):
        hashlib.sha256(password.encode()).hexdigest()
    sha256_time = time.time() - start
    
    # Bcrypt (медленный, безопасный для паролей)
    start = time.time()
    for _ in range(10):  # Меньше итераций из-за медленной скорости
        bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    bcrypt_time = time.time() - start
    
    return {
        "md5": {
            "iterations": 10000,
            "total_time": round(md5_time, 4),
            "time_per_hash": round(md5_time / 10000, 6),
            "security": "НЕБЕЗОПАСНО для паролей"
        },
        "sha256": {
            "iterations": 10000,
            "total_time": round(sha256_time, 4),
            "time_per_hash": round(sha256_time / 10000, 6),
            "security": "НЕБЕЗОПАСНО для паролей"
        },
        "bcrypt": {
            "iterations": 10,
            "total_time": round(bcrypt_time, 4),
            "time_per_hash": round(bcrypt_time / 10, 4),
            "security": "БЕЗОПАСНО для паролей"
        }
    }

