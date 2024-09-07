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
            tokens INTEGER,
            language TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Добавление пользователя в базу данных
def add_user(tg_id, role='user', tokens=1):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    if tg_id == 6451994483 or tg_id == 742854337:
        role = 'admin'

    cursor.execute('''
        INSERT INTO users (tg_id, role, tokens, language)
        VALUES (?, ?, ?, ?)
    ''', (tg_id, role, tokens, '🇷🇺Русский'))
    conn.commit()
    conn.close()

# Проверка наличия пользователя в базе данных
def user_exists(id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE tg_id = ?', (id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Проверка наличия пользователя в базе данных
def user_exists_2(id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
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
def add_tokens(id, tokens_to_add):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tokens FROM users WHERE id = ?', (id,))
    current_tokens = cursor.fetchone()[0]
    new_tokens = current_tokens + tokens_to_add
    cursor.execute('UPDATE users SET tokens = ? WHERE id = ?', (new_tokens, id))
    conn.commit()
    conn.close()


def get_admins():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tg_id FROM users WHERE role = "admin"')
    admins = cursor.fetchall()
    conn.close()
    return admins


# Обновление языка у пользователя
def up_lang(language, tg_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE tg_id = ?', (language, tg_id))
    conn.commit()
    conn.close()


'''Получить данные по id'''
def get_user_id(id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    conn.close()
    return user