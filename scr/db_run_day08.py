import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def run_script(cursor, filepath):
    print("=" * 70)
    print(f"ВЫПОЛНЕНИЕ СКРИПТА: {os.path.basename(filepath)}")
    print("=" * 70)
    with open(filepath, "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    try:
        cursor.executescript(sql_script)
        print("Скрипт выполнен успешно (VIEW и INDEX созданы).\n")
    except Exception as e:
        print(f"Ошибка выполнения скрипта: {e}\n")

def run_explain(cursor, title, sql):
    print("=" * 70)
    print(f"АНАЛИЗ: {title}")
    print("=" * 70)
    print(f"Запрос: {sql.strip()}")
    print("-" * 70)
    try:
        cursor.execute(f"EXPLAIN QUERY PLAN {sql}")
        rows = cursor.fetchall()
        for row in rows:
            print(row[-1]) # Выводим только описание плана
    except Exception as e:
        print(f"Ошибка: {e}")
    print()

def main():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Выполняем скрипт создания VIEW и INDEX
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "views_indexes.sql")
    run_script(cursor, sql_file)
    conn.commit()

    # 2. Проверяем, что VIEW работает
    print("=" * 70)
    print("ПРОВЕРКА РАБОТЫ ПРЕДСТАВЛЕНИЯ v_orders_full (LIMIT 3)")
    print("=" * 70)
    cursor.execute("SELECT * FROM v_orders_full LIMIT 3")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print()

    # 3. Задание 3. Анализ запросов через EXPLAIN
    run_explain(cursor, "Поиск по категории (с индексом)", "SELECT * FROM products WHERE category = 'Спортивная';")
    run_explain(cursor, "Поиск по производителю (без отдельного индекса)", "SELECT * FROM products WHERE manufacturer = 'Nike';")
    run_explain(cursor, "JOIN orders и users", "SELECT * FROM orders o JOIN users u ON o.user_id = u.user_id;")

    # 4. Задание 4. Попытка обновления VIEW
    print("=" * 70)
    print("ПОПЫТКА ОБНОВЛЕНИЯ ПРЕДСТАВЛЕНИЯ")
    print("=" * 70)
    try:
        # Создаем простое VIEW для теста
        cursor.execute("CREATE VIEW IF NOT EXISTS v_simple AS SELECT product_id, price FROM products;")
        cursor.execute("UPDATE v_simple SET price = 100 WHERE product_id = 1;")
        print("Обновление удалось (VIEW обновляемо).")
    except Exception as e:
        print(f"Ошибка при обновлении VIEW: {e}")
    print()

    conn.close()

if __name__ == "__main__":
    main()