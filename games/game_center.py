import tkinter as tk
from tkinter import ttk, messagebox
import random

class GameCenter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Игровой Центр")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Создаем стиль
        style = ttk.Style()
        style.configure("Game.TButton", padding=10, font=('Helvetica', 12))
        style.configure("Title.TLabel", font=('Helvetica', 16, 'bold'))
        
        # Заголовок
        self.title = ttk.Label(self.window, text="Добро пожаловать в Игровой Центр!", 
                             style="Title.TLabel")
        self.title.pack(pady=20)
        
        # Фрейм для кнопок
        self.button_frame = ttk.Frame(self.window)
        self.button_frame.pack(pady=20)
        
        # Кнопки игр
        ttk.Button(self.button_frame, text="Угадай число", 
                  command=self.start_guess_number, style="Game.TButton").pack(pady=10)
        ttk.Button(self.button_frame, text="Кости", 
                  command=self.start_dice_game, style="Game.TButton").pack(pady=10)
        ttk.Button(self.button_frame, text="Камень, ножницы, бумага", 
                  command=self.start_rock_paper_scissors, style="Game.TButton").pack(pady=10)
        ttk.Button(self.button_frame, text="Убегающая кнопка", 
                  command=self.start_running_button, style="Game.TButton").pack(pady=10)
        
        # Статистика
        self.stats_frame = ttk.LabelFrame(self.window, text="Статистика", padding=10)
        self.stats_frame.pack(pady=20, fill="x", padx=20)
        self.stats_label = ttk.Label(self.stats_frame, 
                                   text="Сыграно игр: 0\nПобед: 0\nПоражений: 0")
        self.stats_label.pack()
        
        # Счетчики статистики
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0

    def update_stats(self, won=False):
        self.games_played += 1
        if won:
            self.games_won += 1
        else:
            self.games_lost += 1
        self.stats_label.config(
            text=f"Сыграно игр: {self.games_played}\n"
                 f"Побед: {self.games_won}\n"
                 f"Поражений: {self.games_lost}")

    def start_guess_number(self):
        game_window = tk.Toplevel(self.window)
        game_window.title("Угадай число")
        game_window.geometry("300x400")
        GuessNumber(game_window, self)

    def start_dice_game(self):
        game_window = tk.Toplevel(self.window)
        game_window.title("Кости")
        game_window.geometry("300x400")
        DiceGame(game_window, self)

    def start_rock_paper_scissors(self):
        game_window = tk.Toplevel(self.window)
        game_window.title("Камень, ножницы, бумага")
        game_window.geometry("300x400")
        RockPaperScissors(game_window, self)

    def start_running_button(self):
        game_window = tk.Toplevel(self.window)
        game_window.title("Убегающая кнопка")
        game_window.geometry("550x550")
        RunningButton(game_window, self)

    def run(self):
        self.window.mainloop()

class GuessNumber:
    def __init__(self, window, game_center):
        self.window = window
        self.game_center = game_center
        self.secret_number = None
        self.num_guesses = 0
        
        ttk.Label(window, text="Угадай число от 1 до 100", 
                 style="Title.TLabel").pack(pady=20)
        
        self.guess_entry = ttk.Entry(window, width=5)
        self.guess_entry.pack(pady=10)
        
        self.guess_button = ttk.Button(window, text="Угадать", 
                                     command=self.check_guess, state="disabled")
        self.guess_button.pack(pady=10)
        
        self.start_button = ttk.Button(window, text="Начать игру", 
                                     command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.status_label = ttk.Label(window, text="")
        self.status_label.pack(pady=20)

    def start_game(self):
        self.secret_number = random.randint(1, 100)
        self.num_guesses = 0
        self.guess_entry.delete(0, tk.END)
        self.status_label.config(text="")
        self.guess_button["state"] = "normal"
        self.start_button["state"] = "disabled"

    def check_guess(self):
        try:
            guess = int(self.guess_entry.get())
            self.num_guesses += 1
            
            if guess < self.secret_number:
                self.status_label.config(text="Введи больше")
            elif guess > self.secret_number:
                self.status_label.config(text="Введи меньше")
            else:
                self.status_label.config(
                    text=f"Вы угадали за {self.num_guesses} попыток!")
                self.guess_button["state"] = "disabled"
                self.start_button["state"] = "normal"
                self.game_center.update_stats(won=True)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число!")

class DiceGame:
    def __init__(self, window, game_center):
        self.window = window
        self.game_center = game_center
        self.rounds = 0
        self.current_round = 0
        self.player_score = 0
        self.computer_score = 0
        
        ttk.Label(window, text="Игра в кости", 
                 style="Title.TLabel").pack(pady=20)
        
        self.rounds_frame = ttk.Frame(window)
        self.rounds_frame.pack(pady=10)
        ttk.Label(self.rounds_frame, text="Количество раундов:").pack(side=tk.LEFT)
        self.rounds_entry = ttk.Entry(self.rounds_frame, width=5)
        self.rounds_entry.pack(side=tk.LEFT, padx=5)
        
        self.roll_button = ttk.Button(window, text="Бросить кости", 
                                    command=self.roll_dice, state="disabled")
        self.roll_button.pack(pady=10)
        
        self.start_button = ttk.Button(window, text="Начать игру", 
                                     command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.status_label = ttk.Label(window, text="")
        self.status_label.pack(pady=20)
        
        self.score_label = ttk.Label(window, text="")
        self.score_label.pack(pady=10)

    def start_game(self):
        try:
            self.rounds = int(self.rounds_entry.get())
            if self.rounds <= 0:
                raise ValueError
            self.current_round = 0
            self.player_score = 0
            self.computer_score = 0
            self.roll_button["state"] = "normal"
            self.start_button["state"] = "disabled"
            self.rounds_entry["state"] = "disabled"
            self.update_status()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное целое число раундов!")

    def roll_dice(self):
        self.current_round += 1
        player_roll = random.randint(1, 6)
        computer_roll = random.randint(1, 6)
        
        if player_roll > computer_roll:
            self.player_score += 1
            result = "Вы выиграли раунд!"
        elif computer_roll > player_roll:
            self.computer_score += 1
            result = "Компьютер выиграл раунд!"
        else:
            result = "Ничья в раунде!"
        
        self.status_label.config(
            text=f"Ваш бросок: {player_roll}\n"
                 f"Бросок компьютера: {computer_roll}\n"
                 f"{result}")
        
        self.update_status()
        
        if self.current_round >= self.rounds:
            self.end_game()

    def update_status(self):
        self.score_label.config(
            text=f"Раунд: {self.current_round}/{self.rounds}\n"
                 f"Счёт: Вы {self.player_score} - {self.computer_score} Компьютер")

    def end_game(self):
        self.roll_button["state"] = "disabled"
        self.start_button["state"] = "normal"
        self.rounds_entry["state"] = "normal"
        
        if self.player_score > self.computer_score:
            result = "Поздравляем! Вы выиграли игру!"
            self.game_center.update_stats(won=True)
        elif self.computer_score > self.player_score:
            result = "Вы проиграли игру."
            self.game_center.update_stats(won=False)
        else:
            result = "Игра закончилась вничью!"
            self.game_center.update_stats(won=False)
        
        self.status_label.config(text=f"{result}")

class RockPaperScissors:
    def __init__(self, window, game_center):
        self.window = window
        self.game_center = game_center
        self.rounds = 0
        self.current_round = 0
        self.player_score = 0
        self.computer_score = 0
        self.choices = ["камень", "ножницы", "бумага"]
        
        ttk.Label(window, text="Камень, ножницы, бумага", 
                 style="Title.TLabel").pack(pady=20)
        
        self.rounds_frame = ttk.Frame(window)
        self.rounds_frame.pack(pady=10)
        ttk.Label(self.rounds_frame, text="Количество раундов:").pack(side=tk.LEFT)
        self.rounds_entry = ttk.Entry(self.rounds_frame, width=5)
        self.rounds_entry.pack(side=tk.LEFT, padx=5)
        
        self.choice_frame = ttk.Frame(window)
        self.choice_frame.pack(pady=20)
        
        for choice in self.choices:
            ttk.Button(self.choice_frame, text=choice.capitalize(),
                      command=lambda x=choice: self.make_choice(x),
                      state="disabled").pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(window, text="Начать игру", 
                                     command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.status_label = ttk.Label(window, text="")
        self.status_label.pack(pady=20)
        
        self.score_label = ttk.Label(window, text="")
        self.score_label.pack(pady=10)

    def start_game(self):
        try:
            self.rounds = int(self.rounds_entry.get())
            if self.rounds <= 0:
                raise ValueError
            self.current_round = 0
            self.player_score = 0
            self.computer_score = 0
            for button in self.choice_frame.winfo_children():
                button["state"] = "normal"
            self.start_button["state"] = "disabled"
            self.rounds_entry["state"] = "disabled"
            self.update_status()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное целое число раундов!")

    def make_choice(self, player_choice):
        self.current_round += 1
        computer_choice = random.choice(self.choices)
        
        result = self.determine_winner(player_choice, computer_choice)
        
        self.status_label.config(
            text=f"Ваш выбор: {player_choice}\n"
                 f"Выбор компьютера: {computer_choice}\n"
                 f"{result}")
        
        self.update_status()
        
        if self.current_round >= self.rounds:
            self.end_game()

    def determine_winner(self, player_choice, computer_choice):
        if player_choice == computer_choice:
            return "Ничья!"
        
        winning_combinations = {
            "камень": "ножницы",
            "ножницы": "бумага",
            "бумага": "камень"
        }
        
        if winning_combinations[player_choice] == computer_choice:
            self.player_score += 1
            return "Вы выиграли раунд!"
        else:
            self.computer_score += 1
            return "Компьютер выиграл раунд!"

    def update_status(self):
        self.score_label.config(
            text=f"Раунд: {self.current_round}/{self.rounds}\n"
                 f"Счёт: Вы {self.player_score} - {self.computer_score} Компьютер")

    def end_game(self):
        for button in self.choice_frame.winfo_children():
            button["state"] = "disabled"
        self.start_button["state"] = "normal"
        self.rounds_entry["state"] = "normal"
        
        if self.player_score > self.computer_score:
            result = "Поздравляем! Вы выиграли игру!"
            self.game_center.update_stats(won=True)
        elif self.computer_score > self.player_score:
            result = "Вы проиграли игру."
            self.game_center.update_stats(won=False)
        else:
            result = "Игра закончилась вничью!"
            self.game_center.update_stats(won=False)
        
        self.status_label.config(text=f"{result}")

class RunningButton:
    def __init__(self, window, game_center):
        self.window = window
        self.game_center = game_center
        
        ttk.Label(window, text="Поймай кнопку", 
                 style="Title.TLabel").pack(pady=20)
        
        ttk.Label(window, text="Вы согласны с утверждением?").pack(pady=20)
        
        ttk.Button(window, text="ДА", 
                  command=self.yes_clicked).place(x=180, y=250, width=50, height=20)
        
        self.no_button = ttk.Button(window, text="НЕТ")
        self.no_button.place(x=280, y=250, width=50, height=20)
        self.no_button.bind("<Enter>", self.no_hover)

    def yes_clicked(self):
        messagebox.showinfo("Отлично!", "Мы так и думали!")
        self.game_center.update_stats(won=True)
        self.window.destroy()

    def no_hover(self, event):
        new_x = random.randrange(50, 450)
        new_y = random.randrange(50, 450)
        self.no_button.place(x=new_x, y=new_y)

if __name__ == "__main__":
    game_center = GameCenter()
    game_center.run() 