# Send notify to Telegram bot
def bot_sendtext(bot_message):
    bot_message = urllib.parse.quote(bot_message)
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text, proxies=proxies, headers=headers)
    print(send_text)

# Check, read articles
def read_article_feed(feed):
    """ Get articles from RSS feed """
    feedparser.USER_AGENT = ua
    feed = feedparser.parse(feed)
    print(feed)
    for article in feed['entries']:
        if article_is_not_db(article['title'], article['published']):
            add_article_to_db(article['title'], article['published'])
            bot_sendtext('New feed found ' + article['title'] +', ' + article['link'] + ', ' + article['description'])
            print(article)

# Rotate feeds array
def spin_feds():
    for x in myfeeds:
        print(x)
        read_article_feed(x)

# Runner :)
if __name__ == '__main__':
    spin_feds()
    # get_posts()
    db_connection.close()