import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import json
import os

DATA_FILE = 'products_data.json'

# --- Работа с JSON ---
def load_data_from_file(filename=DATA_FILE):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('products', []), data.get('categories', []), data.get('product_category', [])
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось загрузить данные: {e}')
    # Дефолтные данные
    return (
        [ [1, 'Молоко'], [2, 'Хлеб'], [3, 'Сыр'], [4, 'Яблоко'], [5, 'Кефир'] ],
        [ [1, 'Молочные'], [2, 'Фрукты'], [3, 'Выпечка'] ],
        [ [1, 1], [3, 1], [2, 3], [4, 2] ]
    )

def save_data_to_file(products, categories, product_category, filename=DATA_FILE):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'products': products,
                'categories': categories,
                'product_category': product_category
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror('Ошибка', f'Не удалось сохранить данные: {e}')

# Функция анализа данных (та же логика, что в main.py)
def analyze():
    spark = SparkSession.builder.appName('ProductsCategoriesGUI').getOrCreate()
    products_data = [
        (1, 'Молоко'),
        (2, 'Хлеб'),
        (3, 'Сыр'),
        (4, 'Яблоко'),
        (5, 'Кефир'),
    ]
    categories_data = [
        (1, 'Молочные'),
        (2, 'Фрукты'),
        (3, 'Выпечка'),
    ]
    product_category_data = [
        (1, 1),
        (3, 1),
        (2, 3),
        (4, 2),
    ]
    products = spark.createDataFrame(products_data, ['product_id', 'product_name'])
    categories = spark.createDataFrame(categories_data, ['category_id', 'category_name'])
    product_category = spark.createDataFrame(product_category_data, ['product_id', 'category_id'])

    joined = products.join(product_category, on='product_id', how='left') \
                   .join(categories, on='category_id', how='left')
    pairs = joined.filter(col('category_name').isNotNull()) \
                 .select('product_name', 'category_name')
    orphans = joined.filter(col('category_name').isNull()) \
                   .select('product_name').distinct()

    pairs_list = pairs.collect()
    orphans_list = orphans.collect()
    spark.stop()
    return pairs_list, orphans_list

# GUI приложение на tkinter
class PySparkGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PySpark: Продукты и Категории')
        self.geometry('750x620')
        self.resizable(False, False)

        # Данные из файла или дефолтные
        self.products, self.categories, self.product_category = load_data_from_file()

        # Вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.products_frame = ttk.Frame(self.notebook)
        self.categories_frame = ttk.Frame(self.notebook)
        self.links_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.products_frame, text='Продукты')
        self.notebook.add(self.categories_frame, text='Категории')
        self.notebook.add(self.links_frame, text='Связи')
        self.notebook.add(self.analysis_frame, text='Анализ')

        self.create_products_tab()
        self.create_categories_tab()
        self.create_links_tab()
        self.create_analysis_tab()

        # Кнопки сохранения, импорта и экспорта
        btns = ttk.Frame(self)
        btns.pack(pady=5)
        ttk.Button(btns, text='Сохранить данные', command=self.save_all).pack(side='left', padx=5)
        ttk.Button(btns, text='Импорт', command=self.import_data).pack(side='left', padx=5)
        ttk.Button(btns, text='Экспорт', command=self.export_data).pack(side='left', padx=5)

    # --- Импорт/Экспорт ---
    def import_data(self):
        filename = filedialog.askopenfilename(
            title='Импортировать данные из JSON',
            filetypes=[('JSON файлы', '*.json'), ('Все файлы', '*.*')]
        )
        if filename:
            products, categories, product_category = load_data_from_file(filename)
            if products and categories:
                self.products, self.categories, self.product_category = products, categories, product_category
                self.update_products_tree()
                self.update_categories_tree()
                self.update_links_tree()
                messagebox.showinfo('Импорт', 'Данные успешно импортированы!')
            else:
                messagebox.showwarning('Импорт', 'Файл не содержит корректных данных.')

    def export_data(self):
        filename = filedialog.asksaveasfilename(
            title='Экспортировать данные в JSON',
            defaultextension='.json',
            filetypes=[('JSON файлы', '*.json'), ('Все файлы', '*.*')]
        )
        if filename:
            save_data_to_file(self.products, self.categories, self.product_category, filename)
            messagebox.showinfo('Экспорт', 'Данные успешно экспортированы!')

    # --- Продукты ---
    def create_products_tab(self):
        frame = self.products_frame
        self.products_tree = ttk.Treeview(frame, columns=('id', 'name'), show='headings', height=10)
        self.products_tree.heading('id', text='ID')
        self.products_tree.heading('name', text='Имя продукта')
        self.products_tree.pack(pady=10)
        self.update_products_tree()

        btns = ttk.Frame(frame)
        btns.pack()
        ttk.Button(btns, text='Добавить', command=self.add_product).pack(side='left', padx=5)
        ttk.Button(btns, text='Редактировать', command=self.edit_product).pack(side='left', padx=5)
        ttk.Button(btns, text='Удалить', command=self.delete_product).pack(side='left', padx=5)

    def update_products_tree(self):
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        for row in self.products:
            self.products_tree.insert('', 'end', values=row)

    def add_product(self):
        name = simpledialog.askstring('Добавить продукт', 'Имя продукта:')
        if name:
            new_id = max([p[0] for p in self.products], default=0) + 1
            self.products.append([new_id, name])
            self.update_products_tree()
            self.save_all()

    def edit_product(self):
        sel = self.products_tree.selection()
        if not sel:
            messagebox.showinfo('Внимание', 'Выберите продукт для редактирования')
            return
        item = self.products_tree.item(sel[0])
        pid, old_name = item['values']
        new_name = simpledialog.askstring('Редактировать продукт', 'Новое имя продукта:', initialvalue=old_name)
        if new_name:
            for p in self.products:
                if p[0] == pid:
                    p[1] = new_name
            self.update_products_tree()
            self.save_all()

    def delete_product(self):
        sel = self.products_tree.selection()
        if not sel:
            messagebox.showinfo('Внимание', 'Выберите продукт для удаления')
            return
        item = self.products_tree.item(sel[0])
        pid = item['values'][0]
        self.products = [p for p in self.products if p[0] != pid]
        self.product_category = [pc for pc in self.product_category if pc[0] != pid]
        self.update_products_tree()
        self.update_links_tree()
        self.save_all()

    # --- Категории ---
    def create_categories_tab(self):
        frame = self.categories_frame
        self.categories_tree = ttk.Treeview(frame, columns=('id', 'name'), show='headings', height=10)
        self.categories_tree.heading('id', text='ID')
        self.categories_tree.heading('name', text='Имя категории')
        self.categories_tree.pack(pady=10)
        self.update_categories_tree()

        btns = ttk.Frame(frame)
        btns.pack()
        ttk.Button(btns, text='Добавить', command=self.add_category).pack(side='left', padx=5)
        ttk.Button(btns, text='Редактировать', command=self.edit_category).pack(side='left', padx=5)
        ttk.Button(btns, text='Удалить', command=self.delete_category).pack(side='left', padx=5)

    def update_categories_tree(self):
        for i in self.categories_tree.get_children():
            self.categories_tree.delete(i)
        for row in self.categories:
            self.categories_tree.insert('', 'end', values=row)

    def add_category(self):
        name = simpledialog.askstring('Добавить категорию', 'Имя категории:')
        if name:
            new_id = max([c[0] for c in self.categories], default=0) + 1
            self.categories.append([new_id, name])
            self.update_categories_tree()
            self.save_all()

    def edit_category(self):
        sel = self.categories_tree.selection()
        if not sel:
            messagebox.showinfo('Внимание', 'Выберите категорию для редактирования')
            return
        item = self.categories_tree.item(sel[0])
        cid, old_name = item['values']
        new_name = simpledialog.askstring('Редактировать категорию', 'Новое имя категории:', initialvalue=old_name)
        if new_name:
            for c in self.categories:
                if c[0] == cid:
                    c[1] = new_name
            self.update_categories_tree()
            self.save_all()

    def delete_category(self):
        sel = self.categories_tree.selection()
        if not sel:
            messagebox.showinfo('Внимание', 'Выберите категорию для удаления')
            return
        item = self.categories_tree.item(sel[0])
        cid = item['values'][0]
        self.categories = [c for c in self.categories if c[0] != cid]
        self.product_category = [pc for pc in self.product_category if pc[1] != cid]
        self.update_categories_tree()
        self.update_links_tree()
        self.save_all()

    # --- Связи ---
    def create_links_tab(self):
        frame = self.links_frame
        self.links_tree = ttk.Treeview(frame, columns=('product_id', 'category_id'), show='headings', height=10)
        self.links_tree.heading('product_id', text='ID продукта')
        self.links_tree.heading('category_id', text='ID категории')
        self.links_tree.pack(pady=10)
        self.update_links_tree()

        btns = ttk.Frame(frame)
        btns.pack()
        ttk.Button(btns, text='Добавить', command=self.add_link).pack(side='left', padx=5)
        ttk.Button(btns, text='Удалить', command=self.delete_link).pack(side='left', padx=5)

    def update_links_tree(self):
        for i in self.links_tree.get_children():
            self.links_tree.delete(i)
        for row in self.product_category:
            self.links_tree.insert('', 'end', values=row)

    def add_link(self):
        if not self.products or not self.categories:
            messagebox.showinfo('Внимание', 'Добавьте хотя бы один продукт и категорию')
            return
        pid = simpledialog.askinteger('ID продукта', 'Введите ID продукта:')
        cid = simpledialog.askinteger('ID категории', 'Введите ID категории:')
        if pid and cid:
            if not any(p[0] == pid for p in self.products):
                messagebox.showerror('Ошибка', f'Нет продукта с ID {pid}')
                return
            if not any(c[0] == cid for c in self.categories):
                messagebox.showerror('Ошибка', f'Нет категории с ID {cid}')
                return
            if [pid, cid] not in self.product_category:
                self.product_category.append([pid, cid])
                self.update_links_tree()
                self.save_all()

    def delete_link(self):
        sel = self.links_tree.selection()
        if not sel:
            messagebox.showinfo('Внимание', 'Выберите связь для удаления')
            return
        item = self.links_tree.item(sel[0])
        pid, cid = item['values']
        self.product_category = [pc for pc in self.product_category if not (pc[0] == pid and pc[1] == cid)]
        self.update_links_tree()
        self.save_all()

    # --- Анализ ---
    def create_analysis_tab(self):
        frame = self.analysis_frame
        self.run_btn = ttk.Button(frame, text='Запустить анализ', command=self.run_analysis)
        self.run_btn.pack(pady=10)
        self.text = scrolledtext.ScrolledText(frame, width=70, height=25, font=('Consolas', 10))
        self.text.pack(padx=10, pady=10)

    def run_analysis(self):
        self.text.delete('1.0', tk.END)
        try:
            pairs, orphans = self.analyze_with_current_data()
            self.text.insert(tk.END, 'Пары "Имя продукта – Имя категории":\n')
            if pairs:
                for row in pairs:
                    self.text.insert(tk.END, f'{row[0]} — {row[1]}\n')
            else:
                self.text.insert(tk.END, 'Нет пар.\n')
            self.text.insert(tk.END, '\nПродукты без категорий:\n')
            if orphans:
                for name in orphans:
                    self.text.insert(tk.END, f'{name}\n')
            else:
                self.text.insert(tk.END, 'Нет таких продуктов.\n')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def analyze_with_current_data(self):
        spark = SparkSession.builder.appName('ProductsCategoriesGUI').getOrCreate()
        products = spark.createDataFrame(self.products, ['product_id', 'product_name'])
        categories = spark.createDataFrame(self.categories, ['category_id', 'category_name'])
        product_category = spark.createDataFrame(self.product_category, ['product_id', 'category_id'])
        joined = products.join(product_category, on='product_id', how='left') \
                   .join(categories, on='category_id', how='left')
        pairs = joined.filter(col('category_name').isNotNull()) \
                 .select('product_name', 'category_name')
        orphans = joined.filter(col('category_name').isNull()) \
                   .select('product_name').distinct()
        pairs_list = [(r.product_name, r.category_name) for r in pairs.collect()]
        orphans_list = [r.product_name for r in orphans.collect()]
        spark.stop()
        return pairs_list, orphans_list

    def save_all(self):
        save_data_to_file(self.products, self.categories, self.product_category)

if __name__ == '__main__':
    app = PySparkGUI()
    app.mainloop() 