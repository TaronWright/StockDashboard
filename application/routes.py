from application import application
from flask import render_template, jsonify, request, make_response, abort
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os 
import time
# import concurrent.futures
import requests


# load the .env file
load_dotenv()
# get the aplha vantage api key from the .env file
av_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

#read the stock tickers csv file
yh_sym = pd.read_csv("application/static/flat-ui__data.csv")
symbols = yh_sym[['Symbol', "Security"]]

crypto = pd.read_csv("application/static/CryptocurrencyData.csv")
crypto_coins = crypto[['Coin Name',"Symbol"]]


@application.route("/home",methods=["GET"])
def home():
    start = time.perf_counter()
    ticker_dict = {"Ticker": [],
                 "Change": [],
                 "Price": [],
                 "Volume": [],
                 "Float": [],
                 "MCAP": []
                 }
    for symbol in symbols['Symbol']:
        try:
            ticker = yf.Ticker(symbol)
            ticker_info = ticker.info
            ticker_dict['Volume'].append(ticker_info['volume'])
            ticker_dict['Price'].append(ticker_info['currentPrice'])
            ticker_dict['MCAP'].append(ticker_info['marketCap'])
            ticker_dict['Float'].append(ticker_info['floatShares'])
            percent_change = ((ticker_info['currentPrice']-ticker_info['open'])/ticker_info['open'])*100
            ticker_dict['Change'].append(percent_change)
            ticker_dict['Ticker'].append(symbol)
        except:
            print(f"Info could not be found for {symbol}")

    end = time.perf_counter()

    print(f"It took {end-start}s to run the block of code!")    
    ticker_dict = pd.DataFrame(ticker_dict)
    ticker_dict = ticker_dict.to_dict(orient="records")
    return render_template("home.html", ticker_dict = ticker_dict)

# def fetch_ticker_info(symbol):
#     try:
#         ticker = yf.Ticker(symbol)
#         ticker_info = ticker.info
#         percent_change = ((ticker_info['currentPrice'] - ticker_info['open']) / ticker_info['open']) * 100
#         return {
#             "Ticker": symbol,
#             "Change": percent_change,
#             "Price": ticker_info.get('currentPrice'),
#             "Volume": ticker_info.get('volume'),
#             "Float": ticker_info.get('floatShares'),
#             "MCAP": ticker_info.get('marketCap')
#         }
#     except Exception as e:
#         print(f"Info could not be found for {symbol}: {e}")
#         return None

# @application.route("/home", methods=["GET"])
# def home():
#     ticker_dict = {"Ticker": [], "Change": [], "Price": [], "Volume": [], "Float": [], "MCAP": []}

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = [executor.submit(fetch_ticker_info, symbol) for symbol in symbols['Symbol']]
#         for future in concurrent.futures.as_completed(futures):
#             result = future.result()
#             if result:
#                 ticker_dict["Ticker"].append(result["Ticker"])
#                 ticker_dict["Change"].append(result["Change"])
#                 ticker_dict["Price"].append(result["Price"])
#                 ticker_dict["Volume"].append(result["Volume"])
#                 ticker_dict["Float"].append(result["Float"])
#                 ticker_dict["MCAP"].append(result["MCAP"])

#     ticker_df = pd.DataFrame(ticker_dict)
#     ticker_dict = ticker_df.to_dict(orient="records")
#     return render_template("home.html", ticker_dict=ticker_dict)

@application.route("/")
def index():
    stock_symbols = symbols.to_dict(orient="records")
    return render_template("stock.html", symbols=stock_symbols)


@application.route("/stock",methods=["POST","GET"])
def stock():
    stock = request.get_json()
    symbol = stock["Symbol"]
    
    if symbol == '':
        print("Aborted!")
        abort(500)
    period = stock['Period']
    print(period)
    interval = "1d"
    match period:
        case "1y":
            interval = "1wk"
        case "6mo":
            interval = "1d"
        case "3mo":
            interval = "1d"
        case "1mo":
            interval = "1h"
        case "5d":
            interval = "1h"
        case "1d":
            interval = "5m"

    print(interval)
    

    ticker = yf.Ticker(symbol)

    # candlestick_data is a pandas dataframe
    candlestick_data = ticker.history(period=period, interval = interval)

    candlestick_data = candlestick_data.reset_index()

    print(candlestick_data)

    print(candlestick_data.shape)


    if "Date" in candlestick_data:
        # Convert the date to string format from datetime for frontend plotly chart to process
        candlestick_data['Date'] = candlestick_data["Date"].dt.strftime('%Y-%m-%d')
    elif "Datetime" in candlestick_data:
                # Convert the date to string format from datetime for frontend plotly chart to process
        candlestick_data['Datetime'] = candlestick_data["Datetime"].dt.strftime('%Y-%m-%d %H:%M:%S')
        candlestick_data.rename(columns={"Datetime": "Date"},inplace=True)

    print(candlestick_data)


    # Calculate the Simple Moving Average (SMA) for the window period of the Close values
    candlestick_data["SMA"] = candlestick_data['Close'].rolling(window=12).mean()


    # Calculate the exponential moving average (EMA) (fast - 12 day moving average)
    candlestick_data["EMA-Fast"] = candlestick_data["Close"].ewm(span=12).mean()

    # Calculate the exponential moving average (EMA) (fast - 26 day moving average)
    candlestick_data["EMA-Slow"] = candlestick_data["Close"].ewm(span=26).mean()

    # Calculate the MACD moving average which is the ema-fast minus the ema-slow
    candlestick_data["MACD"] = candlestick_data["EMA-Fast"] - candlestick_data["EMA-Slow"]

    #Calculate the signal line
    candlestick_data["Signal"] = candlestick_data["MACD"].ewm(span=9).mean()

    # SMA won't work for the first n elements in the dataframe as it requires the sample of n elements to create the average
    candlestick_data.dropna(inplace=True)

    # Calculate the MACD Histogram
    candlestick_data['MACD-Hisogram'] = candlestick_data["MACD"] - candlestick_data["Signal"]

    print(candlestick_data)

    candlestick_data = candlestick_data.to_dict(orient="list")
    res = make_response(jsonify(candlestick_data),200)
    return res


@application.route("/info",methods=["POST","GET"])
def stock_info():
    stock_json = request.get_json() # convert json into python dict
    symbol = stock_json['Symbol']
    ticker = yf.Ticker(symbol)
    info = ticker.info
    res = make_response(jsonify(info),200)
    return res

@application.route("/financials", methods=["POST","GET"])
def stock_financials():
    stock_json = request.get_json()
    symbol = stock_json["Symbol"]
    ticker = yf.Ticker(symbol)
    financials = ticker.financials
    financials = financials.transpose()
    print(financials)
    # financials.reset_index(inplace=True)
    financials_json = financials.to_dict(orient="list")
    print(financials_json)
    res = make_response(jsonify(financials_json),200)
    return res

@application.route("/news", methods=["POST","GET"])
def stock_news():
    stock_json = request.get_json()
    symbol = stock_json["Symbol"]
    ticker = yf.Ticker(symbol)
    news = ticker.news
    print(news)
    res = make_response(jsonify(news),200)
    return res

@application.route("/crypto", methods=["POST", "GET"])
def crypto():
    if request.method == "POST":
        crpyto_data = request.get_json()
        coin_name = crpyto_data['Coin Name']
        ticker = yf.Ticker(coin_name)
        crypto_candlestick_data = ticker.history()
        res = make_response(jsonify(crypto_candlestick_data),200)
        return res
    coin_names = crypto_coins.to_dict(orient="records")
    return render_template("crypto.html",coin_names = coin_names)