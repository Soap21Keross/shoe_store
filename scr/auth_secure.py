import sqlite3
import os
import hashlib

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    """Хэширует пароль через SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(conn, login, password):
    """Регистрирует нового пользователя с хэшем пароля"""
    cursor = conn.cursor()
    password_hash = hash_password(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (login, password_hash) VALUES (?, ?)",
            (login, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def check_password(conn, login, password):
    """Проверяет пароль по хэшу"""
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE login = ?", (login,))
    row = cursor.fetchone()
    
    if not row:
        return False
    
    stored_hash = row[0]
    input_hash = hash_password(password)
    return stored_hash == input_hash

def main():
    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("ХЭШИРОВАНИЕ ПАРОЛЕЙ")
    print("=" * 60)

    # Добавляем поле password_hash (если его нет)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        conn.commit()
        print("Поле password_hash добавлено в таблицу users.")
    except sqlite3.OperationalError:
        print("Поле password_hash уже существует.")

    # Регистрируем пользователя
    print("\nРегистрация пользователя 'test_user' с паролем 'admin123'...")
    if register_user(conn, "test_user", "admin123"):
        print("Пользователь успешно зарегистрирован.")
    else:
        print("Пользователь уже существует.")

    # Проверка правильного пароля
    print("\nПроверка правильного пароля 'admin123':")
    result = check_password(conn, "test_user", "admin123")
    print(f"Результат: {result} (должно быть True)")

    # Проверка неправильного пароля
    print("\nПроверка неправильного пароля 'wrongpass':")
    result = check_password(conn, "test_user", "wrongpass")
    print(f"Результат: {result} (должно быть False)")

    conn.close()

if __name__ == "__main__":
    main()