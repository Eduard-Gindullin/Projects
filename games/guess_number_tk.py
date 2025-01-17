import tkinter as tk
import random

def start_game():
    secret_number = random.randint(1, 100)
    num_guesses = 0
    guess_entry.delete(0, tk.END)
    status_label.config(text="")
    guess_buton["state"] = "normal"
    start_button["state"] = "disabled"

    check_guess(secret_number, num_guesses)

def check_guess(secret_number, num_guesses):

    def on_guess():
        guess = int(guess_entry.get())
        nonlocal num_guesses
        num_guesses += 1

        if guess < secret_number:
            status_label.config(text="Введи больше")
        elif guess > secret_number:
            status_label.config(text="Введи меньше")
        else:
            status_label.config(text=f"Вы угадали за {num_guesses} попыток")
            guess_buton["state"] = "disabled"
            start_button["state"] = "normal"

    guess_buton.config(command=on_guess)

window = tk.Tk()
window.geometry("250x200")
window.title("Guess the number")
window.resizable(False, False)

guess_label = tk.Label(window, text="Угадай число от 1 до 100")
guess_label.pack()

guess_entry = tk.Entry(window, width=5)
guess_entry.pack()

guess_buton = tk.Button(window, text="Угадать", state="disabled")
guess_buton.pack()

start_button = tk.Button(window, text="Начать игру", command=start_game)
start_button.pack()

status_label = tk.Label(window, text="")
status_label.pack()

window.mainloop()
