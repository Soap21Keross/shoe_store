import sqlite3
import os
from datetime import datetime

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def main():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Создаем таблицу audit_log, если ее нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            operation TEXT NOT NULL,
            record_id INTEGER,
            old_value TEXT,
            new_value TEXT,
            changed_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()

    # 2. Выполняем скрипт с триггерами
    sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "triggers.sql")
    with open(sql_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    conn.commit()
    print("Триггеры успешно созданы.\n")

    # 3. Добавляем поле updated_at (если его нет)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN updated_at TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Поле уже существует

    # 4. Проверка аудита цен
    print("=" * 60)
    print("ПРОВЕРКА АУДИТА ЦЕН (UPDATE products)")
    print("=" * 60)
    cursor.execute("SELECT product_id, price FROM products LIMIT 1")
    prod = cursor.fetchone()
    if prod:
        p_id, old_price = prod
        new_price = old_price + 1000
        cursor.execute("UPDATE products SET price = ? WHERE product_id = ?", (new_price, p_id))
        conn.commit()
        print(f"Цена товара {p_id} изменена с {old_price} на {new_price}")
        
        cursor.execute("SELECT * FROM audit_log WHERE table_name = 'products' ORDER BY log_id DESC LIMIT 1")
        log = cursor.fetchone()
        if log:
            print(f"Запись в логе: ID={log[0]}, Таблица={log[1]}, Действие={log[2]}, Старое={log[4]}, Новое={log[5]}\n")
        else:
            print("Ошибка: запись в лог не добавилась!\n")

    # 5. Проверка списания остатков (INSERT order_items)
    print("=" * 60)
    print("ПРОВЕРКА СПИСАНИЯ ОСТАТКОВ (INSERT order_items)")
    print("=" * 60)
    
    cursor.execute("SELECT user_id FROM users LIMIT 1")
    user_id = cursor.fetchone()[0]
    cursor.execute("SELECT stock_item_id, quantity FROM stock_items WHERE quantity > 5 LIMIT 1")
    stock = cursor.fetchone()
    
    if stock:
        stock_id, qty_before = stock
        cursor.execute("INSERT INTO orders (user_id) VALUES (?)", (user_id,))
        order_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO order_items (order_id, stock_item_id, quantity, price) VALUES (?, ?, 2, 1000)", (order_id, stock_id))
        conn.commit()
        
        cursor.execute("SELECT quantity FROM stock_items WHERE stock_item_id = ?", (stock_id,))
        qty_after = cursor.fetchone()[0]
        print(f"Остаток до: {qty_before}, после: {qty_after}")
        if qty_before - qty_after == 2:
            print("РЕЗУЛЬТАТ: Списание остатков работает корректно!\n")
        else:
            print("РЕЗУЛЬТАТ: Ошибка списания!\n")

    # 6. Проверка запрета на удаление пользователя с заказами
    print("=" * 60)
    print("ПРОВЕРКА ЗАПРЕТА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    try:
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        print("ОШИБКА: Пользователь был удален, хотя у него есть заказы!\n")
    except sqlite3.IntegrityError as e:
        print(f"УСПЕХ: Удаление запрещено. Сообщение: {e}\n")
        conn.rollback()

    # 7. Проверка аудита удаления заказа
    print("=" * 60)
    print("ПРОВЕРКА АУДИТА УДАЛЕНИЯ ЗАКАЗА")
    print("=" * 60)
    if 'order_id' in locals():
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        conn.commit()
        cursor.execute("SELECT * FROM audit_log WHERE table_name = 'orders' ORDER BY log_id DESC LIMIT 1")
        log = cursor.fetchone()
        if log:
            print(f"Запись в логе: ID={log[0]}, Таблица={log[1]}, Действие={log[2]}, ID заказа={log[3]}\n")
        else:
            print("Ошибка: запись об удалении заказа не добавилась!\n")

    conn.close()

if __name__ == "__main__":
    main()