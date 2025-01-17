import tkinter as tk
from tkinter import messagebox
import random

def yes():
    messagebox.showinfo("Отлично!", "Мы так и думали")

def no(event):
    new_x = random.randrange(50,450)
    new_y = random.randrange(50,450)
    button2.place(x=new_x, y=new_y)



window = tk.Tk()
window.geometry("550x550")
window.title("Нажми на кнопку")
window.resizable(False, False)

label = tk.Label(text="Вы согласны с утверждением?")
label.place(x=180, y=50, width=200, height=50)

button1 = tk.Button(window, text="ДА", command=yes)
button1.place(x=180, y=250, width=50, height=20)

button2 = tk.Button(window, text="НЕТ")
button2.place(x=280, y=250, width=50, height=20)

button2.bind("<Enter>", no)


window.mainloop()