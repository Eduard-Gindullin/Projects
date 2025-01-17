# Импортируем библиотеки
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow import DAG
import pandahouse as ph
import clickhouse_connect
import pandas as pd
import numpy as np
import feedparser
import json

## DB Connect
connection = dict(database='default',
                 host='http://192.168.3.18:8123',
                 user='default',
                 password='')
client = clickhouse_connect.get_client(host='192.168.3.18', username='default', password='')


##  ЛЕНТА
## 
def lentaParcer():
# Парсим данные Ленты
 Lenta = feedparser.parse('https://lenta.ru/rss/')
 Lenta_list = []
 for i in Lenta['entries']:
    Lenta_list.append([i["summary"],i["link"],i["tags"][0].term,i["published"]])
 Lenta_df = pd.DataFrame(Lenta_list, columns=["summary","link","tags","published"])
 Lenta_df['published'] = Lenta_df['published'].astype('datetime64[ns]')
# Переименуем колонку для приведения к общему виду
 Lenta_df = Lenta_df.rename(columns={'summary': 'title'})

 # Сразу сделаем контроль, что все у нас нормально записалось и нет съехавших значений
 # Если есть - удаляем строку
 Lenta_df.dropna()

 # Запишем промежуточные данные в файлы
 with open('rawDataLenta.json', 'w', encoding='utf-8') as fp:
     json.dump(Lenta, fp, ensure_ascii=False)

 with open('MidDataLenta.json', 'w', encoding='utf-8') as fp:
     json.dump(Lenta_list, fp, ensure_ascii=False)

# Создаем классификатор по категориям
 conditions = [(Lenta_df['tags'] == 'Политика') , (Lenta_df['tags'] == 'Общество'), (Lenta_df['tags'] == 'Бизнес'), (Lenta_df['tags'] == 'Экономика'), (Lenta_df['tags'] == 'Финансы'), (Lenta_df['tags'] == 'Медиа'), (Lenta_df['tags'] == 'Авто'), (Lenta_df['tags'] == 'Политика / Власть'), 
(Lenta_df['tags'] == 'Политика / Международные отношения'), (Lenta_df['tags'] == 'Технологии'), (Lenta_df['tags'] == 'Среда обитания'), (Lenta_df['tags'] == 'Недвижимость'), (Lenta_df['tags'] == 'Экономика и бизнес'), (Lenta_df['tags'] == 'Армия и ОПК'), (Lenta_df['tags'] == 'Происшествия'),
(Lenta_df['tags'] == 'Культура'), (Lenta_df['tags'] == 'НедвижимостьОбщество'), (Lenta_df['tags'] == 'Международная панорама'), (Lenta_df['tags'] == 'Спорт'), (Lenta_df['tags'] == 'Москва'), (Lenta_df['tags'] == 'Северный Кавказ'), (Lenta_df['tags'] == 'Космос'), (Lenta_df['tags'] == 'Биографии и справки'),
(Lenta_df['tags'] == 'Военная операция на Украине'), (Lenta_df['tags'] == 'Мир'), (Lenta_df['tags'] == 'Забота о себе'), (Lenta_df['tags'] == 'Россия'), (Lenta_df['tags'] == 'Путешествия'), (Lenta_df['tags'] == 'Ценности'), (Lenta_df['tags'] == 'Бывший СССР'), (Lenta_df['tags'] == 'Интернет и СМИ'),
(Lenta_df['tags'] == 'Силовые структуры'), (Lenta_df['tags'] == 'Наука и техника'), (Lenta_df['tags'] == 'Из жизни'), (Lenta_df['tags'] == 'Моя страна'), (Lenta_df['tags'] == 'Национальные проекты'), (Lenta_df['tags'] == 'Новости партнеров'), (Lenta_df['tags'] == 'Новости регионов'), (Lenta_df['tags'] == '69-я параллель')]

 choices = ['Политика', 'Общество', 'Экономика', 'Экономика', 'Экономика', 'Медиа и СМИ', 'Технологии', 'Политика', 'Политика', 'Технологии', 'Общество', 'Экономика', 'Экономика', 'Технологии', 'Общество', 'Общество', 'Экономика', 'Политика', 'Спорт и здоровье', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Технологии', 'Общество', 'Россия и бывший СССР', 'Общество', 'Общество', 'Россия и бывший СССР', 'Спорт и здоровье', 'Общество', 'Россия и бывший СССР', 'Медиа и СМИ', 'Общество', 'Технологии', 'Общество', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Медиа и СМИ', 'Россия и бывший СССР', 'Россия и бывший СССР']

 Lenta_df['tags'] = np.select(conditions, choices, default='Разное')

 conditions1 = [(Lenta_df['tags'] == 'Политика'), (Lenta_df['tags'] == 'Общество'), (Lenta_df['tags'] == 'Экономика'), (Lenta_df['tags'] == 'Медиа и СМИ'), (Lenta_df['tags'] == 'Технологии'), (Lenta_df['tags'] == 'Спорт и здоровье'), (Lenta_df['tags'] == 'Россия и бывший СССР'),
(Lenta_df['tags'] == 'Спорт и здоровье')]
 choices1 = [1,2,3,4,5,6,7,8]
 Lenta_df['category_id'] = np.select(conditions1, choices1, default=0)
 # Повторим контроль, перед записью в БД
 # Если есть пустые - удаляем строку
 Lenta_df.dropna()
# Создаем таблицу
 client.command('CREATE TABLE IF NOT EXISTS lentaRSS (title String, link String,tags String, category_id Int32, published DateTime) ENGINE MergeTree ORDER BY published')
# Записываем в таблицу полученные данные
 ph.to_clickhouse(Lenta_df, 'lentaRSS', index=False, chunksize=100000, connection=connection)
#Если были дубликаты - удаляем
 client.command('OPTIMIZE TABLE lentaRSS FINAL DEDUPLICATE')

## ТАСС
##
def tassParcer():

# Парсим данные Тасс
 Tass = feedparser.parse('https://tass.ru/rss/v2.xml')
 Tass_list = []
 for i in Tass['entries']:
    Tass_list.append([i["title"],i["link"],i["tags"][0].term,i["published"]])
 Tass_df = pd.DataFrame(Tass_list, columns=["title","link","tags","published"])
 Tass_df['published'] = Tass_df['published'].astype('datetime64[ns]')

# Сразу сделаем контроль, что все у нас нормально записалось и нет съехавших значений
# Если есть - удаляем строку
 Tass_df.dropna()

# Запишем промежуточные данные в файлы
 with open('rawDataTass.json', 'w', encoding='utf-8') as fp:
     json.dump(Tass, fp, ensure_ascii=False)

 with open('MidDataTass.json', 'w', encoding='utf-8') as fp:
     json.dump(Tass_list, fp, ensure_ascii=False)

# Создаем классификатор по категориям
 conditions = [(Tass_df['tags'] == 'Политика') , (Tass_df['tags'] == 'Общество'), (Tass_df['tags'] == 'Бизнес'), (Tass_df['tags'] == 'Экономика'), (Tass_df['tags'] == 'Финансы'), (Tass_df['tags'] == 'Медиа'), (Tass_df['tags'] == 'Авто'), (Tass_df['tags'] == 'Политика / Власть'), 
(Tass_df['tags'] == 'Политика / Международные отношения'), (Tass_df['tags'] == 'Технологии'), (Tass_df['tags'] == 'Среда обитания'), (Tass_df['tags'] == 'Недвижимость'), (Tass_df['tags'] == 'Экономика и бизнес'), (Tass_df['tags'] == 'Армия и ОПК'), (Tass_df['tags'] == 'Происшествия'),
(Tass_df['tags'] == 'Культура'), (Tass_df['tags'] == 'НедвижимостьОбщество'), (Tass_df['tags'] == 'Международная панорама'), (Tass_df['tags'] == 'Спорт'), (Tass_df['tags'] == 'Москва'), (Tass_df['tags'] == 'Северный Кавказ'), (Tass_df['tags'] == 'Космос'), (Tass_df['tags'] == 'Биографии и справки'),
(Tass_df['tags'] == 'Военная операция на Украине'), (Tass_df['tags'] == 'Мир'), (Tass_df['tags'] == 'Забота о себе'), (Tass_df['tags'] == 'Россия'), (Tass_df['tags'] == 'Путешествия'), (Tass_df['tags'] == 'Ценности'), (Tass_df['tags'] == 'Бывший СССР'), (Tass_df['tags'] == 'Интернет и СМИ'),
(Tass_df['tags'] == 'Силовые структуры'), (Tass_df['tags'] == 'Наука и техника'), (Tass_df['tags'] == 'Из жизни'), (Tass_df['tags'] == 'Моя страна'), (Tass_df['tags'] == 'Национальные проекты'), (Tass_df['tags'] == 'Новости партнеров'), (Tass_df['tags'] == 'Новости регионов'), (Tass_df['tags'] == '69-я параллель')]

 choices = ['Политика', 'Общество', 'Экономика', 'Экономика', 'Экономика', 'Медиа и СМИ', 'Технологии', 'Политика', 'Политика', 'Технологии', 'Общество', 'Экономика', 'Экономика', 'Технологии', 'Общество', 'Общество', 'Экономика', 'Политика', 'Спорт и здоровье', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Технологии', 'Общество', 'Россия и бывший СССР', 'Общество', 'Общество', 'Россия и бывший СССР', 'Спорт и здоровье', 'Общество', 'Россия и бывший СССР', 'Медиа и СМИ', 'Общество', 'Технологии', 'Общество', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Медиа и СМИ', 'Россия и бывший СССР', 'Россия и бывший СССР']

 Tass_df['tags'] = np.select(conditions, choices, default='Разное')

 conditions1 = [(Tass_df['tags'] == 'Политика'), (Tass_df['tags'] == 'Общество'), (Tass_df['tags'] == 'Экономика'), (Tass_df['tags'] == 'Медиа и СМИ'), (Tass_df['tags'] == 'Технологии'), (Tass_df['tags'] == 'Спорт и здоровье'), (Tass_df['tags'] == 'Россия и бывший СССР'),
(Tass_df['tags'] == 'Спорт и здоровье')]
 choices1 = [1,2,3,4,5,6,7,8]
 Tass_df['category_id'] = np.select(conditions1, choices1, default=0)
 # Повторим контроль, перед записью в БД
 # Если есть пустые - удаляем строку
 Tass_df.dropna()
 # Создаем таблицу
 client.command('CREATE TABLE IF NOT EXISTS tassRSS (title String, link String,tags String, category_id Int32, published DateTime) ENGINE MergeTree ORDER BY published')
# Записываем в таблицу полученные данные
 ph.to_clickhouse(Tass_df, 'tassRSS', index=False, chunksize=100000, connection=connection)
#Если были дубликаты - удаляем
 client.command('OPTIMIZE TABLE tassRSS FINAL DEDUPLICATE')

## ВЕДОМОСТИ
##
def vedomostiParcer():

# Парсим данные Ведомости
 Vedomosti = feedparser.parse('https://www.vedomosti.ru/rss/news')
 Vedomosti_list = []
 for i in Vedomosti['entries']:
    Vedomosti_list.append([i["title"],i["link"],i["tags"][0].term,i["published"]])
 Vedomosti_df = pd.DataFrame(Vedomosti_list, columns=["title","link","tags","published"])
 Vedomosti_df['published'] = Vedomosti_df['published'].astype('datetime64[ns]')

# Сразу сделаем контроль, что все у нас нормально записалось и нет съехавших значений
# Если есть - удаляем строку
 Vedomosti_df.dropna()

   # Запишем промежуточные данные в файлы
 with open('rawDataVedomosti.json', 'w', encoding='utf-8') as fp:
     json.dump(Vedomosti, fp, ensure_ascii=False)

 with open('MidDataVedomosti.json', 'w', encoding='utf-8') as fp:
     json.dump(Vedomosti_list, fp, ensure_ascii=False)

# Создаем классификатор по категориям
 conditions = [(Vedomosti_df['tags'] == 'Политика') , (Vedomosti_df['tags'] == 'Общество'), (Vedomosti_df['tags'] == 'Бизнес'), (Vedomosti_df['tags'] == 'Экономика'), (Vedomosti_df['tags'] == 'Финансы'), (Vedomosti_df['tags'] == 'Медиа'), (Vedomosti_df['tags'] == 'Авто'), (Vedomosti_df['tags'] == 'Политика / Власть'), 
(Vedomosti_df['tags'] == 'Политика / Международные отношения'), (Vedomosti_df['tags'] == 'Технологии'), (Vedomosti_df['tags'] == 'Среда обитания'), (Vedomosti_df['tags'] == 'Недвижимость'), (Vedomosti_df['tags'] == 'Экономика и бизнес'), (Vedomosti_df['tags'] == 'Армия и ОПК'), (Vedomosti_df['tags'] == 'Происшествия'),
(Vedomosti_df['tags'] == 'Культура'), (Vedomosti_df['tags'] == 'НедвижимостьОбщество'), (Vedomosti_df['tags'] == 'Международная панорама'), (Vedomosti_df['tags'] == 'Спорт'), (Vedomosti_df['tags'] == 'Москва'), (Vedomosti_df['tags'] == 'Северный Кавказ'), (Vedomosti_df['tags'] == 'Космос'), (Vedomosti_df['tags'] == 'Биографии и справки'),
(Vedomosti_df['tags'] == 'Военная операция на Украине'), (Vedomosti_df['tags'] == 'Мир'), (Vedomosti_df['tags'] == 'Забота о себе'), (Vedomosti_df['tags'] == 'Россия'), (Vedomosti_df['tags'] == 'Путешествия'), (Vedomosti_df['tags'] == 'Ценности'), (Vedomosti_df['tags'] == 'Бывший СССР'), (Vedomosti_df['tags'] == 'Интернет и СМИ'),
(Vedomosti_df['tags'] == 'Силовые структуры'), (Vedomosti_df['tags'] == 'Наука и техника'), (Vedomosti_df['tags'] == 'Из жизни'), (Vedomosti_df['tags'] == 'Моя страна'), (Vedomosti_df['tags'] == 'Национальные проекты'), (Vedomosti_df['tags'] == 'Новости партнеров'), (Vedomosti_df['tags'] == 'Новости регионов'), (Vedomosti_df['tags'] == '69-я параллель')]

 choices = ['Политика', 'Общество', 'Экономика', 'Экономика', 'Экономика', 'Медиа и СМИ', 'Технологии', 'Политика', 'Политика', 'Технологии', 'Общество', 'Экономика', 'Экономика', 'Технологии', 'Общество', 'Общество', 'Экономика', 'Политика', 'Спорт и здоровье', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Технологии', 'Общество', 'Россия и бывший СССР', 'Общество', 'Общество', 'Россия и бывший СССР', 'Спорт и здоровье', 'Общество', 'Россия и бывший СССР', 'Медиа и СМИ', 'Общество', 'Технологии', 'Общество', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Медиа и СМИ', 'Россия и бывший СССР', 'Россия и бывший СССР']

 Vedomosti_df['tags'] = np.select(conditions, choices, default='Разное')

 conditions1 = [(Vedomosti_df['tags'] == 'Политика'), (Vedomosti_df['tags'] == 'Общество'), (Vedomosti_df['tags'] == 'Экономика'), (Vedomosti_df['tags'] == 'Медиа и СМИ'), (Vedomosti_df['tags'] == 'Технологии'), (Vedomosti_df['tags'] == 'Спорт и здоровье'), (Vedomosti_df['tags'] == 'Россия и бывший СССР'),
(Vedomosti_df['tags'] == 'Спорт и здоровье')]
 choices1 = [1,2,3,4,5,6,7,8]
 Vedomosti_df['category_id'] = np.select(conditions1, choices1, default=0)
# Повторим контроль, перед записью в БД
# Если есть пустые - удаляем строку
 Vedomosti_df.dropna()
 # Создаем таблицу
 client.command('CREATE TABLE IF NOT EXISTS vedomostiRSS (title String, link String,tags String, category_id Int32, published DateTime) ENGINE MergeTree ORDER BY published')
# Записываем в таблицу полученные данные
 ph.to_clickhouse(Vedomosti_df, 'vedomostiRSS', index=False, chunksize=100000, connection=connection)
#Если были дубликаты - удаляем
 client.command('OPTIMIZE TABLE vedomostiRSS FINAL DEDUPLICATE')

#Напишем даги
with DAG (dag_id="news_parcer_dag", start_date=datetime(2023, 1, 23), catchup=False, schedule='@once') as dag:
    start = BashOperator(task_id="we_start", bash_command="echo pocess started")
    LentaInit = PythonOperator(task_id="Lenta", python_callable = lentaParcer)
    TassInit = PythonOperator(task_id="Tass", python_callable = tassParcer)
    VedomostiInit = PythonOperator(task_id="Vedomosti", python_callable = vedomostiParcer)
    finish = BashOperator(task_id="all_done", bash_command="echo process finished")
start >> LentaInit >> finish
start >> TassInit >> finish
start >> VedomostiInit >> finish