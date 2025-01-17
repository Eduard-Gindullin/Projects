# Imports
#import sqlite3
import requests
import feedparser
import os
import urllib
import random
import clickhouse_connect


# Feeds
myfeeds = [
  'https://www.vedomosti.ru/rss/news',
]

# User agents
uags = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]

# Random User Agent (from uags list)
ua = random.choice(uags)

# Header
headers = {
  "Connection" : "close",  # another way to cover tracks
  "User-Agent" : ua
}

# Proxies
proxies = {
}

# DB


client = clickhouse_connect.get_client(host='localhost', username='default', password='')
client.command('CREATE TABLE IF NOT EXISTS vedomosti (title String, date String) ENGINE MergeTree ORDER BY title')
#scriptDir = os.path.dirname(os.path.realpath(__file__))
#db_connection = sqlite3.connect(scriptDir + '/rss.sqlite')
#db = client.cursor()
#db.execute('CREATE TABLE IF NOT EXISTS vedomosti (title TEXT, date TEXT)')

# Get posts from DB and print
def get_posts():
    with client:
        print(client.command("SELECT * FROM vedomosti"))