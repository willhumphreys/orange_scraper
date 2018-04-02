import datetime
import logging
import sys
import uuid
from decimal import Decimal
from urllib.request import urlopen

import boto3
import requests
from bs4 import BeautifulSoup

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

symbol_prices = None
db_table = None


def persist_to_dynamodb(sentiments):
    fixed_symbol = sentiments['symbol'].replace('/', '')

    symbol_price_list = list(filter(lambda x: x['symbol'] == fixed_symbol, symbol_prices))

    if len(symbol_price_list) == 1:
        item_id = str(uuid.uuid4())
        symbol_price = symbol_price_list[0]
        print(symbol_price)
        bid = round(Decimal(symbol_price['bid']), 3)
        offer = round(Decimal(symbol_price['ask']), 3)
        symbol = sentiments['symbol'].replace('/', '-').lower()
        provider = 'oanda'
        long_percentage = sentiments['long_percentage']
        short_percentage = sentiments['short_percentage']

        long_percentage = convert_percentage(long_percentage, short_percentage)
        short_percentage = convert_percentage(short_percentage, long_percentage)

        date_time = datetime.datetime.now().isoformat()

        table = dynamodb.Table(db_table)

        item = {'id': item_id,
                'symbol': symbol,
                'dateTime': date_time,
                'longPercentage': long_percentage,
                'shortPercentage': short_percentage,
                'bid': bid,
                'offer': offer,
                'provider': provider}

        table.put_item(Item=item)
        return item


def convert_percentage(percentage, other_percentage):
    if not percentage:
        return round(Decimal(100 - float(other_percentage)), 3)
    else:
        return round(Decimal(float(percentage)), 3)


def my_handler(event, context):
    forge_api_key = event['forge_api_key']
    data_url = event['data_url']

    global db_table
    db_table = event['db_table']

    logger.info('Using forge key {} and data url {}'.format(forge_api_key, data_url))

    mapped_sentiments = scrap_sentiments(data_url)

    symbol_list = list(map(lambda x: x['symbol'].replace('/', ''), mapped_sentiments))
    symbols_string = ",".join(symbol_list)

    current_prices = 'https://forex.1forge.com/1.0.3/quotes?pairs={}&api_key={}'.format(
        symbols_string, forge_api_key)

    response = requests.get(current_prices)

    global symbol_prices
    symbol_prices = response.json()

    print(symbol_prices)

    persisted_items = list(map(persist_to_dynamodb, mapped_sentiments))

    return {
        'persisted_items': persisted_items
    }


def scrap_sentiments(data_url):
    page = urlopen(data_url)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.findAll('ol', attrs={'class': 'position-ratio-list'})
    all_sentiment_html = name_box[0]
    sentiment_lines = all_sentiment_html.find_all("li")
    mapped_sentiments = list(map(map_to_symbols, sentiment_lines))
    return mapped_sentiments


def map_to_symbols(x):
    symbol = x['name']

    logger.info('processing %s', symbol)

    long_percentage = x.find('span', attrs={'class': 'long-position'}).text.strip().replace('%', '')
    short_percentage = x.find('span', attrs={'class': 'short-position'}).text.strip().replace('%', '')

    return {'symbol': symbol, 'long_percentage': long_percentage, 'short_percentage': short_percentage}
