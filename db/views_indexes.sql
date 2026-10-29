-- Задание 1. Создание представлений (VIEW)

-- Представление 1: Полная информация о заказах
DROP VIEW IF EXISTS v_orders_full;
CREATE VIEW v_orders_full AS
SELECT 
    o.order_id, 
    o.order_date, 
    u.last_name || ' ' || u.first_name || ' ' || COALESCE(u.middle_name, '') AS full_name,
    SUM(oi.quantity * oi.price) AS total_sum
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id;

-- Представление 2: Товары с остатками
DROP VIEW IF EXISTS v_products_with_stock;
CREATE VIEW v_products_with_stock AS
SELECT 
    p.product_name, 
    p.price, 
    s.size_value, 
    si.quantity AS available_quantity
FROM products p
JOIN stock_items si ON p.product_id = si.product_id
JOIN sizes s ON si.size_id = s.size_id;

-- Представление 3: Статистика по клиентам
DROP VIEW IF EXISTS v_user_stats;
CREATE VIEW v_user_stats AS
SELECT 
    u.last_name || ' ' || u.first_name AS full_name,
    u.login,
    COUNT(o.order_id) AS orders_count
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id;



-- Задание 2. Создание индексов

-- Шаг 5: Индекс на категорию товаров
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Шаг 6: Индекс на дату заказа
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);

-- Шаг 7: Индексы на внешние ключи
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_stock_items_product_id ON stock_items(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_items_size_id ON stock_items(size_id);

-- Шаг 8: Составной индекс (производитель + категория)
CREATE INDEX IF NOT EXISTS idx_products_manufacturer_category ON products(manufacturer, category);