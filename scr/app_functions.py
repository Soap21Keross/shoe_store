def pluralize_items(count):
    """Склоняет слово 'товар' в зависимости от числа."""
    if count is None:
        return "0 товаров"
    try:
        count = int(count)
    except (ValueError, TypeError):
        return "0 товаров"
        
    n = abs(count) % 100
    if 11 <= n <= 19:
        word = "товаров"
    else:
        n = n % 10
        if n == 1:
            word = "товар"
        elif n in (2, 3, 4):
            word = "товара"
        else:
            word = "товаров"
            
    # ОБЯЗАТЕЛЬНО ВОЗВРАЩАЕМ ЧИСЛО И СЛОВО
    return f"{count} {word}"