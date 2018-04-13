import json
import os
import requests
import threading
import time
from flask import Flask, request, jsonify, make_response
app = Flask(__name__)

import apilib

COINS_DATA = []


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.before_first_request
def activate_repeating_job():
	# res = requests.get('https://min-api.cryptocompare.com/data/all/coinlist').json()
	# print(res)
	def get_coins_data():
		while True:
			try:
				resA = requests.get('https://min-api.cryptocompare.com/data/all/coinlist').json()
				resB = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=0').json()
				global COINS_DATA
				COINS_DATA = apilib.parse_allcoins(resA, resB)
				print(len(COINS_DATA))
			except Exception as e:
				raise e

			time.sleep(86400)

	thread = threading.Thread(target=get_coins_data)
	thread.start()



@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/coins', methods=['GET'])
def get_coins():
	start = request.args.get('rank.gte', default = 1, type = int)
	end = request.args.get('rank.lte', default = 0, type = int)
	query = request.args.get('query', default = '', type = str)
	limit = request.args.get('limits', default = 10, type = int)

	result = apilib.get_coins(COINS_DATA, start, end, query, limit)

	print(result)
	return jsonify(result)

@app.route('/coins/coin/<int:id>', methods=['GET'])
def get_coinby_id(id):
	global COINS_DATA
	result = apilib.get_coinby_id(COINS_DATA, id)

	if result is None:
		result = { 'error' : 'Coin not found for given id'}


	print(result)
	return jsonify(result)

@app.route('/coins/coin/<symbol>', methods=['GET'])
def get_coinby_symbol(symbol):
	global COINS_DATA
	result = apilib.get_coinby_symbol(COINS_DATA, symbol)

	if result is None:
		result = { 'error' : 'Coin not found for given symbol'}

	print(result)
	return jsonify(result)


@app.route('/coins/coin/price/<symbol>', methods=['GET'])
def get_coin_price(symbol):
	convert = request.args.get('convert', default = "USD", type = str)

	global COINS_DATA
	coin = apilib.get_coinby_symbol(COINS_DATA, symbol.upper())

	if coin is None or not ('name' in coin.keys()):
		result = { 'error' : 'Coin not found for given symbol'}
		return jsonify(result)
	
	res = requests.get('https://api.coinmarketcap.com/v1/ticker/' + coin['name'] + '?convert=' + convert).json()[0]

	result = apilib.parse_priceresult(res, convert)
	print(result)
	return jsonify(result)


@app.route('/convert/list', methods=['GET'])
def get_convert_list():
	converts = [
	"AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR",
	"GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN",
	"MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD",
	"THB", "TRY", "TWD", "ZAR", "BTC", "USD"
	]

	return jsonify(converts)
	

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)

"""
@app.route('/addimg', methods=['POST'])
def add_img():
	if not 'token' in request.args:
		return jsonify({ 'error' : 'Missing argument' })

	token = request.args['token']

	if 'image' not in request.files:
		print('No file part')
		return jsonify({ 'error': 'Not found \'image\' argument'})

	file = request.files['image']

	if file.filename == '':
		return jsonify({ 'error': 'No selected file'})

	if file and allowed_file(file.filename):
		f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
		file.save(f)
		return jsonify(apilib.add_img(token, file.filename))

	return jsonify({ 'error': 'Invalid file'})

"""
