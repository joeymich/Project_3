import time
from termcolor import colored
import pickle
import pandas as pd


from redblacktree import RedBlackTree
from hashtable import HashTable


# continue to take input until valid option is selected
def selectChoice(selections):
    while True:
        userChoice = input("> ")
        for item in selections:
            for selectionTag in selections[item]:
                if userChoice.lower().strip() == selectionTag:
                    return item


# decorator that prints time for function to run - https://www.geeksforgeeks.org/timing-functions-with-decorators-python/
def timeFunc(func):
    def wrapFunc(*args, **kwargs):
        t1 = time.time_ns()
        result = func(*args, **kwargs)
        t2 = time.time_ns()
        # '!r adds quotations'
        print(f'{func.__name__!r} excuted in {t2 - t1}ns')
        return result
    return wrapFunc


def loadGroupedData():
    # data grouped by date
    with open('grouped.pkl', 'rb') as f:
        return pickle.load(f)


def loadUngroupedData():
    # data not grouped by date, (ex. index = 2022-01-03AAPL)
    return pd.read_pickle('ungrouped.pkl')


def printValidTickers():
    # prints stock tickers in database
    print(colored('Valid Tickers', 'green'))
    df = loadUngroupedData()
    print(df.stock_id.unique())


def printValidDates():
    # prints dates in database
    print(colored('Valid Dates', 'green'))
    df = loadUngroupedData()
    print(df.t.unique())


def buildStructures():
    # calls functions to build red black tree and hash table
    data = loadGroupedData()
    return buildRedBlackTree(data), buildHashTable(data)


@timeFunc
def buildRedBlackTree(data):
    # insert all items into redblack tree
    tree = RedBlackTree()
    for key, value in data.items():
        tree.insert(key, value)
    return tree


@timeFunc
def buildHashTable(data):
    # insert all items into hash table
    hashTable = HashTable()
    for key, value in data.items():
        hashTable.insert(key, value)
    return hashTable


@timeFunc
def search(structure, date, ticker):
    # searches for given date and ticker in selected data structure
    result = structure.find(date)
    if result:
        # checks for selected stock ticker within date node
        # if it does not exist, returns None
        return next((row for row in result if row['stock_id'] == ticker), None)
    return None


def searchmenu():
    print(colored('\nSearch', 'blue'))

    print('What S&P 500 stock ticker are you searching for? (ex. AAPL)')
    ticker = input('> ')
    print('\nWhat date are you searching for? (YYYY-MM-DD)')
    date = input('> ')

    print('\nWhat data structure to search with?')
    print('0: Hash Table\n1: Red Black Tree')

    selections = {
        0: ['0', 'hash table'],
        1: ['1', 'red black tree']
    }

    selection = selectChoice(selections)

    if selection == 0:
        dataStructure = 'Hash Table'
    elif selection == 1:
        dataStructure = 'Red Black Tree'

    print(
        colored(f'\nSearching for {ticker} on {date} in {dataStructure}', 'blue'))
    result = search([hashTable, redBlackTree][selection], date, ticker)
    if result:
        print(f'Stock Ticker: {result["stock_id"]}')
        print(f'Data: {result["t"]}')
        print(f'Open: ${result["o"]}')
        print(f'High: ${result["h"]}')
        print(f'Low: ${result["l"]}')
        print(f'Close: ${result["c"]}')
        print(f'Volume: {result["v"]}')
    else:
        print('stock ticker or date is invalid')


hashTable = None
redBlackTree = None


def mainmenu():
    global hashTable, redBlackTree
    print(colored('\nMain Menu', 'yellow'))
    print('0: Build Red Black Tree and Hash Table')
    print('1: Print Valid Stock Tickers')
    print('2: Print Valid Dates')
    print('3: Search')
    print('4: Exit')

    selections = {
        0: ['0'],
        1: ['1'],
        2: ['2'],
        3: ['3', 'search'],
        4: ['4', 'exit']
    }

    selection = selectChoice(selections)

    if selection == 0:
        redBlackTree, hashTable = buildStructures()
        mainmenu()
    elif selection == 1:
        printValidTickers()
        mainmenu()
    elif selection == 2:
        printValidDates()
        mainmenu()
    elif selection == 3:
        searchmenu()
        mainmenu()


if __name__ == '__main__':
    mainmenu()
