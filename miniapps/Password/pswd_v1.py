import tkinter as tk
from tkinter import messagebox, filedialog
import random
import string
import json
import os

# Политика паролей
password_policy = {
    "min_length": 12,
    "complexity": True
}

# Путь к файлу со словарем по умолчанию
DEFAULT_DICT_PATH = "default_words.json"

class PasswordGenerator:
    def __init__(self):
        self.words = self.load_default_dictionary()
        
    def load_default_dictionary(self):
        """Загрузка словаря по умолчанию"""
        if os.path.exists(DEFAULT_DICT_PATH):
            try:
                with open(DEFAULT_DICT_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.get_basic_words()
        else:
            # Сохраняем базовый словарь как словарь по умолчанию
            words = self.get_basic_words()
            self.save_dictionary(words, DEFAULT_DICT_PATH)
            return words

    def get_basic_words(self):
        """Возвращает базовый набор слов"""
        return ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew",
                "secure", "password", "strong", "protect", "encrypt", "safe", "guard", "shield"]

    def save_dictionary(self, words, filepath):
        """Сохранение словаря в файл"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(words, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save dictionary: {str(e)}")
            return False

    def load_dictionary(self, filepath):
        """Загрузка словаря из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dictionary: {str(e)}")
            return False

    def transform_password(self, password):
        """Трансформация пароля с заменой символов"""
        replacements = {
            'a': '@', 'A': '@', 'i': '!', 'I': '1', 'o': '0', 'O': '0', 
            's': '$', 'S': '$', 'e': '3', 'E': '3', 't': '7', 'T': '7'
        }
        transformed = ''.join(replacements.get(c, random.choice([c.lower(), c.upper()])) 
                            if c.isalpha() else c for c in password)
        return transformed

    def generate_password(self, bits=40):
        """Генерация пароля заданной битности"""
        num_words = {40: 2, 128: 4, 256: 8}.get(bits, 2)
        password = '_'.join(random.choice(self.words) for _ in range(num_words))
        return self.transform_password(password)

    def generate_policy_password(self):
        """Генерация пароля по политике безопасности"""
        password = ''
        while len(password) < password_policy["min_length"]:
            word = random.choice(self.words)
            if len(password) + len(word) <= password_policy["min_length"]:
                password += word
            else:
                break
        
        if len(password) < password_policy["min_length"]:
            password += ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) 
                              for _ in range(password_policy["min_length"] - len(password)))
        
        return self.transform_password(password)

class PasswordGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator Pro")
        self.root.geometry("900x400")
        
        self.generator = PasswordGenerator()
        self.setup_gui()

    def setup_gui(self):
        """Настройка графического интерфейса"""
        # Фрейм для словаря
        dict_frame = tk.Frame(self.root)
        dict_frame.pack(pady=5, padx=10, fill=tk.X)

        tk.Label(dict_frame, text="Current Dictionary:").pack(side=tk.LEFT, padx=5)
        self.dict_label = tk.Label(dict_frame, text=f"Words: {len(self.generator.words)}")
        self.dict_label.pack(side=tk.LEFT, padx=5)

        # Кнопки управления словарем
        tk.Button(dict_frame, text="Load Dictionary", command=self.load_dictionary).pack(side=tk.LEFT, padx=5)
        tk.Button(dict_frame, text="Save Dictionary", command=self.save_dictionary).pack(side=tk.LEFT, padx=5)

        # Поле для ввода пароля
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5, padx=10, fill=tk.X)

        tk.Label(input_frame, text="Enter/Generated Password:").pack(side=tk.LEFT, padx=5)
        self.password_entry = tk.Entry(input_frame, width=50)
        self.password_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Кнопка копирования
        tk.Button(input_frame, text="Copy", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)

        # Кнопки генерации
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=5)

        tk.Button(buttons_frame, text="Transform Password", 
                 command=self.transform_password).pack(pady=5)
        
        for bits in [40, 128, 256]:
            tk.Button(buttons_frame, text=f"Generate {bits}-bit Password",
                     command=lambda b=bits: self.generate_password(b)).pack(pady=5)

        tk.Button(buttons_frame, text="Generate Policy Password",
                 command=self.generate_policy_password).pack(pady=5)

        # Метка результата
        self.result_label = tk.Label(self.root, text="", wraplength=800)
        self.result_label.pack(pady=5)

    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_entry.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.result_label.config(text="Password copied to clipboard!")
        else:
            self.result_label.config(text="No password to copy!")

    def load_dictionary(self):
        """Загрузка словаря из файла"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            if self.generator.load_dictionary(filepath):
                self.dict_label.config(text=f"Words: {len(self.generator.words)}")
                self.result_label.config(text=f"Dictionary loaded successfully: {len(self.generator.words)} words")

    def save_dictionary(self):
        """Сохранение текущего словаря в файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            if self.generator.save_dictionary(self.generator.words, filepath):
                self.result_label.config(text=f"Dictionary saved successfully to {filepath}")

    def transform_password(self):
        """Трансформация введенного пароля"""
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Warning", "Please enter a password")
            return
        transformed = self.generator.transform_password(password)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, transformed)
        self.result_label.config(text=f"Transformed Password: {transformed}")

    def generate_password(self, bits):
        """Генерация пароля заданной битности"""
        password = self.generator.generate_password(bits)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self.result_label.config(text=f"Generated {bits}-bit Password: {password}")

    def generate_policy_password(self):
        """Генерация пароля по политике безопасности"""
        password = self.generator.generate_policy_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self.result_label.config(text=f"Generated Policy Password: {password}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorGUI(root)
    root.mainloop() 