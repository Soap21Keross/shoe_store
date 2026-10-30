import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "shoe_store.sqlite")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "backups")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def backup_simple():
    """Бэкап через shutil (простое копирование файла)"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}.sqlite")
    shutil.copy2(DB_PATH, backup_path)
    print(f"Бэкап (simple) создан: {backup_path}")
    return backup_path

def backup_safe():
    """Бэкап через API SQLite (безопасное копирование)"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    backup_path = os.path.join(BACKUP_DIR, f"backup_safe_{timestamp}.sqlite")
    
    source = sqlite3.connect(DB_PATH)
    dest = sqlite3.connect(backup_path)
    source.backup(dest)
    source.close()
    dest.close()
    print(f"Бэкап (safe) создан: {backup_path}")
    return backup_path

def check_integrity(conn):
    """Проверка целостности базы"""
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()[0]
    print(f"Результат проверки целостности: {result}")
    return result

def get_db_stats(conn):
    """Сбор статистики базы"""
    cursor = conn.cursor()
    cursor.execute("PRAGMA page_size;")
    page_size = cursor.fetchone()[0]
    cursor.execute("PRAGMA page_count;")
    page_count = cursor.fetchone()[0]
    total_size = page_size * page_count

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    print("\n" + "=" * 60)
    print("СТАТИСТИКА БАЗЫ")
    print("=" * 60)
    print(f"Размер страницы: {page_size} байт")
    print(f"Количество страниц: {page_count}")
    print(f"Общий размер базы: {total_size} байт")
    print(f"Таблицы ({len(tables)}): {', '.join(tables)}")
    return total_size, tables

def main():
    print("=" * 60)
    print("АДМИНИСТРИРОВАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    conn = get_connection()

    # 1. Проверка целостности
    check_integrity(conn)
    
    # 2. Бэкапы
    backup_simple()
    backup_safe()

    # 3. Статистика
    get_db_stats(conn)

    conn.close()

if __name__ == "__main__":
    main()