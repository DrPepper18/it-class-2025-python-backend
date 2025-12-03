# test_calculator.py
import pytest
from calculator import *

# 🎯 ТЕСТ 1: Простое сложение
def test_sum_positive():
    """Тест сложения положительных чисел"""
    assert sum_numbers(2, 3) == 5
    assert sum_numbers(10, 20) == 30

def test_sum_negative():
    """Тест сложения отрицательных чисел"""
    assert sum_numbers(-5, -3) == -8
    assert sum_numbers(5, -3) == 2

# 🎯 ТЕСТ 2: Умножение
def test_multiply():
    """Тест умножения"""
    assert multiply_numbers(3, 4) == 12
    assert multiply_numbers(0, 100) == 0
    assert multiply_numbers(-2, 5) == -10

# 🎯 ТЕСТ 3: Проверка чётности
def test_is_even():
    """Тест проверки чётности"""
    assert is_even(4) is True
    assert is_even(5) is False
    assert is_even(0) is True  # 0 - чётное!
    assert is_even(-2) is True

# 🎯 ТЕСТ 4: Деление с ошибкой
def test_divide_normal():
    """Нормальное деление"""
    assert divide_numbers(10, 2) == 5
    assert divide_numbers(9, 3) == 3

def test_divide_by_zero():
    """Деление на ноль вызывает ошибку"""
    with pytest.raises(ValueError) as error:
        divide_numbers(10, 0)
    
    # Проверяем текст ошибки
    assert str(error.value) == "На ноль делить нельзя!"

# 🎯 ТЕСТ 5: Обработка списков
def test_process_list():
    """Тест обработки списка"""
    # Обычный случай
    assert process_list([1, 2, 3, 4, 5]) == [4, 8]
    
    # Только нечётные
    assert process_list([1, 3, 5]) == []
    
    # Только чётные
    assert process_list([2, 4, 6]) == [4, 8, 12]

def test_process_list_wrong_input():
    """Неправильный ввод вызывает ошибку"""
    with pytest.raises(TypeError):
        process_list("это не список")  # Строка вместо списка
