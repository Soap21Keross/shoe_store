import sqlite3
import os

# Словарь прав (какая роль что может)
PERMISSIONS = {
    "admin_db": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP"],
    "developer": ["SELECT", "INSERT", "UPDATE"],
    "reader": ["SELECT"]
}

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def check_permission(conn, user_id, action):
    cursor = conn.cursor()
    # Получаем роль пользователя
    cursor.execute("""
        SELECT r.role_name FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    if not row:
        return False
    
    role = row[0]
    allowed_actions = PERMISSIONS.get(role, [])
    return action.upper() in allowed_actions

def main():
    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("ДОБАВЛЕНИЕ НОВЫХ РОЛЕЙ")
    print("=" * 60)
    # Добавляем роли для администрирования (если их нет)
    new_roles = ['admin_db', 'developer', 'reader']
    for role in new_roles:
        try:
            cursor.execute("INSERT INTO roles (role_name) VALUES (?)", (role,))
            print(f"Роль '{role}' добавлена.")
        except sqlite3.IntegrityError:
            print(f"Роль '{role}' уже существует.")
    conn.commit()

    print("\n" + "=" * 60)
    print("ПРОВЕРКА ПРАВ")
    print("=" * 60)

    # Найдем пользователя с ролью reader (обычный пользователь)
    cursor.execute("""
        SELECT u.user_id, u.last_name, r.role_name FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE r.role_name = 'reader' LIMIT 1
    """)
    reader_row = cursor.fetchone()
    
    if reader_row:
        user_id, name, role = reader_row
        print(f"Пользователь {name} (роль: {role})")
        print(f"  Может ли сделать DELETE? {check_permission(conn, user_id, 'DELETE')}")
        print(f"  Может ли сделать SELECT? {check_permission(conn, user_id, 'SELECT')}")
    else:
        print("Пользователь с ролью 'reader' не найден. Создайте его через SQL.")

    # Найдем администратора (обычно это admin)
    cursor.execute("""
        SELECT u.user_id, u.last_name, r.role_name FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.login = 'admin'
    """)
    admin_row = cursor.fetchone()

    if admin_row:
        user_id, name, role = admin_row
        print(f"\nПользователь {name} (роль: {role})")
        print(f"  Может ли сделать DELETE? {check_permission(conn, user_id, 'DELETE')}")

    conn.close()

if __name__ == "__main__":
    main()