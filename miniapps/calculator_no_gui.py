# Калькулятор
import math

def add(x,y):
    return x + y

def subtract(x,y):
    return x - y

def multiply(x,y):
    return x * y

def divide(x,y):
    if y == 0:
        return float("inf")
    return x / y
    
def calculator():
    print("Выберите операцию")
    print ("1. сложение")
    print ("2. вычитание")
    print ("3. умножение")
    print ("4. деление")
    choice = input("Введите номер операции(1/2/3/4) \n")
    if choice in ["1", "2", "3", "4"]:
        x = float(input("Введите первое число: "))
        y = float(input("Введите второе число: "))

        if choice == "1":
            print(f"Результат {add(x,y)}")
        elif choice == "2":
            print(f"Результат {subtract(x,y)}")
        elif choice == "3":
            print(f"Результат {multiply(x,y)}") 
        elif choice == "4":
            print(f"Результат {divide(x,y)}")
        else:
            print("Нет такой операции")

calculator()
