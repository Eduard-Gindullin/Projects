# Камень, ножницы, бумага
import random

print("Сыграем в камень, ножницы, бумага")
user_choice = ""
comp_choice = ""
user_score = 0
comp_score = 0
variants = ["камень", "ножницы", "бумага"]
rounds = int(input("Введите количество раунов: \n"))
for round in range(rounds):
    print(f"Раунд №" +str(round+1))
    while True:
        user_choice = input("Введите камень, ножницы или бумага: \n").lower()
        if user_choice == "камень" or user_choice == "ножницы" or user_choice == "бумага":
            break
        else:
            print("Некорректный ввод")
    comp_choice =random.choice(variants)
    if user_choice == comp_choice:
        print("Ничья")
        print(f"Ваш выбор {user_choice}, Выбор комьютера {comp_choice}")
    elif user_choice == "камень" and comp_choice == "ножницы":
        print("Ты виграля")
        print(f"Ваш выбор {user_choice}, Выбор комьютера {comp_choice}") 
        user_score +=1
    elif user_choice == "камень" and comp_choice == "бумага":
        print("Ты проиграл")
        print(f"Ваш выбор {user_choice}, Выбор комьютера {comp_choice}") 
        comp_score +=1   
    elif user_choice == "бумага" and comp_choice == "камень":
        print("Ты выиграл")
        print(f"Ваш выбор {user_choice}, Выбор комьютера {comp_choice}") 
        user_score +=1 
    elif user_choice == "бумага" and comp_choice == "ножницы":
        print("Ты проиграл")
        print(f"Ваш выбор {user_choice}, Выбор комьютера {comp_choice}") 
        comp_score +=1   
    elif user_choice == "ножницы" and comp_choice == "бумага":
        print("Ты выиграл")
        print(f"Ваш выбор {user_choice}, Выбор комьютера {comp_choice}") 
        user_score +=1 
    elif user_choice == "ножницы" and comp_choice == "камень":
        print("Ты проиграл")
        print(f"Ваш выбор {user_choice}, Выбор комьютера {comp_choice}") 
        comp_score +=1   

if user_score > comp_score:
    print("Ты выиграл")
elif user_score < comp_score:
    print("Ты проиграл")
else: 
    print("Ничья")
