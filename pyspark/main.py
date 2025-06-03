from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Инициализация SparkSession
spark = SparkSession.builder.appName('ProductsCategories').getOrCreate()

# Примерные данные
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
    (1, 1),  # Молоко - Молочные
    (3, 1),  # Сыр - Молочные
    (2, 3),  # Хлеб - Выпечка
    (4, 2),  # Яблоко - Фрукты
]

# Создание датафреймов
products = spark.createDataFrame(products_data, ['product_id', 'product_name'])
categories = spark.createDataFrame(categories_data, ['category_id', 'category_name'])
product_category = spark.createDataFrame(product_category_data, ['product_id', 'category_id'])

# Метод для получения всех пар 'Имя продукта – Имя категории' и продуктов без категорий
def get_product_category_pairs_and_orphans(products, categories, product_category):
    # Джойним продукты с категориями через таблицу связей (left join, чтобы получить и продукты без категорий)
    joined = products.join(product_category, on='product_id', how='left') \
                   .join(categories, on='category_id', how='left')

    # Все пары 'Имя продукта – Имя категории' (без None)
    pairs = joined.filter(col('category_name').isNotNull()) \
                 .select('product_name', 'category_name')

    # Продукты без категорий
    orphans = joined.filter(col('category_name').isNull()) \
                   .select('product_name').distinct()

    return pairs, orphans

if __name__ == '__main__':
    pairs, orphans = get_product_category_pairs_and_orphans(products, categories, product_category)
    print('Пары "Имя продукта – Имя категории":')
    pairs.show(truncate=False)
    print('Продукты без категорий:')
    orphans.show(truncate=False)
    spark.stop() 