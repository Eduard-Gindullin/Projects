#vedomosti
import clickhouse2pandas as ch2pd

connection_url = 'http://default:@localhost:8123'
query = 'select * from vedomosti limit 1000000'

df2= ch2pd.select(connection_url, query)
df2['published'] = df2['published'].astype('datetime64[ns]')


connection = dict(database='default',
                  host='http://localhost:8123',
                  user='default',
                 password='')
conditions = [(df2['tags'] == 'Политика') , (df2['tags'] == 'Общество'), (df2['tags'] == 'Бизнес'), (df2['tags'] == 'Экономика'), (df2['tags'] == 'Финансы'), (df2['tags'] == 'Медиа'), (df2['tags'] == 'Авто'), (df2['tags'] == 'Политика / Власть'), 
(df2['tags'] == 'Политика / Международные отношения'), (df2['tags'] == 'Технологии'), (df2['tags'] == 'Среда обитания'), (df2['tags'] == 'Недвижимость'), (df2['tags'] == 'Экономика и бизнес'), (df2['tags'] == 'Армия и ОПК'), (df2['tags'] == 'Происшествия'),
(df2['tags'] == 'Культура'), (df2['tags'] == 'НедвижимостьОбщество'), (df2['tags'] == 'Международная панорама'), (df2['tags'] == 'Спорт'), (df2['tags'] == 'Москва'), (df2['tags'] == 'Северный Кавказ'), (df2['tags'] == 'Космос'), (df2['tags'] == 'Биографии и справки'),
(df2['tags'] == 'Военная операция на Украине'), (df2['tags'] == 'Мир'), (df2['tags'] == 'Забота о себе'), (df2['tags'] == 'Россия'), (df2['tags'] == 'Путешествия'), (df2['tags'] == 'Ценности'), (df2['tags'] == 'Бывший СССР'), (df2['tags'] == 'Интернет и СМИ'),
(df2['tags'] == 'Силовые структуры'), (df2['tags'] == 'Наука и техника'), (df2['tags'] == 'Из жизни'), (df2['tags'] == 'Моя страна'), (df2['tags'] == 'Национальные проекты'), (df2['tags'] == 'Новости партнеров'), (df2['tags'] == 'Новости регионов'), (df2['tags'] == '69-я параллель')]

choices = ['Политика', 'Общество', 'Экономика', 'Экономика', 'Экономика', 'Медиа и СМИ', 'Технологии', 'Политика', 'Политика', 'Технологии', 'Общество', 'Экономика', 'Экономика', 'Технологии', 'Общество', 'Общество', 'Экономика', 'Политика', 'Спорт и здоровье', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Технологии', 'Общество', 'Россия и бывший СССР', 'Общество', 'Общество', 'Россия и бывший СССР', 'Спорт и здоровье', 'Общество', 'Россия и бывший СССР', 'Медиа и СМИ', 'Общество', 'Технологии', 'Общество', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Медиа и СМИ', 'Россия и бывший СССР', 'Россия и бывший СССР']

df2['tags'] = np.select(conditions, choices, default='Разное')

conditions1 = [(df2['tags'] == 'Политика'), (df2['tags'] == 'Общество'), (df2['tags'] == 'Экономика'), (df2['tags'] == 'Медиа и СМИ'), (df2['tags'] == 'Технологии'), (df2['tags'] == 'Спорт и здоровье'), (df2['tags'] == 'Россия и бывший СССР'),
(df2['tags'] == 'Спорт и здоровье')]
choices1 = [1,2,3,4,5,6,7,8]
df2['category_id'] = np.select(conditions1, choices1, default=0)


client = clickhouse_connect.get_client(host='localhost', username='default', password='')

ph.to_clickhouse(df2, 'vedomostiRSS', index=False, chunksize=100000, connection=connection)


import numpy as np

client = clickhouse_connect.get_client(host='localhost', username='default', password='')

connection = dict(database='default',
                  host='http://localhost:8123',
                  user='default',
                  password='')
client = clickhouse_connect.get_client(host='localhost', username='default', password='')
client.command('CREATE TABLE IF NOT EXISTS all_news (title String, link String,tags String, published String) ENGINE MergeTree ORDER BY published')
client.command('CREATE TABLE IF NOT EXISTS all_categories (category_id Int32, category_name String, tags String) ENGINE MergeTree ORDER BY category_id')

data_list1 = client.command('Select published from vedomostiRSS  ')
data_list2 = client.command('Select published from tassRSS')
data_list3 = client.command('Select published from lentaRSS')
data_list4 = data_list1 + '\n' +  data_list2 + '\n' + data_list3
#df = pd.read_table(data_list4)
df = pd.DataFrame([x.split(';') for x in data_list4.split('\n')])
df = df.rename(columns={0:'tags'})


conditions = [(df['tags'] == 'Политика') , (df['tags'] == 'Общество'), (df['tags'] == 'Бизнес'), (df['tags'] == 'Экономика'), (df['tags'] == 'Финансы'), (df['tags'] == 'Медиа'), (df['tags'] == 'Авто'), (df['tags'] == 'Политика / Власть'), 
(df['tags'] == 'Политика / Международные отношения'), (df['tags'] == 'Технологии'), (df['tags'] == 'Среда обитания'), (df['tags'] == 'Недвижимость'), (df['tags'] == 'Экономика и бизнес'), (df['tags'] == 'Армия и ОПК'), (df['tags'] == 'Происшествия'),
(df['tags'] == 'Культура'), (df['tags'] == 'НедвижимостьОбщество'), (df['tags'] == 'Международная панорама'), (df['tags'] == 'Спорт'), (df['tags'] == 'Москва'), (df['tags'] == 'Северный Кавказ'), (df['tags'] == 'Космос'), (df['tags'] == 'Биографии и справки'),
(df['tags'] == 'Военная операция на Украине'), (df['tags'] == 'Мир'), (df['tags'] == 'Забота о себе'), (df['tags'] == 'Россия'), (df['tags'] == 'Путешествия'), (df['tags'] == 'Ценности'), (df['tags'] == 'Бывший СССР'), (df['tags'] == 'Интернет и СМИ'),
(df['tags'] == 'Силовые структуры'), (df['tags'] == 'Наука и техника'), (df['tags'] == 'Из жизни'), (df['tags'] == 'Моя страна'), (df['tags'] == 'Национальные проекты'), (df['tags'] == 'Новости партнеров'), (df['tags'] == 'Новости регионов'), (df['tags'] == '69-я параллель')]

choices = ['Политика', 'Общество', 'Экономика', 'Экономика', 'Экономика', 'Медиа и СМИ', 'Технологии', 'Политика', 'Политика', 'Технологии', 'Общество', 'Экономика', 'Экономика', 'Технологии', 'Общество', 'Общество', 'Экономика', 'Политика', 'Спорт и здоровье', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Технологии', 'Общество', 'Россия и бывший СССР', 'Общество', 'Общество', 'Россия и бывший СССР', 'Спорт и здоровье', 'Общество', 'Россия и бывший СССР', 'Медиа и СМИ', 'Общество', 'Технологии', 'Общество', 
'Россия и бывший СССР', 'Россия и бывший СССР', 'Медиа и СМИ', 'Россия и бывший СССР', 'Россия и бывший СССР']

df['category'] = np.select(conditions, choices, default='Разное')

conditions1 = [(df['category'] == 'Политика'), (df['category'] == 'Общество'), (df['category'] == 'Экономика'), (df['category'] == 'Медиа и СМИ'), (df['category'] == 'Технологии'), (df['category'] == 'Спорт и здоровье'), (df['category'] == 'Россия и бывший СССР'),
(df['category'] == 'Спорт и здоровье')]
choices1 = [1,2,3,4,5,6,7,8]
df['category_id'] = np.select(conditions1, choices1, default=0)

#df['category'] = np.where(((df['category']=='Экономика') | (df['category']=='Бизнес') 
#                           | (df['category']=='Финансы') | (df['category']=='Бизнес / Транспорт')),
#                          'Экономика и бизнес', df['category'])

#df['category','category_id'] = np.where()
#df.index.names = ['Category_id']


#pd.DataFrame(data_list1, columns=["category_id", "category_name", "tags"])

#client.command('INSERT INTO `default`.all_categories (category_name, tags) VALUES(sport String, sport String)')
#client.command('ALTER TABLE default.all_categories UPDATE (category_id, category_name) VALUES("sport","sport")')

#client.query('select tags from all_categories where tags = "Политика"')
#client.command('INSERT INTO default.all_categories (category_id, category_name) VALUES (1, "Общество") select category_id, Category_name, tags from all_categories WHERE tags IS Общество')
#print(data_list4['published'].dt.day_name())
