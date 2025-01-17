# Импортируем библиотеки
import feedparser
import pandahouse as ph
import clickhouse_connect
import pandas as pd
import numpy as np
import json

# Парсим данные
d = feedparser.parse('https://tass.ru/rss/v2.xml')
data_list = []
for i in d["entries"]:
    data_list.append([i["title"],i["link"],i["tags"][0].term,i["published"]])
df = pd.DataFrame(data_list, columns=["title","link","tags","published"])
df['published'] = df['published'].astype('datetime64[ns]')

# Сразу сделаем контроль, что все у нас нормально записалось и нет съехавших значений
# Если есть - удаляем строку
df.dropna()

# Запишем промежуточные данные в файлы
with open('rawDataTass.json', 'w', encoding='utf-8') as fp:
    json.dump(d, fp, ensure_ascii=False)

with open('MidDataTass.json', 'w', encoding='utf-8') as fp:
    json.dump(data_list, fp, ensure_ascii=False)

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

# Повторим контроль, перед записью в БД
# Если есть - удаляем строку
df.dropna()

# Создадим табличку в БД и запишем наши данные
client = clickhouse_connect.get_client(host='192.168.3.18', username='default', password='')
client.command('CREATE TABLE IF NOT EXISTS tassRSS (title String, link String,tags String, category_id Int32, published DateTime) ENGINE MergeTree ORDER BY published')
connection = dict(database='default',
                  host='http://192.168.3.18:8123',
                  user='default',
                  password='')
ph.to_clickhouse(df, 'tassRSS', index=False, chunksize=100000, connection=connection)
# Если были дубликаты - удаляем
client.command('OPTIMIZE TABLE tassRSS FINAL DEDUPLICATE')