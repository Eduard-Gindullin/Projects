# Генератор паролей

import random

def generate_symbols():
    s1 = "1234567890"
    s2 = "qwertyuiopasdfghjklzxcvbnm"
    s3 = "!@#$%^&*()[]{:'\<>?"
    return s1 + s2 + s3 +s2.upper()

def get_password_length():
    while True:
        try:
            length = int(input("Введите желаемую длинну пароля \n"))
            if length <=0:
                print("Введите положительное число")
            else:
                return length
        except:
            print("Введите число")   

def generate_password(symbols, length):
    password = ""
    for i in range(length):
        password =+ random.choice(symbols)
    return password

def main():
    symbols = generate_symbols()
    password_lengh = get_password_length()
    password = generate_password(symbols, password_lengh)
    print(f"Ваш пароль {password}")

main()