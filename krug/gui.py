import tkinter as tk
from tkinter import ttk, messagebox
from .factory import FigureFactory

class GeometryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Калькулятор площадей фигур')  # Заголовок окна
        self.geometry('350x300')
        self.resizable(False, False)

        self.figure_type = tk.StringVar(value='Круг')  # Тип фигуры по умолчанию
        self.inputs = {}

        self.create_widgets()

    def create_widgets(self):
        # Выбор типа фигуры
        ttk.Label(self, text='Выберите фигуру:').pack(pady=5)
        figure_combo = ttk.Combobox(self, textvariable=self.figure_type, values=['Круг', 'Треугольник'], state='readonly')
        figure_combo.pack()
        figure_combo.bind('<<ComboboxSelected>>', self.update_fields)

        self.fields_frame = ttk.Frame(self)
        self.fields_frame.pack(pady=10)
        self.update_fields()

        self.result_label = ttk.Label(self, text='')
        self.result_label.pack(pady=10)

        calc_btn = ttk.Button(self, text='Вычислить площадь', command=self.calculate)
        calc_btn.pack(pady=5)

        self.right_label = ttk.Label(self, text='')
        self.right_label.pack(pady=5)

    def update_fields(self, event=None):
        # Обновление полей ввода при смене типа фигуры
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.inputs.clear()
        if self.figure_type.get() == 'Круг':
            self.add_field('Радиус')
        elif self.figure_type.get() == 'Треугольник':
            self.add_field('Сторона a')
            self.add_field('Сторона b')
            self.add_field('Сторона c')

    def add_field(self, name):
        # Добавление поля ввода
        row = ttk.Frame(self.fields_frame)
        row.pack(fill='x', pady=2)
        ttk.Label(row, text=f'{name}:', width=12).pack(side='left')
        var = tk.StringVar()
        entry = ttk.Entry(row, textvariable=var)
        entry.pack(side='left', fill='x', expand=True)
        self.inputs[name] = var

    def calculate(self):
        # Вычисление площади и проверка на прямоугольность
        try:
            if self.figure_type.get() == 'Круг':
                params = {'radius': float(self.inputs['Радиус'].get())}
            elif self.figure_type.get() == 'Треугольник':
                params = {
                    'a': float(self.inputs['Сторона a'].get()),
                    'b': float(self.inputs['Сторона b'].get()),
                    'c': float(self.inputs['Сторона c'].get()),
                }
            figure = FigureFactory.create_figure(**params)
            area = figure.area()
            self.result_label.config(text=f'Площадь: {area:.4f}')
            if hasattr(figure, 'is_right'):
                is_right = figure.is_right()
                self.right_label.config(text=f'Треугольник прямоугольный: {"Да" if is_right else "Нет"}')
            else:
                self.right_label.config(text='')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

if __name__ == '__main__':
    app = GeometryApp()
    app.mainloop() 