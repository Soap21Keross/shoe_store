import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def run_query(cursor, title, sql):
    print("=" * 70)
    print(title)
    print("=" * 70)
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        print(" | ".join(columns))
        print("-" * 70)
        for row in rows:
            print(" | ".join(str(val) if val is not None else "None" for val in row))
        print(f"Всего записей: {len(rows)}")
    except Exception as e:
        print(f"Ошибка выполнения: {e}")
    print()

def main():
    # Путь к файлу с запросами
    sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "queries", "04_check_queries.sql")
    
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Разделяем файл по комментариям "-- Запрос"
    parts = content.split("-- Запрос")
    queries = []
    
    for part in parts[1:]:
        lines = part.strip().split("\n")
        title = "-- Запрос " + lines[0].strip()
        sql = "\n".join(lines[1:]).strip()
        if sql:
            queries.append((title, sql))

    conn = get_connection()
    cursor = conn.cursor()

    for title, sql in queries:
        run_query(cursor, title, sql)

    conn.close()

if __name__ == "__main__":
    main()