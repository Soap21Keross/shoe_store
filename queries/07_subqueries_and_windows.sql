-- Задание 1. Скалярные подзапросы
-- Запрос 1: Товары дороже средней цены
SELECT product_name, price 
FROM products 
WHERE price > (SELECT AVG(price) FROM products);

-- Запрос 2: Пользователь, сделавший самый дорогой заказ
SELECT u.last_name, u.first_name 
FROM users u 
JOIN orders o ON u.user_id = o.user_id 
WHERE o.order_id = (
    SELECT order_id 
    FROM order_items 
    GROUP BY order_id 
    ORDER BY SUM(quantity * price) DESC 
    LIMIT 1
);

-- Задание 2. Подзапросы с IN и EXISTS
-- Запрос 3: Клиенты, у которых есть хотя бы один заказ (IN)
SELECT last_name 
FROM users 
WHERE user_id IN (SELECT user_id FROM orders);

-- Запрос 4: Пользователи без заказов (NOT EXISTS)
SELECT u.last_name 
FROM users u 
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.user_id);

-- Запрос 5: Товары, которые ни разу не заказывали (NOT IN)
SELECT product_name 
FROM products 
WHERE product_id NOT IN (
    SELECT si.product_id 
    FROM stock_items si 
    JOIN order_items oi ON si.stock_item_id = oi.stock_item_id
);

-- Задание 3. Ранжирование и группировка (Оконные функции)
-- Запрос 6: Ранжирование клиентов по сумме заказов
SELECT u.last_name, 
       SUM(oi.quantity * oi.price) AS total_sum,
       RANK() OVER(ORDER BY SUM(oi.quantity * oi.price) DESC) AS rank
FROM users u 
JOIN orders o ON u.user_id = o.user_id 
JOIN order_items oi ON o.order_id = oi.order_id 
GROUP BY u.user_id;

-- Запрос 7: Порядковый номер заказа клиента (ROW_NUMBER)
SELECT o.order_id, u.last_name, o.order_date,
       ROW_NUMBER() OVER(PARTITION BY o.user_id ORDER BY o.order_date ASC) AS order_number
FROM orders o 
JOIN users u ON o.user_id = u.user_id;

-- Запрос 8: Нумерация товаров внутри категории по цене (ROW_NUMBER + PARTITION BY)
SELECT category, product_name, price,
       ROW_NUMBER() OVER(PARTITION BY category ORDER BY price DESC) AS rn
FROM products;

-- Запрос 9: Самый дорогой товар в каждой категории (через подзапрос в FROM)
SELECT category, product_name, price 
FROM (
    SELECT category, product_name, price,
           ROW_NUMBER() OVER(PARTITION BY category ORDER BY price DESC) AS rn
    FROM products
) sub 
WHERE sub.rn = 1;

-- Задание 4. Нарастающие итоги и сдвиги
-- Запрос 10: Накопительная сумма продаж по датам
SELECT o.order_date, 
       SUM(oi.quantity * oi.price) AS daily_sum,
       SUM(SUM(oi.quantity * oi.price)) OVER(ORDER BY o.order_date) AS running_total
FROM orders o 
JOIN order_items oi ON o.order_id = oi.order_id 
GROUP BY o.order_date;

-- Запрос 11: Дата текущего и предыдущего заказа (LAG)
SELECT o.order_id, 
       o.user_id, 
       o.order_date, 
       LAG(o.order_date) OVER(PARTITION BY o.user_id ORDER BY o.order_date) AS prev_order_date,
       ROUND(julianday(o.order_date) - julianday(LAG(o.order_date) OVER(PARTITION BY o.user_id ORDER BY o.order_date)), 0) AS days_diff
FROM orders o;