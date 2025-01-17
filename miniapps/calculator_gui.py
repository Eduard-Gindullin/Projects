import tkinter as tk
from tkinter import messagebox


def calculate():
    try:
        expression = entry.get()
        result = eval(expression)
        result_label.config(text=result)
    except:
        messagebox.showerror("Ошибка", "неверное выражение")

window = tk.Tk()
window.geometry("450x450")
window.title("Калькулятор")

label = tk.Label(window, text="Ввдедите выражение")
label.pack(pady=15)

entry = tk.Entry(window, width=30)
entry.pack(pady=15)

calculate_button = tk.Button(window, text="Посчитать результат", command=calculate)
calculate_button.pack(pady=15)

result_label = tk.Label(window, text="")
result_label.pack(pady=15)

window.mainloop()
