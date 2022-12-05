import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import config
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import pickle

from hashtable import HashTable
from redblacktree import RedBlackTree


def create_tables():
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            name TEXT NOT NULL,
            primary_exchange TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_price (
            id INTEGER PRIMARY KEY,
            stock_id INTEGER,
            t NOT NULL,
            o NOT NULL,
            h NOT NULL,
            l NOT NULL,
            c NOT NULL,
            v BIGINT UNSIGNED NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES stock (id)
        )
    ''')

    connection.commit()


def drop_tables():
    connection = sqlite3.connect(config.DB_FILE)

    cursor = connection.cursor()

    cursor.execute('''
        SELECT name FROM sqlite_schema
        WHERE type='table'
        ORDER BY name;
    ''')

    tables = cursor.fetchall()

    for table in tables:
        table = table[0]
        query = f'DROP TABLE IF EXISTS {table}'
        cursor.execute(query)

    connection.commit()


def fill_stock(tickers):

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)

    for ticker in tickers:
        try:
            asset = api.get_asset(ticker)
            cursor.execute('''
                INSERT INTO stock (ticker, primary_exchange, name)
                VALUES (?, ?, ?)
            ''', (ticker, asset.exchange, asset.name))
            print(f'Added ticker {ticker} to database')
        except:
            print(f'failed ticker {ticker}')

    connection.commit()


def fill_stock_price():

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute('''
        SELECT id, ticker FROM stock
    ''')

    rows = cursor.fetchall()

    stock_dict = {}
    for row in rows:
        stock_dict[row['ticker']] = row['id']

    api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)

    symbols = list(stock_dict.keys())
    chunk_size = 200
    for i in range(0, len(symbols), chunk_size):
        symbol_chunk = symbols[i:i+chunk_size]
        df = api.get_bars(symbol_chunk, TimeFrame.Day, '2022-01-01', '2022-11-30').df
        symbols_check = []
        for index, row in df.iterrows():
            ticker = row.symbol
            if ticker not in symbols_check:
                symbols_check.append(ticker)
                print(f'adding data for ticker {ticker}')
            stock_id = stock_dict[ticker]
            query = '''
                INSERT INTO stock_price (stock_id, t, o, h, l, c, v)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            values = (stock_id, index.date(), row.open, row.high, row.low, row.close, row.volume)
            cursor.execute(query, values)

    connection.commit()


def load_tickers():
    df = pd.read_pickle('sp500.pkl')
    return list(df.Ticker)


def print_num_rows():
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    cursor.execute('''
        SELECT COUNT(*) FROM stock_price
    ''')

    count = cursor.fetchone()[0]

    print(f'numRows: {count}')


def scrape_tickers():
    r = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(r.text)

    table = soup.select_one('table')

    tickers = []
    for row in table.tbody.find_all('tr'):
        columns = row.find_all('td')
        if columns != []:
            ticker = columns[0].text.strip()
            tickers.append(ticker)

    df = pd.DataFrame(tickers, columns=['Ticker'])
    print(df)
    df.to_pickle('sp500.pkl')


def time_func(func):
    def wrap_func(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(f'{func.__name__!r} excuted in {(t2-t1)*1000:.4f}ms') # '!r adds quations'
        return result
    return wrap_func


def prep_grouped_data():
    connection = sqlite3.connect(config.DB_FILE)

    query = 'SELECT stock_id, t, o, h, l, c, v FROM stock_price'

    df = pd.read_sql_query(query, connection)

    cursor = connection.cursor()

    cursor.execute('SELECT id, ticker FROM stock')
    stock_id_map = {}
    for row in cursor.fetchall():
        stock_id_map[row[0]] = row[1]
    df = df.replace({'stock_id': stock_id_map})

    data = dict(tuple(df.groupby('t')))
    for key, value in data.items():
        data[key] = value.to_dict('records')

    with open('grouped.pkl', 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    return data


def prep_ungrouped_data():
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    query = 'SELECT stock_id, t, o, h, l, c, v FROM stock_price'
    df = pd.read_sql_query(query, connection)

    cursor.execute('SELECT id, ticker FROM stock')
    stock_id_map = {}
    for row in cursor.fetchall():
        stock_id_map[row[0]] = row[1]
    df = df.replace({'stock_id': stock_id_map})

    df['id'] = df['t'] + df['stock_id']
    df = df.set_index('id')

    df.to_pickle('ungrouped.pkl')

    return df


@time_func
def make_redblacktree2(df):
    tree = RedBlackTree()
    for index, row in df.iterrows():
        tree.insert(index, row.to_dict())
    return tree


@time_func
def redblacktree_lookup2(tree, date, ticker):
    result = tree.find(date + ticker)
    return result


def get_ungrouped_data():
    return pd.read_pickle('ungrouped.pkl')


def get_grouped_data():
    with open('grouped.pkl', 'rb') as f:
        return pickle.load(f)


if __name__ == '__main__':
    # drop_tables()
    # create_tables()
    # scrape_tickers()
    # tickers = load_tickers()
    # fill_stock(tickers)
    # fill_stock_price()
    # print_num_rows()
    # prep_grouped_data()
    # prep_ungrouped_data()
    df = pd.read_pickle('ungrouped.pkl')

    @time_func
    def makeHashTable():
        hashTable = HashTable()
        for index, row in df.iterrows():
            hashTable.insert(index, row)
        return hashTable

    hashTable = makeHashTable()
    print(hashTable.find('2022-01-03'+'AAPL'))

