import sqlite3

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            role TEXT,
            tokens INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Добавление пользователя в базу данных
def add_user(tg_id, role='user', tokens=1):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (tg_id, role, tokens)
        VALUES (?, ?, ?)
    ''', (tg_id, role, tokens))
    conn.commit()
    conn.close()

# Проверка наличия пользователя в базе данных
def user_exists(tg_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Обновление количества жетонов у пользователя
def update_tokens(tg_id, tokens):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET tokens = ? WHERE tg_id = ?', (tokens, tg_id))
    conn.commit()
    conn.close()

# Получение информации о пользователе
def get_user(tg_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Добавление жетонов пользователю
def add_tokens(tg_id, tokens_to_add):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tokens FROM users WHERE tg_id = ?', (tg_id,))
    current_tokens = cursor.fetchone()[0]
    new_tokens = current_tokens + tokens_to_add
    cursor.execute('UPDATE users SET tokens = ? WHERE tg_id = ?', (new_tokens, tg_id))
    conn.commit()
    conn.close()
