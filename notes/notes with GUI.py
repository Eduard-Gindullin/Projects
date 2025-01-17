from datetime import datetime
import tkinter as tk

class DroneCatalog:
    def __init__(self, master):
        self.master = master
        master.title('Каталог дронов')
        master.geometry('1550x400')

        # Создание виджетов
        self.label_manufacturer = tk.Label(master, text='Производитель')
        self.entry_manufacturer = tk.Entry(master, width=10)
        self.label_model = tk.Label(master, text='Модель')
        self.entry_model = tk.Entry(master, width=10)
        self.label_mass = tk.Label(master, text='Масса дрона (кг)')
        self.entry_mass = tk.Entry(master, width=10)
        self.label_payload = tk.Label(master, text='Полезная нагрузка (кг)')
        self.entry_payload = tk.Entry(master, width=10)
        self.label_flight_distance = tk.Label(master, text='Максимальная дальность полёта (км)')
        self.entry_flight_distance = tk.Entry(master, width=10)
        self.label_speed = tk.Label(master, text='Максимальная скорость (км/ч)')
        self.entry_speed = tk.Entry(master, width=10)
        self.label_battery_life = tk.Label(master, text='Время работы от батареи (мин)')
        self.entry_battery_life = tk.Entry(master, width=10)
        self.button_create_note = tk.Button(master, text='Записать дрона в каталог', command=self.create_note)
        self.button_view_notes = tk.Button(master, text='Пролистать записи с начала', command=self.table_notes)
#        self.button_view_notes = tk.Button(master, text='удалить запись', command=self.delete_note)

        # Добавление виджетов на форму
        self.label_manufacturer.grid(column=0, row=0)
        self.entry_manufacturer.grid(column=1, row=0)
        self.label_model.grid(column=3, row=0)
        self.entry_model.grid(column=4, row=0)
        self.label_mass.grid(column=6, row=0)
        self.entry_mass.grid(column=7, row=0)
        self.label_payload.grid(column=9, row=0)
        self.entry_payload.grid(column=10, row=0)
        self.label_flight_distance.grid(column=0, row=2)
        self.entry_flight_distance.grid(column=1, row=2)        
        self.label_speed.grid(column=3, row=2)
        self.entry_speed.grid(column=4, row=2)
        self.label_battery_life.grid(column=6, row=2)
        self.entry_battery_life.grid(column=7, row=2)

        self.button_create_note.grid(column=3, row=4)
        self.button_view_notes.grid(column=4, row=4)

    # Функция для создания заметки
    def create_note(self):
        manufacturer = self.entry_manufacturer.get()
        model = self.entry_model.get()
        mass = self.entry_model.get()
        payload = self.entry_mass.get()
        flight_distance = self.entry_flight_distance.get()
        speed = self.entry_speed.get()
        battery_life = self.entry_battery_life.get()

        current_time = datetime.now()
        creation_time_str = current_time.strftime("%Y-%m-%d %H:%M")

        with open("notes.txt", "a", encoding='utf-8') as file:
            file.write(manufacturer + ';' + model + ';' + mass + ';' + payload + ';' + flight_distance + ';' + speed + ';' + battery_life + ';' + creation_time_str + '\n')
            file.close()

        self.clear_entries()
        self.display_message(f"Данные успешно сохранены! Время создания: {creation_time_str}.")


    # Функция удаления записи из каталога
        # def delete_note(self):
        #     with open("notes.txt", "a", encoding='utf-8') as file:
        #         file.write(manufacturer + ';' + model + ';' + mass + ';' + payload + ';' + flight_distance + ';' + speed + ';' + battery_life + ';' + creation_time_str + '\n')
        #     file.close()

        # self.clear_entries()
        # self.display_message(f"Данные успешно сохранены! Время создания: {creation_time_str}.")

      

    # Функция для просмотра заметок
    def view_notes(self):
        try:
            with open("notes.txt", "r", encoding='utf-8') as file:
                notes = file.readlines()
                if not notes:
                    print("Заметок пока нет")
                else:
                    self.display_notes(notes)
        except FileNotFoundError:
            print("Файл с заметками не найден. Создайте новую заметку")

    # Функция для отображения заметок
    def display_notes(self, notes):
        for note in notes:
            data = note.strip().split(';')
            manufacturer = data[0]
            model = data[1]
            mass = data[2]
            payload = data[3]
            flight_distance = data[4]
            speed = data[5]
            battery_life = data[6]
            creation_time = data[7]

            self.entry_manufacturer.delete(0, 'end')
            self.entry_manufacturer.insert(0, manufacturer)
            self.entry_model.delete(0, 'end')
            self.entry_model.insert(0, model)
            self.entry_mass.delete(0, 'end')
            self.entry_mass.insert(0, mass)
            self.entry_payload.delete(0, 'end')
            self.entry_payload.insert(0, payload)
            self.entry_flight_distance.delete(0, 'end')
            self.entry_flight_distance.insert(0, flight_distance)
            self.entry_speed.delete(0, 'end')
            self.entry_speed.insert(0, speed)
            self.entry_battery_life.delete(0, 'end')
            self.entry_battery_life.insert(0, battery_life)          

            # Обновление виджетов с новыми данными
            self.update_idletasks()
            self.master.update()

    # Вывод всех заметок в виде таблицы
    def table_notes(self):
        frame = tk.Frame(self.master, rows=8, columns=8)
        frame.pack(fill=tk.BOTH, expand=True)
        row = 0
        column = 0

        with open("notes.txt", "r", encoding='utf-8') as file:
           for line in file:
               data = line.strip().split(';')
               row += 1
               column = 0
               for item in data:
                   frame.add_cell(row, column, item)
                   column += 1

       # Добавление кнопок для выбора строки
        for i in range(len(notes)):
           button = tk.Button(frame, text="Выбрать", command=lambda row=i: self.select_row(row))
           frame.add_row(button, i+1)

       # Добавление кнопок для редактирования и удаления строк
        for row in range(1, len(notes)+1):
           buttons = []
           buttons.append(tk.Button(frame, text="Редактировать", command=lambda row=row: self.edit_row(row)))
           buttons.append(tk.Button(frame, text="Удалить", command=lambda row=row: self.delete_row(row)))

           frame.add_row(*buttons, row)

   # Выбор строки
    def select_row(self, row):
       print("Выбрана строка:", row)

   # Редактирование строки
    def edit_row(self, row):
       print("Редактируется строка:", row)

   # Удаление строки
    def delete_row(self, row):
       with open("notes.txt", "w", encoding='utf-8') as file:
           rows = file.read().splitlines()
           file.seek(0)
           for i in range(row):
               file.write(rows[i])

    # Очистка полей ввода
    def clear_entries(self):
        self.entry_manufacturer.delete(0, 'end')
        self.entry_model.delete(0, 'end')
        self.entry_mass.delete(0, 'end')
        self.entry_payload.delete(0, 'end')
        self.entry_flight_distance.delete(0, 'end')
        self.entry_speed.delete(0, 'end')
        self.entry_battery_life.delete(0, 'end')

    # Отображение сообщения в GUI
    def display_message(self, message):
        win = tk.Toplevel(self.master)
        label_message = tk.Label(win, text=message)
        label_message.pack()
        win.mainloop()

# Запуск приложения
if __name__ == '__main__':
    root = tk.Tk()
    app = DroneCatalog(root)
    root.mainloop()