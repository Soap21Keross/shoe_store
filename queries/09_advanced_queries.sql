-- 1. Вывести название товара, цену и цену со скидкой 20%
SELECT product_name, price, calc_discount(price, 20) AS discount_price 
FROM products;

-- 2. Вывести ФИО клиентов (с заменой на 'Аноним' если нет отчества)
SELECT format_full_name(last_name, first_name, middle_name) AS fio 
FROM users;

-- 3. Вывести количество проданных единиц товара в каждом заказе, используя pluralize_items
SELECT order_id, pluralize_items(quantity) AS items_count 
FROM order_items LIMIT 5;

-- 4. Соединить 1 и 2 запрос: вывести имя клиента и сумму его заказа со скидкой 10%
SELECT 
    format_full_name(u.last_name, u.first_name, u.middle_name) AS fio,
    SUM(oi.quantity * oi.price) AS total,
    calc_discount(SUM(oi.quantity * oi.price), 10) AS total_discount
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id
LIMIT 5;

-- 5. Аналитический запрос: уровень клиента и дни лояльности
SELECT 
    format_full_name(u.last_name, u.first_name, u.middle_name) AS fio,
    SUM(oi.quantity * oi.price) AS total_spent,
    get_client_tier(SUM(oi.quantity * oi.price)) AS tier,
    get_client_loyalty_days(MIN(o.order_date)) AS loyalty_days
FROM users u
JOIN orders o ON u.user_id = o.user_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY u.user_id;