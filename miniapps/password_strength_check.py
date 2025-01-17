# Проверка надежности пароля

import random
import string

def check_password_strenght(password):
    errors = []

    if len(password) < 8:
        errors.append("Пароль должен содержать не менее 8 символов")

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False 
    special_characters = "!@#$%^&*()_+{[]}:"

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_characters:
            has_special = True

    if not has_upper:
        errors.append("Пароль должен содержать хотя бы одну заглавную букву")
    if not has_lower:
         errors.append("Пароль должен содержать хотя бы одну строчную букву")
    if not has_digit:
        errors.append("Пароль должен содержать хотя бы одну цифру")
    if not has_special:
        errors.append("Пароль должен содержать хотя бы один спец символ")   

    return errors

def display_errors(errors):
    print ("Пароль не безопасен. Ошибки")
    for error in errors:
        print(f" - {error}")

def generate_random_password(lenght):
    if lenght < 8:
        return "Длинна пароля меньше 8 символов"
    special_characters = "!@#$%^&*()_+{[]}:"
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(special_characters),
    ]
    all_characters = string.ascii_letters + string.digits + special_characters
    for i in range(lenght-4):
        password.append(random.choice(all_characters))
    
    random.shuffle(password)
    return "".join(password)

def main():
    password = input ("Введите пароль")
    errors = check_password_strenght(password)
    if not errors:
        print("Пароль безопасен")
    else:
        display_errors(errors)
        random_password = generate_random_password(8)
        print(f"Сгерерированнный безопасный пароль: {random_password}")

main()