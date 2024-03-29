import sqlite3

import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}


def get_stock_list():
    main_url = 'https://kabuoji3.com/stock/'
    page_url = 'https://kabuoji3.com/stock/?page={}'
    main_page = requests.get(main_url, headers=headers)
    main_page_soup = BeautifulSoup(main_page.text, 'lxml')
    page_nums = []

    for a in main_page_soup.find('ul', {'class': 'pager'}).find_all('a'):
        page_nums.append(a.text)

    stock_list = []

    for page_num in page_nums:
        url = page_url.format(page_num)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text)
        tr_list = soup.find('table', {'class': 'stock_table'}).find_all('tr')

        for tr in tr_list[1:]:
            link = tr.get('data-href')
            td_list = tr.find_all('td')
            stock_num, stock_name = td_list[0].a.text.split(' ', 1)
            stock_market = td_list[1].text
            stock_list.append([stock_num, stock_name, stock_market, link])

    return stock_list


def get_stock_data(**kwargs):
    url = kwargs.get('url')
    name = kwargs.get('name')
    number = kwargs.get('number')
    market = kwargs.get('market')
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text)
    tables = soup.find_all('table', {'class': 'stock_table'})
    data_list = []

    for table in tables:
        for row in table.find_all('tr')[1:]:
            td_list = row.find_all('td')
            data = [number, name, market]
            data.extend([td.text for td in td_list])
            data.pop(-1)
            data_list.append(data)

    return data_list


def insert_stock_list(data):
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS stocks")
    c.execute('''CREATE TABLE stocks
            (number text, name text, market text, url text)''')
    c.executemany('INSERT INTO stocks VALUES (?,?,?,?)', data)
    conn.commit()
    conn.close()


def insert_daily_data(data, conn):
    # conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS daily")
    c.execute('''CREATE TABLE daily
                (number text, date timestamp, open integer, high integer, low integer, close integer, volume integer)''')
    c.executemany('INSERT INTO daily VALUES (?,?,?,?,?,?,?)', data)
    conn.commit()



def get_high_low_rate(first=None, last=None, top=None, bottom=None):

    # if went up
    if first < last:
        if last == top:
            high_gap = 0
        else:
            high_gap = top - last
        low_gap = first - bottom
    # if went down
    elif first > last:
        high_gap = top - first
        if last == bottom:
            low_gap = 0
        else:
            low_gap = bottom - last
    # if no movement
    else:
        high_gap = top - last
        low_gap = last - bottom

    high_rate = high_gap / last * 100
    low_rate = low_gap / last * 100

    return high_rate, low_rate

