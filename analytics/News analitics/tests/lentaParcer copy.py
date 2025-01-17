# Импортируем библиотеки
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow import DAG
import pandahouse as ph
import clickhouse_connect
import pandas as pd
import numpy as np
import feedparser


def lentaparcer():

# Парсим данные
 d = feedparser.parse('https://lenta.ru/rss/')
 data_list = []
 for i in d['entries']:
    data_list.append([i["summary"],i["link"],i["tags"][0].term,i["published"]])
 df = pd.DataFrame(data_list, columns=["summary","link","tags","published"])
 df['published'] = df['published'].astype('datetime64[ns]')
# Переименуем колонку для приведения к общему виду
 df = df.rename(columns={'summary': 'title'})

# Создаем классификатор по категориям
 conditions = [(df['tags'] == 'Политика') , (df['tags'] == 'Общество'), (df['tags'] == 'Бизнес'), (df['tags'] == 'Экономика'), (df['tags'] == 'Финансы'), (df['tags'] == 'Медиа'), (df['tags'] == 'Авто'), (df['tags'] == 'Политика / Власть'), 
(df['tags'] == 'Политика / Международные отношения'), (df['tags'] == 'Технологии'), (df['tags'] == 'Среда обитания'), (df['tags'] == 'Недвижимость'), (df['tags'] == 'Экономика и бизнес'), (df['tags'] == 'Армия и ОПК'), (df['tags'] == 'Происшествия'),
(df['tags'] == 'Культура'), (df['tags'] == 'НедвижимостьОбщество'), (df['tags'] == 'Международная панорама'), (df['tags'] == 'Спорт'), (df['tags'] == 'Москва'), (df['tags'] == 'Северный Кавказ'), (df['tags'] == 'Космос'), (df['tags'] == 'Биографии и справки'),
(df['tags'] == 'Военная операция на Украине'), (df['tags'] == 'Мир'), (df['tags'] == 'Забота о себе'), (df['tags'] == 'Россия'), (df['tags'] == 'Путешествия'), (df['tags'] == 'Ценности'), (df['tags'] == 'Бывший СССР'), (df['tags'] == 'Интернет и СМИ'),
(df['tags'] == 'Силовые структуры'), (df['tags'] == 'Наука и техника'), (df['tags'] == 'Из жизни'), (df['tags'] == 'Моя страна'), (df['tags'] == 'Национальные проекты'), (df['tags'] == 'Новости партнеров'), (df['tags'] == 'Новости регионов'), (df['tags'] == '69-я параллель')]

 choices = ['Политика', 'Общество', 'Экономика', 'Экономика', 'Экономика', 'Медиа и СМИ', 'Технологии', 'Политика', 'Политика', 'Технологии', 'Общество', 'Экономика', 'Экономика', 'Технологии', 'Общество', 'Общество', 'Экономика', 'Политика', 'Спорт и здоровье', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Технологии', 'Общество', 'Россия и бывший СССР', 'Общество', 'Общество', 'Россия и бывший СССР', 'Спорт и здоровье', 'Общество', 'Россия и бывший СССР', 'Медиа и СМИ', 'Общество', 'Технологии', 'Общество', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Медиа и СМИ', 'Россия и бывший СССР', 'Россия и бывший СССР']

 df['tags'] = np.select(conditions, choices, default='Разное')

 conditions1 = [(df['tags'] == 'Политика'), (df['tags'] == 'Общество'), (df['tags'] == 'Экономика'), (df['tags'] == 'Медиа и СМИ'), (df['tags'] == 'Технологии'), (df['tags'] == 'Спорт и здоровье'), (df['tags'] == 'Россия и бывший СССР'),
(df['tags'] == 'Спорт и здоровье')]
 choices1 = [1,2,3,4,5,6,7,8]
 df['category_id'] = np.select(conditions1, choices1, default=0)
 client = clickhouse_connect.get_client(host='192.168.3.18', username='default', password='')
 client.command('CREATE TABLE IF NOT EXISTS lentaRSS1 (title String, link String,tags String, category_id Int32, published DateTime) ENGINE MergeTree ORDER BY published')
 connection = dict(database='default',
                 host='http://192.168.3.18:8123',
                 user='default',
                 password='')
 ph.to_clickhouse(df, 'lentaRSS1', index=False, chunksize=100000, connection=connection)
#Если были дубликаты - удаляем
 client.command('OPTIMIZE TABLE lentaRSS1 FINAL DEDUPLICATE')


with DAG (dag_id="lenta_parcer_dag", start_date=datetime(2023, 1, 23), schedule="0 0 * * *") as dag:
    python_task = PythonOperator(task_id="world", python_callable = lentaparcer)
    bash_task = BashOperator(task_id="hello", bash_command="echo hello")
bash_task >> python_task




# Создадим табличку в БД и запишем наши данные
# client = clickhouse_connect.get_client(host='localhost', username='default', password='')
# client.command('CREATE TABLE IF NOT EXISTS lentaRSS (title String, link String,tags String, category_id Int32, published DateTime) ENGINE MergeTree ORDER BY published')
# connection = dict(database='default',
#                   host='http://localhost:8123',
#                   user='default',
#                   password='')
# ph.to_clickhouse(df, 'lentaRSS', index=False, chunksize=100000, connection=connection)
# # Если были дубликаты - удаляем
# client.command('OPTIMIZE TABLE lentaRSS FINAL DEDUPLICATE')
