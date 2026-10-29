import sqlite3
import os
import sys

# Импортируем наши функции из файла app_functions.py
sys.path.append(os.path.dirname(__file__))
from app_functions import (
    calc_discount, pluralize_items, format_full_name, 
    place_order, cancel_order, get_client_tier, get_client_loyalty_days
)

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Регистрируем функции в SQLite
    conn.create_function("calc_discount", 2, calc_discount)
    conn.create_function("pluralize_items", 1, pluralize_items)
    conn.create_function("format_full_name", 3, format_full_name)
    conn.create_function("get_client_tier", 1, get_client_tier)
    conn.create_function("get_client_loyalty_days", 1, get_client_loyalty_days)
    
    return conn

# ЮНИТ-ТЕСТЫ (Unit Tests)

def test_calc_discount():
    print("Тест: calc_discount...")
    assert calc_discount(1000, 10) == 900.0
    assert calc_discount(1000, -5) == 1000.0 # Скидка меньше 0
    assert calc_discount(1000, 150) == 0.0   # Скидка больше 100
    assert calc_discount(None, 10) == 0.0
    assert calc_discount(1000, None) == 0.0
    assert calc_discount("1000", "10") == 900.0
    print("  OK")

def test_pluralize_items():
    print("Тест: pluralize_items...")
    assert pluralize_items(1) == "1 товар"
    assert pluralize_items(2) == "2 товара"
    assert pluralize_items(5) == "5 товаров"
    assert pluralize_items(11) == "11 товаров"
    assert pluralize_items(21) == "21 товар"
    assert pluralize_items(None) == "0 товаров"
    print("  OK")

def test_format_full_name():
    print("Тест: format_full_name...")
    assert format_full_name("иванов", "иван", "иванович") == "Иванов И.И."
    assert format_full_name("Петров", "Петр", None) == "Петров П."
    assert format_full_name(None, "Иван", "Иванович") == "Аноним"
    assert format_full_name("", "Иван", None) == "Аноним"
    print("  OK")

def test_get_client_tier():
    print("Тест: get_client_tier...")
    assert get_client_tier(0) == "Новичок"
    assert get_client_tier(4999) == "Новичок"
    assert get_client_tier(5000) == "Бронза"
    assert get_client_tier(25000) == "Серебро"
    assert get_client_tier(80000) == "Золото"
    assert get_client_tier(150000) == "Платина"
    assert get_client_tier(None) == "Без статуса"
    assert get_client_tier(-100) == "Без статуса"
    print("  OK")

def test_transactions():
    print("Тест: Транзакции (place_order, cancel_order)...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # Найдем любой валидный user_id, product_id и size_id из базы
    cursor.execute("SELECT user_id FROM users LIMIT 1")
    user_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT product_id, size_id, quantity FROM stock_items WHERE quantity > 5 LIMIT 1")
    row = cursor.fetchone()
    if not row:
        print("  Пропущено: нет товаров с остатком > 5")
        conn.close()
        return
    product_id, size_id, initial_qty = row

    # 1. Успешное создание заказа
    assert place_order(conn, user_id, product_id, size_id, 2) == True
    
    cursor.execute("SELECT quantity FROM stock_items WHERE product_id=? AND size_id=?", (product_id, size_id))
    new_qty = cursor.fetchone()[0]
    assert new_qty == initial_qty - 2, "Остаток не уменьшился!"
    
    # Найдем order_id последнего заказа
    cursor.execute("SELECT MAX(order_id) FROM orders")
    order_id = cursor.fetchone()[0]

    # 2. Отмена заказа
    assert cancel_order(conn, order_id) == True
    
    cursor.execute("SELECT quantity FROM stock_items WHERE product_id=? AND size_id=?", (product_id, size_id))
    restored_qty = cursor.fetchone()[0]
    assert restored_qty == initial_qty, "Остаток не восстановился!"

    conn.close()
    print("  OK")

# ЗАПУСК ЗАПРОСОВ

def run_sql_queries():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("ЗАПРОС 1. Цена со скидкой 20%")
    print("="*70)
    cursor.execute("SELECT product_name, price, calc_discount(price, 20) AS discount_price FROM products;")
    for row in cursor.fetchall():
        print(f"{row[0]} | Цена: {row[1]} | Со скидкой: {row[2]}")
        
    print("\n" + "="*70)
    print("ЗАПРОС 2. ФИО (с заменой на 'Аноним' если нет отчества)")
    print("="*70)
    cursor.execute("SELECT format_full_name(last_name, first_name, middle_name) AS fio FROM users;")
    for row in cursor.fetchall():
        print(row[0])

    print("\n" + "="*70)
    print("ЗАПРОС 3. Количество товаров в заказах (с склонением)")
    print("="*70)
    cursor.execute("SELECT order_id, pluralize_items(quantity) AS items_count FROM order_items LIMIT 5;")
    for row in cursor.fetchall():
        print(f"Заказ {row[0]}: {row[1]}")

    print("\n" + "="*70)
    print("ЗАПРОС 4. Сумма заказа со скидкой 10% и ФИО")
    print("="*70)
    # Считаем сумму, округляем и применяем скидку
    cursor.execute("""
        SELECT 
            format_full_name(u.last_name, u.first_name, u.middle_name) AS fio,
            SUM(oi.quantity * oi.price) AS total,
            calc_discount(SUM(oi.quantity * oi.price), 10) AS total_discount
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_id
        LIMIT 5;
    """)
    for row in cursor.fetchall():
        print(f"{row[0]} | Сумма: {row[1]} | Со скидкой 10%: {row[2]}")

    print("\n" + "="*70)
    print("ЗАПРОС 5. Аналитика клиентов (уровень и дни лояльности)")
    print("="*70)
    cursor.execute("""
        SELECT 
            format_full_name(u.last_name, u.first_name, u.middle_name) AS fio,
            SUM(oi.quantity * oi.price) AS total_spent,
            get_client_tier(SUM(oi.quantity * oi.price)) AS tier,
            get_client_loyalty_days(MIN(o.order_date)) AS loyalty_days
        FROM users u
        JOIN orders o ON u.user_id = o.user_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY u.user_id;
    """)
    for row in cursor.fetchall():
        print(f"{row[0]} | Сумма: {row[1]} | Уровень: {row[2]} | Дней с нами: {row[3]}")

    conn.close()

if __name__ == "__main__":
    print("ЗАПУСК ТЕСТОВ...")
    test_calc_discount()
    test_pluralize_items()
    test_format_full_name()
    test_get_client_tier()
    test_transactions()
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!\n")
    
    run_sql_queries()