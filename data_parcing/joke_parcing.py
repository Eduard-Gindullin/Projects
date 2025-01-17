import requests
import random
from bs4 import BeautifulSoup

def get_random_number(start = 1, end = 50):
    return random.randint(start, end)

def fetch_joke(page_number):
    url = f"https://www.anekdot.ru/release/anekdot/year/2024/{page_number}"
    response =requests.get(url)
    return response.text

def get_joke(html):
    soup = BeautifulSoup(html, "lxml")
    joke = soup.find_all("div", class_="text")
    i = random.randint(1, 50)
    return joke[i].getText()

def main():
    joke_number = get_random_number()
    html = fetch_joke(joke_number)
    joke = get_joke(html)
    print(joke)

main()