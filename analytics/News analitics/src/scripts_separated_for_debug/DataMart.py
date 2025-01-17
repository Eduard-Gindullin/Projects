import pandahouse as ph
import clickhouse_connect
import pandas as pd
import clickhouse2pandas as ch2pd

connection_url = 'http://default:@192.168.3.18:8123'
query1 = 'select * from vedomostiRSS limit 10000'
query2 = 'select * from lentaRSS limit 10000'
query3 = 'select * from tassRSS limit 10000'


df1= ch2pd.select(connection_url, query1)
df2= ch2pd.select(connection_url, query2)
df3= ch2pd.select(connection_url, query3)


df4 = pd.merge(df1,df2, how='outer')
df5 = pd.merge(df4,df3, how='outer')

# Общее количество новостей по категории Общество за все время со всех источников
total_category_count = df5['category_id'].value_counts()[2]

# Общее количество новостей по категории Общество за все время с источника Ведомости
total_category_count_vedomosti = df1['category_id'].value_counts()[2]

# Общее количество новостей по категории Общество за все время с источника Лента
total_category_count_lenta = df2['category_id'].value_counts()[2]

# Общее количество новостей по категории Общество за все время с источника Тасс
total_category_count_tass = df3['category_id'].value_counts()[2]

# Выводим количество публикаций по категории Общество за последнии сутки с источника Ведомости
day_category_count_vedomosti= df1[(df1['published'] < df1['published'].values.max()) & (df1['published'] > (df1['published'].values.max() - pd.DateOffset(days=1)) )]['category_id'].value_counts()[2]

# Выводим количество публикаций по категории Общество за последнии сутки с источника Лента
day_category_count_lenta= df2[(df2['published'] < df2['published'].values.max()) & (df2['published'] > (df2['published'].values.max() - pd.DateOffset(days=1)) )]['category_id'].value_counts()[2]

# Выводим количество публикаций по категории Общество за последнии сутки с источника Тасс
day_category_count_tass= df3[(df3['published'] < df3['published'].values.max()) & (df3['published'] > (df3['published'].values.max() - pd.DateOffset(days=1)) )]['category_id'].value_counts()[2]

# Выводим среднее количество публикаций по категории Общество в сутки
total_category_count_byDay = df5[df5['category_id'] == 2]["published"].dt.date.value_counts().tolist()
mean_category_daily = sum(total_category_count_byDay)/len(total_category_count_byDay)

# Выведем день в который было максимально колличество публикаций по категории Общество
max_category_count_day = df5[df5['category_id'] == 2]["published"].dt.date.value_counts().nlargest(1).index[0]

# Количество публикаций по теме Общество по дням недели
category_count_byWeekDay = df5[df5['category_id'] == 2]["published"].dt.day_name().value_counts()

# Создаем витрину
variables = {'category_id':2,
             'tags':'Общество',
             'total_category_count':total_category_count,
             'total_category_count_vedomosti':total_category_count_vedomosti,
             'total_category_count_lenta':total_category_count_lenta,
             'total_category_count_tass':total_category_count_tass,
             'day_category_count_vedomosti':day_category_count_vedomosti,
             'day_category_count_lenta':day_category_count_lenta,
             'day_category_count_tass':day_category_count_tass,
             'mean_category_daily':mean_category_daily,
             'max_category_count_day':max_category_count_day,
             'category_count_Monday':category_count_byWeekDay['Monday'],
             'category_count_Tuesday':category_count_byWeekDay['Tuesday'],
             'category_count_Wednesday':category_count_byWeekDay['Wednesday'],
             'category_count_Thursday':category_count_byWeekDay['Thursday'],
             'category_count_Friday':category_count_byWeekDay['Friday'],
             'category_count_Saturday':category_count_byWeekDay['Saturday'],
             'category_count_Sunday':category_count_byWeekDay['Sunday']}

DataMart = pd.DataFrame(variables).T
DataMart.set_index('category_id', inplace=True)
# DataMart = DataMart.T
# t = DataMart.index.tolist()
# Создадим табличку в БД и запишем наши данные
# client = clickhouse_connect.get_client(host='192.168.3.18', username='default', password='')
# client.command('CREATE TABLE IF NOT EXISTS DataMart (t String, link String,tags String, category_id Int32, published DateTime) ENGINE MergeTree ORDER BY title')
# connection = dict(database='default',
#                   host='http://192.168.3.18:8123',
#                   user='default',
#                   password='')
# ph.to_clickhouse(DataMart, 'DataMart', index=True, chunksize=100000, connection=connection)
#сли были дубликаты - удаляем
# client.command('OPTIMIZE TABLE DataMart FINAL DEDUPLICATE') columns.tolist() .columns.tolist()
print(DataMart)