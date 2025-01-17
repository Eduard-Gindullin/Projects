# Импортируем библиотеки
import pandahouse as ph
import feedparser
import clickhouse_connect
import pandas as pd
import numpy as np

# Подключаемся к БД
client = clickhouse_connect.get_client(host='192.168.3.18', username='default', password='')
connection = dict(database='default',
                  host='http://192.168.3.18:8123',
                  user='default',
                  password='')
last_published = client.command('Select * from tassRSS where published IN (SELECT MAX(`published`) as `time` FROM `tassRSS`)')
# Узнаем когда была последняя публикация
time = last_published[4]

#Парсим все что нам готова дать RSS
d = feedparser.parse('https://tass.ru/rss/v2.xml')
data_list = []
for i in d['entries']:
    data_list.append([i["title"],i["link"],i["tags"][0].term,i["published"]])
df = pd.DataFrame(data_list, columns=["title","link","tags","published"])
df['published'] = df['published'].astype('datetime64[ns]')

# Сразу сделаем контроль, что все у нас нормально записалось и нет съехавших значений
# Если есть - удаляем строку
df.dropna()

# Копируем классификатор по категориям
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

# Делаем выборку из спарсеного ДФ по дате и времени публикации, забираем 
# только новое и дописываем в БД
df1 = df[df['published'] > time]
ph.to_clickhouse(df1, 'tassRSS', index=False, chunksize=100000, connection=connection)
client.command('OPTIMIZE TABLE vedomostiRSS FINAL DEDUPLICATE')

print(df1)
