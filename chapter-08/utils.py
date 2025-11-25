import sqlite3

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    
    # Добавляем тестового пользователя
    try:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256(('password123' + salt).encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            ('admin', password_hash, salt)
        )
    except sqlite3.IntegrityError:
        pass  # Пользователь уже существует
    
    conn.commit()
    conn.close()

# Уязвимая функция для демонстрации SQL-инъекции
def vulnerable_login(username: str, password: str):
    """НЕБЕЗОПАСНО: уязвимый метод с SQL-инъекцией"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # ОПАСНО: прямое склеивание строк!
    query = f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{password}'"
    print(f"🚨 Выполняется уязвимый запрос: {query}")
    
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

# Безопасная функция с параметризованными запросами
def safe_login(username: str, password: str):
    """БЕЗОПАСНО: защищенный метод с параметризованными запросами"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # БЕЗОПАСНО: параметризованные запросы
    cursor.execute("SELECT salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if not result:
        return False
    
    salt = result[0]
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

# Функция для регистрации новых пользователей
def register_user(username: str, password: str):
    """Безопасная регистрация пользователя"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    
    conn.close()
    return success