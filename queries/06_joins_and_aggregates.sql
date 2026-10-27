-- Задание 1. Простые JOIN
-- Запрос 1: Список всех заказов с ФИО клиента
SELECT o.order_id, o.order_date, u.last_name, u.first_name 
FROM orders o 
JOIN users u ON o.user_id = u.user_id;

-- Запрос 2: Товарные позиции с названием модели и размером
SELECT si.stock_item_id, p.product_name, s.size_value, si.quantity 
FROM stock_items si 
JOIN products p ON si.product_id = p.product_id 
JOIN sizes s ON si.size_id = s.size_id;

-- Запрос 3: Заказы с ФИО и названием купленного товара
SELECT o.order_id, u.last_name, p.product_name 
FROM orders o 
JOIN users u ON o.user_id = u.user_id 
JOIN order_items oi ON o.order_id = oi.order_id 
JOIN stock_items si ON oi.stock_item_id = si.stock_item_id 
JOIN products p ON si.product_id = p.product_id;

-- Запрос 4: Список всех пользователей и количество их заказов (LEFT JOIN)
SELECT u.last_name, u.first_name, o.order_id 
FROM users u 
LEFT JOIN orders o ON u.user_id = o.user_id;

-- Задание 2. Базовые агрегатные функции
-- Запрос 5: Общее количество пользователей
SELECT COUNT(*) AS total_users FROM users;

-- Запрос 6: Средняя цена всех товаров
SELECT AVG(price) AS avg_price FROM products;

-- Запрос 7: Самый дорогой и самый дешевый товар
SELECT MAX(price) AS max_price, MIN(price) AS min_price FROM products;

-- Запрос 8: Общая выручка (сумма всех проданных товаров)
SELECT SUM(quantity * price) AS total_revenue FROM order_items;

-- Задание 3. Группировка GROUP BY
-- Запрос 9: Количество товаров в каждой категории
SELECT category, COUNT(*) AS products_count 
FROM products 
GROUP BY category;

-- Запрос 10: Список производителей и средняя цена их товаров
SELECT manufacturer, AVG(price) AS avg_price 
FROM products 
GROUP BY manufacturer;

-- Запрос 11: ФИО пользователя и общая сумма его заказов
SELECT u.last_name, u.first_name, SUM(oi.quantity * oi.price) AS total_sum 
FROM users u 
JOIN orders o ON u.user_id = o.user_id 
JOIN order_items oi ON o.order_id = oi.order_id 
GROUP BY u.user_id, u.last_name, u.first_name;

-- Запрос 12: Статистика продаж по моделям (сколько пар продано)
SELECT p.product_name, SUM(oi.quantity) AS total_pairs_sold 
FROM order_items oi 
JOIN stock_items si ON oi.stock_item_id = si.stock_item_id 
JOIN products p ON si.product_id = p.product_id 
GROUP BY p.product_name;

-- Запрос 13: Список размеров и количество товарных позиций в этом размере
SELECT s.size_value, COUNT(si.stock_item_id) AS items_count 
FROM sizes s 
LEFT JOIN stock_items si ON s.size_id = si.size_id 
GROUP BY s.size_value;

-- Задание 4. Фильтрация групп HAVING
-- Запрос 14: Категории, в которых больше 3 моделей
SELECT category, COUNT(*) AS model_count 
FROM products 
GROUP BY category 
HAVING COUNT(*) > 3;

-- Запрос 15: Клиенты, сделавшие больше 2 заказов
SELECT u.last_name, u.first_name, COUNT(o.order_id) AS orders_count 
FROM users u 
JOIN orders o ON u.user_id = o.user_id 
GROUP BY u.user_id, u.last_name, u.first_name 
HAVING COUNT(o.order_id) > 2;

-- Запрос 16: Модели обуви, общая сумма продаж которых превысила 100000
SELECT p.product_name, SUM(oi.quantity * oi.price) AS total_sales 
FROM products p 
JOIN stock_items si ON p.product_id = si.product_id 
JOIN order_items oi ON si.stock_item_id = oi.stock_item_id 
GROUP BY p.product_name 
HAVING SUM(oi.quantity * oi.price) > 100000;

-- Задание 5. Комбинированный аналитический отчет
-- Запрос 17: Топ-3 самых популярных размеров обуви
SELECT s.size_value, SUM(oi.quantity) AS total_bought 
FROM sizes s 
JOIN stock_items si ON s.size_id = si.size_id 
JOIN order_items oi ON si.stock_item_id = oi.stock_item_id 
GROUP BY s.size_value 
ORDER BY total_bought DESC 
LIMIT 3;

-- Запрос 18: Пользователи, которые ни разу ничего не заказывали
SELECT u.last_name, u.first_name 
FROM users u 
LEFT JOIN orders o ON u.user_id = o.user_id 
WHERE o.order_id IS NULL;

-- Запрос 19: Средний чек (средняя стоимость одного заказа)
SELECT AVG(order_total) AS average_check 
FROM (
    SELECT SUM(quantity * price) AS order_total 
    FROM order_items 
    GROUP BY order_id
);

-- Запрос 20: Производитель, чьи товары принесли наибольшую выручку
SELECT p.manufacturer, SUM(oi.quantity * oi.price) AS total_revenue 
FROM products p 
JOIN stock_items si ON p.product_id = si.product_id 
JOIN order_items oi ON si.stock_item_id = oi.stock_item_id 
GROUP BY p.manufacturer 
ORDER BY total_revenue DESC 
LIMIT 1;