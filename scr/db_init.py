import sqlite3
import os


def get_connection():
    # Определяем путь к папке db и создаём её, если она не существует
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
    os.makedirs(db_dir, exist_ok=True)
    
    # Путь к файлу базы данных
    db_path = os.path.join(db_dir, "shoe_store.sqlite")
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    
    # Включаем проверку внешних ключей (по умолчанию в SQLite отключена)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Таблица ролей
    # Хранит справочник ролей пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL UNIQUE
        )
    """)

    # 2. Таблица размеров
    # Справочник размеров обуви. Добавлено ограничение CHECK на диапазон от 20 до 50
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sizes (
            size_id INTEGER PRIMARY KEY AUTOINCREMENT,
            size_value REAL NOT NULL UNIQUE CHECK (size_value > 20 AND size_value < 50)
        )
    """)

    # 3. Таблица товаров
    # Добавлены ограничения CHECK на непустое имя и цену в разумных пределах
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL CHECK (length(product_name) > 0),
            category TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            price NUMERIC NOT NULL CHECK (price > 0 AND price < 1000000),
            image_path TEXT
        )
    """)

    # 4. Таблица пользователей
    # Добавлено ограничение CHECK на длину логина (от 3 до 20 символов)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            login TEXT NOT NULL UNIQUE CHECK (length(login) >= 3 AND length(login) <= 20),
            role_id INTEGER NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE RESTRICT
        )
    """)

    # 5. Таблица товарных позиций (склад)
    # Ограничение CHECK на неотрицательное количество
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_items (
            stock_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            size_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
            FOREIGN KEY (size_id) REFERENCES sizes(size_id) ON DELETE RESTRICT
        )
    """)

    # 6. Таблица заказов
    # Добавлено ограничение CHECK на корректность формата даты (ISO 8601)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TEXT NOT NULL DEFAULT CURRENT_DATE CHECK (date(order_date) IS NOT NULL),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT
        )
    """)

    # 7. Таблица состава заказов
    # Ограничения CHECK на положительное количество и цену
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            stock_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            price NUMERIC NOT NULL CHECK (price > 0),
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (stock_item_id) REFERENCES stock_items(stock_item_id) ON DELETE RESTRICT
        )
    """)

    # --- Создание индексов ---
    # Индексы на внешние ключи (ускоряют JOIN)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_items_product_id ON stock_items(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_items_size_id ON stock_items(size_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_stock_item_id ON order_items(stock_item_id)")

    # Индексы на поля поиска и сортировки
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_manufacturer ON products(manufacturer)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date)")

    conn.commit()
    conn.close()
    print("База данных успешно создана со всеми ограничениями и индексами")


if __name__ == "__main__":
    init_db()