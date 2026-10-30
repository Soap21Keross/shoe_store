import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def vulnerable_login(conn, login):
    """УЯЗВИМЫЙ запрос (через f-строку)"""
    cursor = conn.cursor()
    # ОПАСНО! Данные пользователя склеиваются с SQL-запросом
    query = f"SELECT * FROM users WHERE login = '{login}'"
    print(f"Выполняется запрос: {query}")
    cursor.execute(query)
    return cursor.fetchall()

def secure_login(conn, login):
    """БЕЗОПАСНЫЙ запрос (параметризованный)"""
    cursor = conn.cursor()
    # БЕЗОПАСНО! Данные передаются отдельно от SQL-запроса
    query = "SELECT * FROM users WHERE login = ?"
    print(f"Выполняется запрос: {query} с параметром ('{login}',)")
    cursor.execute(query, (login,))
    return cursor.fetchall()

def main():
    conn = get_connection()

    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ SQL-ИНЪЕКЦИИ")
    print("=" * 60)

    # 1. Обычный логин (безопасный)
    print("\n1. Уязвимая функция с логином 'admin':")
    result = vulnerable_login(conn, "admin")
    print(f"Найдено записей: {len(result)}")

    # 2. Вредоносный код (SQL-инъекция)
    print("\n2. Уязвимая функция с вредоносным кодом:")
    malicious_input = "' OR '1'='1"
    result = vulnerable_login(conn, malicious_input)
    print(f"Найдено записей: {len(result)} (должно быть много!)")
    for row in result[:3]:
        print(f"  Найден пользователь: {row[1]}")

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАЩИТЫ (ПАРАМЕТРИЗАЦИЯ)")
    print("=" * 60)

    # 3. Безопасная функция с вредоносным кодом
    print("\n3. Безопасная функция с вредоносным кодом:")
    result = secure_login(conn, malicious_input)
    print(f"Найдено записей: {len(result)} (должно быть 0!)")

    conn.close()

if __name__ == "__main__":
    main()