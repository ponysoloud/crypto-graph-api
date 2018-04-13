import json
import os
import requests
from math import radians, cos, sin, asin, sqrt
from requests.exceptions import HTTPError

UPLOAD_FOLDER = 'cache'

class Coin:

	def __init__(self, json):
		self.symbol = json['Name'].lower()
		self.name = json['id']
		self.fullname = json['name']

		try:
			self.id = int(json['Id'])
		except:
			self.id = -1

		try:
			self.rank = int(json['rank'])
		except:
			self.rank = -1
		
		if 'ImageUrl' in json:
			self.img_url = "https://www.cryptocompare.com" + json['ImageUrl']
		else:
			self.img_url = ""

	def json(self): 
		return {
		'symbol'  : self.symbol,
		'id'      : self.id,
		'name'    : self.name,
		'fullname': self.fullname,
		'rank'    : self.rank,
		'img_url' : self.img_url
		}



def parse_allcoins(dataA, dataB):
	if not os.path.exists(UPLOAD_FOLDER):
		os.makedirs(UPLOAD_FOLDER)

	coinsdata = dataA['Data']

	coinsdict_list = []

	for coinjson in dataB:
		symbol = coinjson['symbol']
		if symbol in coinsdata.keys():
			cjson = coinjson
			cjson.update(coinsdata[symbol])

			coinsdict_list.append(cjson)

	with open('cache/coins.txt', 'w+') as outfile:
		json.dump(coinsdict_list, outfile)

	coinsres = [Coin(value) for value in coinsdict_list]

	return coinsres


# Flask requests implementation methods

def get_coins(coins, start, end, query, limit):
	if end == 0:
		ends = len(coins)
	else:
		ends = end

	res = []
	for coin in coins:
		if (start <= coin.rank <= ends) and ((query.lower() in coin.name) or (query.lower() in coin.symbol)):
			res.append(coin)
		if len(res) == limit:
			break

	res.sort(key=lambda x: x.rank)

	json = [coin.json() for coin in res]

	return json


def get_coinby_id(coins, id):
	res = [coin for coin in coins if coin.id == id]
	json = [coin.json() for coin in res]

	result = {}
	if len(json) > 0:
		result = json[0]
	else:
		result = None

	return result


def get_coinby_symbol(coins, symbol):
	res = [coin for coin in coins if coin.symbol == symbol.lower()]
	json = [coin.json() for coin in res]

	result = {}
	if len(json) > 0:
		result = json[0]
	else:
		result = None

	return result

def parse_priceresult(result, convert):
	converts = ["usd", "btc"]
	if not (convert.lower() in converts):
		converts.append(convert.lower())

	pricesconverts = [('price_' + conv) for conv in converts]

	temp = result.copy()
	prices = []
	for key, value in result.items():
		for c in pricesconverts:
			if key.endswith(c):
				prices.append({ 
					'convert' : key[-3:].upper(),
					'value' : value 
					})
				del temp[key]

	temp['prices'] = prices
	return temp


