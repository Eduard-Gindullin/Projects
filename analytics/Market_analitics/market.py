import pandas as pd
import numpy as np

# --- Шаг 1: Загрузка и первичная обработка данных ---

# Используем raw string для пути
file_path = r'c:\projects\Projects\analytics\Market_analitics\_Тестовое задание 1 (выгрузка).csv'

# Загружаем файл
df = pd.read_csv(file_path, sep=';', encoding='cp1251', skiprows=1, header=None)
print(f"Загружено {df.shape[0]} строк, {df.shape[1]} столбцов")

# Смотрим на структуру
print("\nПервые 2 строки:")
for i in range(min(2, len(df))):
    print(f"Строка {i}: {df.iloc[i, :5].tolist()} | {df.iloc[i, 5:].tolist()}")

# Разделяем первые 5 столбцов (они уже должны быть разделены табуляцией)
# Но в данных они могут быть склеены, поэтому обработаем каждый столбец отдельно

# Создадим новый DataFrame для результатов
result_rows = []

for idx, row in df.iterrows():
    # Первые 5 столбцов должны содержать основные данные
    main_data = []
    for i in range(5):
        val = row[i]
        if pd.notna(val):
            # Разделяем по табуляции, если есть
            if isinstance(val, str) and '\t' in val:
                parts = val.split('\t')
                main_data.extend(parts)
            else:
                main_data.append(val)
        else:
            main_data.append(np.nan)
    
    # Оставшиеся столбцы содержат числовые данные
    numeric_data = []
    for i in range(5, len(row)):
        val = row[i]
        if pd.notna(val):
            if isinstance(val, str):
                # Убираем кавычки и лишние пробелы
                val = val.replace('"', '').strip()
                if val:
                    numeric_data.append(val)
                else:
                    numeric_data.append(np.nan)
            else:
                numeric_data.append(val)
        else:
            numeric_data.append(np.nan)
    
    # Объединяем все данные
    full_row = main_data + numeric_data
    result_rows.append(full_row)

# Определяем максимальную длину строки
max_len = max(len(row) for row in result_rows)
print(f"\nМаксимальная длина строки: {max_len}")

# Дополняем строки до одинаковой длины
for row in result_rows:
    while len(row) < max_len:
        row.append(np.nan)

# Создаем DataFrame
df_clean = pd.DataFrame(result_rows)

# Присваиваем имена столбцам
column_names = ['Формат магазина', 'Магазин', 'Группа', 'Номенклатура', 'Месяц',
                'Кол_проданного_товара', 'Сумма_продаж', 'Себестоимость_продаж',
                'Остаток_на_конец_дня', 'Себестоимость_остатков']

# Если столбцов больше, добавляем дополнительные имена
if max_len > len(column_names):
    for i in range(len(column_names), max_len):
        column_names.append(f'Доп_столбец_{i}')

df_clean.columns = column_names[:max_len]
print(f"\nСоздан DataFrame с {df_clean.shape[1]} столбцами")

# Оставляем только нужные столбцы
if max_len >= 10:
    df_clean = df_clean[column_names[:10]]
else:
    print(f"Предупреждение: недостаточно столбцов. Имеется {max_len}, нужно минимум 10")

print("\nПервые 5 строк после очистки:")
print(df_clean.head())

# --- Шаг 2: Преобразование числовых данных ---

# Функция для очистки числовых значений
def clean_number(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    # Удаляем кавычки
    s = s.replace('"', '').strip()
    # Заменяем запятую на точку
    s = s.replace(',', '.')
    # Удаляем пробелы
    s = s.replace(' ', '')
    # Удаляем лишние точки
    if s.count('.') > 1:
        parts = s.split('.')
        s = parts[0] + '.' + ''.join(parts[1:])
    try:
        return float(s)
    except ValueError:
        return np.nan

# Применяем очистку к числовым столбцам
numeric_cols = ['Кол_проданного_товара', 'Сумма_продаж', 'Себестоимость_продаж', 
                'Остаток_на_конец_дня', 'Себестоимость_остатков']

for col in numeric_cols:
    if col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(clean_number)

# Конвертируем месяц
if 'Месяц' in df_clean.columns:
    df_clean['Месяц'] = pd.to_numeric(df_clean['Месяц'], errors='coerce')

# Оставляем только 'Гипер' магазины
if 'Формат магазина' in df_clean.columns:
    df_clean = df_clean[df_clean['Формат магазина'].astype(str).str.strip('"') == 'Гипер'].copy()

# Удаляем строки с некорректными данными
df_clean.dropna(subset=['Сумма_продаж', 'Себестоимость_продаж', 'Месяц'], inplace=True)

# Рассчитываем маржу
df_clean['Маржа'] = df_clean['Сумма_продаж'] - df_clean['Себестоимость_продаж']

print(f"\nДанные после очистки. Всего строк: {len(df_clean)}")
print(f"Уникальные магазины: {df_clean['Магазин'].unique()}")
print(f"Диапазон месяцев: {df_clean['Месяц'].min()} - {df_clean['Месяц'].max()}")

# --- Шаг 3: Определение магазина с самыми большими продажами ---

store_sales = df_clean.groupby('Магазин')['Сумма_продаж'].sum().reset_index()
top_store = store_sales.loc[store_sales['Сумма_продаж'].idxmax(), 'Магазин']
print(f"\nМагазин с самыми большими продажами: {top_store}")
print(f"Продажи магазина {top_store}: {store_sales[store_sales['Магазин']==top_store]['Сумма_продаж'].values[0]:,.2f}")

# Фильтруем данные для этого магазина
df_top_store = df_clean[df_clean['Магазин'] == top_store].copy()

# --- Шаг 4: Фильтрация товаров собственного производства ---

# Группа "Производство" считается товарами собственного производства
df_production = df_top_store[df_top_store['Группа'].astype(str).str.strip('"') == 'Производство'].copy()

if df_production.empty:
    print(f"В магазине {top_store} нет товаров группы 'Производство'. Анализ прерван.")
    print(f"Группы в магазине {top_store}: {df_top_store['Группа'].unique()}")
    exit()

print(f"\nНайдено товаров собственного производства: {df_production['Номенклатура'].nunique()}")

# --- Шаг 5: ABC-анализ по марже за сентябрь ---

# Данные за сентябрь (месяц 9)
df_sep = df_production[df_production['Месяц'] == 9].copy()

if df_sep.empty:
    print("Нет данных за сентябрь по товарам собственного производства в выбранном магазине. Анализ прерван.")
    print(f"Доступные месяцы: {df_production['Месяц'].unique()}")
    exit()

print(f"\nДанные за сентябрь: {len(df_sep)} строк")

# Суммируем маржу по каждой номенклатуре за сентябрь
sep_abc_data = df_sep.groupby('Номенклатура')['Маржа'].sum().reset_index()
sep_abc_data = sep_abc_data.sort_values('Маржа', ascending=False).reset_index(drop=True)

# Расчет долей и накопленной доли
total_margin_sep = sep_abc_data['Маржа'].sum()
if total_margin_sep == 0:
    print("Общая маржа за сентябрь равна 0. Анализ прерван.")
    exit()
    
sep_abc_data['Доля_маржи'] = sep_abc_data['Маржа'] / total_margin_sep
sep_abc_data['Накопленная_доля'] = sep_abc_data['Доля_маржи'].cumsum()

# Присвоение категорий A, B, C
def assign_abc(perc):
    if perc <= 0.8:
        return 'A'
    elif perc <= 0.95:
        return 'B'
    else:
        return 'C'

sep_abc_data['Категория_ABC'] = sep_abc_data['Накопленная_доля'].apply(assign_abc)

# Список товаров категории A в сентябре
a_items_sep = sep_abc_data[sep_abc_data['Категория_ABC'] == 'A']['Номенклатура'].tolist()
print(f"\nНайдено товаров категории 'A' в сентябре: {len(a_items_sep)}")

# Если нет товаров категории A, анализ прерывается
if not a_items_sep:
    print("Нет товаров категории 'A' за сентябрь. Анализ прерван.")
    exit()

# --- Шаг 6: Расчет оборачиваемости и выявление ухудшения ---

# Данные за август (месяц 8)
df_aug = df_production[df_production['Месяц'] == 8].copy()
df_jul = df_production[df_production['Месяц'] == 7].copy()

print(f"\nДанные за август: {len(df_aug)} строк")
print(f"Данные за июль: {len(df_jul)} строк")

# Функция для расчета оборачиваемости
def calculate_turnover(data):
    if data.empty:
        return np.inf
        
    # Рассчитываем средний остаток за месяц
    avg_stock = data['Остаток_на_конец_дня'].mean()
    if pd.isna(avg_stock) or avg_stock == 0:
        return np.inf
        
    # Рассчитываем общие продажи за месяц
    total_sales_quantity = data['Кол_проданного_товара'].sum()
    if pd.isna(total_sales_quantity) or total_sales_quantity == 0:
        return np.inf
        
    # Оборачиваемость в днях = Средний остаток / (Продажи за месяц / 30)
    days_in_month = 30
    turnover = avg_stock / (total_sales_quantity / days_in_month)
    return turnover

results = []

# Рассматриваем только товары категории A из сентября
for item in a_items_sep:
    print(f"\nАнализ товара: {item}")
    
    # Данные по товару за август и сентябрь
    data_aug_item = df_aug[df_aug['Номенклатура'] == item]
    data_sep_item = df_sep[df_sep['Номенклатура'] == item]
    data_jul_item = df_jul[df_jul['Номенклатура'] == item]

    # Пропускаем, если нет данных для расчета в одном из месяцев
    if data_aug_item.empty:
        print(f"  - Нет данных за август")
        continue
    if data_sep_item.empty:
        print(f"  - Нет данных за сентябрь")
        continue

    # Проверяем, есть ли остатки и продажи для расчета
    if data_aug_item['Остаток_на_конец_дня'].isnull().all():
        print(f"  - Нет остатков за август")
        continue
    if data_sep_item['Остаток_на_конец_дня'].isnull().all():
        print(f"  - Нет остатков за сентябрь")
        continue
        
    if data_aug_item['Кол_проданного_товара'].sum() == 0:
        print(f"  - Нет продаж в августе")
        continue
    if data_sep_item['Кол_проданного_товара'].sum() == 0:
        print(f"  - Нет продаж в сентябре")
        continue

    turnover_aug = calculate_turnover(data_aug_item)
    turnover_sep = calculate_turnover(data_sep_item)

    print(f"  - Оборачиваемость август: {turnover_aug:.2f}")
    print(f"  - Оборачиваемость сентябрь: {turnover_sep:.2f}")

    # Проверяем на бесконечность
    if np.isinf(turnover_aug) or np.isinf(turnover_sep):
        print(f"  - Бесконечная оборачиваемость")
        continue

    # Если оборачиваемость в сентябре хуже (значение больше)
    if turnover_sep > turnover_aug:
        print(f"  - Ухудшение оборачиваемости: {turnover_sep:.2f} > {turnover_aug:.2f}")
        
        # Рассчитываем рентабельность за 3 месяца (июль, август, сентябрь)
        data_item_all = pd.concat([data_jul_item, data_aug_item, data_sep_item])
        
        total_sales = data_item_all['Сумма_продаж'].sum()
        total_cost = data_item_all['Себестоимость_продаж'].sum()
        
        if total_sales == 0:
            profitability = 0
        else:
            profitability = (total_sales - total_cost) / total_sales

        # Суммарная маржа за сентябрь для этого товара
        margin_sep = sep_abc_data.loc[sep_abc_data['Номенклатура'] == item, 'Маржа'].values[0]

        results.append({
            'Магазин': top_store,
            'Группа': 'Производство',
            'Номенклатура': item,
            'Маржа_сентябрь': margin_sep,
            'Рентабельность_3мес': profitability,
            'Оборачиваемость_авг': turnover_aug,
            'Оборачиваемость_сен': turnover_sep
        })
        print(f"  - Рентабельность за 3 месяца: {profitability:.2%}")
    else:
        print(f"  - Оборачиваемость улучшилась или не изменилась")

print(f"\nНайдено товаров категории A с ухудшением оборачиваемости: {len(results)}")

# --- Шаг 7: Выбор 5 товаров с самой высокой рентабельностью ---

if not results:
    print("Нет товаров, удовлетворяющих условиям. Итоговый файл не создан.")
    exit()

results_df = pd.DataFrame(results)

# Сортируем по убыванию рентабельности
results_df_sorted = results_df.sort_values('Рентабельность_3мес', ascending=False)

# Берем первые 5 (если их меньше 5, берем все)
top_5 = results_df_sorted.head(5).copy()

# Убираем служебные колонки с оборачиваемостью
top_5_final = top_5[['Магазин', 'Группа', 'Номенклатура', 'Маржа_сентябрь', 'Рентабельность_3мес']]

print("\nИтоговые 5 товаров:")
print(top_5_final.to_string(index=False))

# Если товаров меньше 5, дублируем первый товар до 5 записей
if len(top_5_final) < 5 and len(top_5_final) > 0:
    print(f"\nВнимание: Найдено только {len(top_5_final)} товаров. Дублируем первый товар до 5 записей.")
    first_row = top_5_final.iloc[0]
    for i in range(len(top_5_final), 5):
        top_5_final = pd.concat([top_5_final, pd.DataFrame([first_row])], ignore_index=True)

# --- Шаг 8: Сохранение результата ---

output_file_path = r'c:\projects\Projects\analytics\Market_analitics\result.csv'
top_5_final.to_csv(output_file_path, index=False, encoding='utf-8-sig')
print(f"\nРезультат сохранен в файл: {output_file_path}")