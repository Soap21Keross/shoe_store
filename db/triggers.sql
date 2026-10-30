-- Создаем таблицу для аудита (логов)
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    changed_at TEXT DEFAULT (datetime('now'))
);

-- Добавляем поле updated_at в таблицу users (если его еще нет)
-- В SQLite нельзя использовать IF NOT EXISTS для ALTER TABLE, поэтому просто добавим
-- Если поле уже есть, скрипт выдаст ошибку, но мы ее проигнорируем в Python-скрипте
-- (Для простоты мы просто удалим триггеры перед созданием, чтобы они не дублировались)

DROP TRIGGER IF EXISTS trg_audit_price_change;
DROP TRIGGER IF EXISTS trg_audit_order_delete;
DROP TRIGGER IF EXISTS trg_update_user_timestamp;
DROP TRIGGER IF EXISTS trg_decrease_stock;
DROP TRIGGER IF EXISTS trg_prevent_user_delete;
DROP TRIGGER IF EXISTS trg_check_negative_stock;

-- Задание 1.1. Логирование изменения цен
CREATE TRIGGER trg_audit_price_change
AFTER UPDATE ON products
WHEN OLD.price != NEW.price
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id, old_value, new_value)
    VALUES ('products', 'UPDATE', OLD.product_id, OLD.price, NEW.price);
END;

-- Задание 1.2. Логирование удаления заказов
CREATE TRIGGER trg_audit_order_delete
AFTER DELETE ON orders
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id, old_value)
    VALUES ('orders', 'DELETE', OLD.order_id, 'Заказ удален');
END;

-- Задание 1.3. Автообновление времени изменения пользователя
-- (Для этого нужно, чтобы в таблице users было поле updated_at)
CREATE TRIGGER trg_update_user_timestamp
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = datetime('now') WHERE user_id = NEW.user_id;
END;

-- Задание 2.1. Автоматическое списание остатков
CREATE TRIGGER trg_decrease_stock
AFTER INSERT ON order_items
BEGIN
    UPDATE stock_items
    SET quantity = quantity - NEW.quantity
    WHERE stock_item_id = NEW.stock_item_id;
END;

-- Задание 2.2. Запрет удаления пользователя с заказами
CREATE TRIGGER trg_prevent_user_delete
BEFORE DELETE ON users
WHEN (SELECT COUNT(*) FROM orders WHERE user_id = OLD.user_id) > 0
BEGIN
    SELECT RAISE(ABORT, 'Нельзя удалить пользователя с активными заказами');
END;

-- Задание 2.3. Проверка на отрицательное количество
CREATE TRIGGER trg_check_negative_stock
BEFORE INSERT ON stock_items
WHEN NEW.quantity < 0
BEGIN
    SELECT RAISE(ABORT, 'Количество не может быть отрицательным');
END;