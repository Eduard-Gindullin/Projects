# krug

Библиотека для вычисления площади круга и треугольника (по трем сторонам), а также проверки треугольника на прямоугольность. Содержит GUI на tkinter.

# Возможности
- Вычисление площади круга по радиусу
- Вычисление площади треугольника по трем сторонам
- Проверка треугольника на прямоугольность
- Легко расширяется для других фигур (наследование от Figure)
- Фабрика для создания фигур без знания типа в compile-time
- GUI для пользователей
- Юнит-тесты

# Пример использования (Python)
```python
from krug import Circle, Triangle
from krug.factory import FigureFactory

c = Circle(2)
print(c.area())  # 12.566...

t = Triangle(3, 4, 5)
print(t.area())  # 6.0
print(t.is_right())  # True

# Через фабрику
f = FigureFactory.create_figure(radius=1)
print(f.area())
```

# Запуск GUI
```bash
python -m krug.gui
```

# Тесты
```bash
python -m krug.test_geometry
```

# Добавление новых фигур
1. Создайте класс, наследующий Figure, и реализуйте метод area().
2. Добавьте обработку в FigureFactory.create_figure(). 