# Imports
#import sqlite3
import requests
import feedparser
import pandahouse as ph
import random
import clickhouse_connect
import pandas as pd
import numpy as np


# DB




d = feedparser.parse('https://www.vedomosti.ru/rss/news')
d['feed']['title']
print(d.feed)
data_list = []

for i in d["entries"]:
     data_list.append([i["title"],i["link"],i["tags"],i["published"]])
      

df = pd.DataFrame(data_list, columns=["title","link","tags","published"])
 
