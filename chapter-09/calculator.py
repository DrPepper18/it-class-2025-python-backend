# calculator.py

def sum_numbers(a, b):
    """Сложение двух чисел"""
    return a + b

def multiply_numbers(a, b):
    """Умножение двух чисел"""
    return a * b

def is_even(number):
    """Проверка чётности"""
    return number % 2 == 0

def divide_numbers(a, b):
    """Деление с обработкой ошибок"""
    if b == 0:
        raise ValueError("На ноль делить нельзя!")
    return a / b

def process_list(numbers):
    """Обработка списка: фильтр + преобразование"""
    if not isinstance(numbers, list):
        raise TypeError("Ожидается список!")
    
    # Оставляем только чётные и умножаем на 2
    return [x * 2 for x in numbers if x % 2 == 0]