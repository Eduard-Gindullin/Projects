# Бросок кости
import random

def roll_dice():
    return random.randint(1, 6)

def play_round():
    input("Нажмите Enter, чтобы бросить кости")
    player_roll = roll_dice()
    computer_roll = roll_dice()

    print(f"Ваш результат {player_roll}")
    print(f"результат компьютера {computer_roll}")
    return player_roll, computer_roll

def winner(player_roll, computer_roll):
    if player_roll > computer_roll:
        return "player"
    elif player_roll < computer_roll:
        return "computer"
    else: 
        return "tie"
    
def main():
    player_score = 0
    computer_score = 0

    print ("Приветствуем игрока, добро пожаловать в игру кости \n")
    rounds = int(input("Введите количество раундов \n"))

    for round in range(rounds):
        player_roll, computer_roll = play_round()
        game_winner = winner(player_roll, computer_roll)

        if game_winner == "player":
            print("Вы победили в этом раунде \n")
            player_score += 1
        elif game_winner == "computer":
            print("Компьютер победил в раунде \n")
            computer_score += 1
        else:
            print("Ничья")
    print(f"Итоги: Вы {player_score}, Комп {computer_score}")
    if player_score > computer_score:
        print ("Вы победили")
    elif computer_score > player_score:
        print ("Вы проиграли")
    else:
        print("Ничья")

main()


