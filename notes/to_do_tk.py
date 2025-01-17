import tkinter as tk
from tkinter import messagebox


taskList = []


def updateListBox():
    tasks.delete(0, tk.END)
    for i in taskList:
        tasks.insert(tk.END, i)


def add_task():
    currentTask = taskEntry.get()
    if currentTask != "":
        taskEntry.delete(0, tk.END)
        taskList.append(currentTask)
        updateListBox()
    else:
        messagebox.showerror("Ошибка", "Поле пустое")


def delete_task():
    selectTask = tasks.selection_get()
    taskList.remove(selectTask)
    updateListBox()


def delete_all_tasks():
    answer = messagebox.askyesno("Подтвердите удаление", "Удалить все задачи?")
    if answer:
        taskList.clear()
        updateListBox()


def sort():
    taskList.sort()
    updateListBox()


def sortReverse():
    taskList.sort(reverse=True)
    updateListBox()


window = tk.Tk()
window.geometry("400x650")
window.title("ToDo")
window.resizable(False, False)

addButton = tk.Button(window, text="Добавить", command=add_task)
addButton.place(relx=0.05, rely=0.1, relwidth=0.3, relheight=0.1)

delButton = tk.Button(window, text="Удалить", command=delete_task)
delButton.place(relx=0.05, rely=0.2, relwidth=0.3, relheight=0.1)

delAllButton = tk.Button(window, text="Удалить все", command=delete_all_tasks)
delAllButton.place(relx=0.05, rely=0.3, relwidth=0.3, relheight=0.1)

sortButton = tk.Button(window, text="Сортировать", command=sort)
sortButton.place(relx=0.05, rely=0.4, relwidth=0.3, relheight=0.1)

sortReverseButton = tk.Button(window, text="Обр. сортировка", command=sortReverse)
sortReverseButton.place(relx=0.05, rely=0.5, relwidth=0.3, relheight=0.1)

enterLabel = tk.Label(window, text="Введите задачу")
enterLabel.place(relx=0.4, rely=0.1)

taskEntry = tk.Entry(window)
taskEntry.place(relx=0.4, rely=0.15, relwidth=0.55)

tasks = tk.Listbox(window)
tasks.place(relx=0.4, rely=0.2, relwidth=0.55, relheight=0.6)

window.mainloop()
