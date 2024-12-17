import time  # Import the time module to manage sleep intervals
import pandas as pd  # Import pandas for data manipulation and analysis
import numpy as np  # Import NumPy for numerical operations
from binance.client import Client  # Import the Binance client to interact with the Binance API
from binance.enums import *  # Import Binance enums for trading commands and options
import pandas_ta as ta  # Import pandas-ta for technical analysis indicators


# Your Binance API Key and Secret

api_key = '2K43KfmIgF63h5HcZTol0aXgdPVPeecOJX0u2AVOcrvwnA6VzrYPb1JTGOvYd9yu'
api_secret = 'amj2MYOqDLiXCjjivOp2kVXKvnseifwMa3LrNcAd2WP4Dj3Cj8XiFUNtJzNpAJ5C'

# Create a client instance to interact with the Binance API
client = Client(api_key, api_secret)

# Define the trading symbol and other parameters
symbol = 'SOLUSDT'  # Trading pair for Solana against USDT
interval = Client.KLINE_INTERVAL_1MINUTE  # Set the interval for 5 minutes
lookback = '1 minute ago UTC'  # Define the lookback period to fetch historical data
usdt_quantity = 3  # Set the quantity in USDT for buying/selling; adjust based on your balance

def get_historical_data(symbol, interval, lookback):
    # Fetch historical price data from the Binance API
    klines = client.get_historical_klines(symbol, interval, lookback)
    # Convert the raw data into a DataFrame for easier manipulation
    data = pd.DataFrame(klines, columns=[
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close Time', 'Quote Asset Volume', 'Number of Trades',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
    ])
    data['Close'] = pd.to_numeric(data['Close'])  # Convert the 'Close' column to numeric values
    data['Open Time'] = pd.to_datetime(data['Open Time'], unit='ms')  # Convert timestamps to datetime
    return data[['Open Time', 'Close']]  # Return only the relevant columns

def calculate_wilders(data, window):
    # Calculate the Wilder's Moving Average
    wma = data['Close'].ewm(span=window, adjust=False).mean()  # Exponential Moving Average as Wilder's Average
    return wma

def calculate_indicators(data):
    # Calculate various technical indicators for the trading strategy
    data['EMA'] = ta.trend.ema_indicator(data['Close'], window=20)  # Calculate the 20-period EMA
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)  # Calculate the 14-period RSI
    data['Bollinger_High'] = ta.volatility.bollinger_hband(data['Close'], window=20, window_dev=2)  # Upper Bollinger Band
    data['Bollinger_Low'] = ta.volatility.bollinger_lband(data['Close'], window=20, window_dev=2)  # Lower Bollinger Band
    
    # QQE Mod calculation
    data['Wilders'] = calculate_wilders(data, window=14)  # Calculate Wilder's moving average manually
    data['QQE'] = (data['Wilders'].shift(1) * 0.25 + data['Wilders'] * 0.75).fillna(0)  # Calculate QQE
    data['QQE_Signal'] = np.where(data['Close'] > data['QQE'], 1, 0)  # Generate buy/sell signal based on QQE
    
    return data  # Return the data with indicators added

def execute_trade(signal):
    # Fetch the current price of SOL in USDT to determine the quantity to buy/sell
    ticker = client.get_symbol_ticker(symbol=symbol)  
    price = float(ticker['price'])  # Get the current price of SOL
    sol_quantity = round(usdt_quantity / price, 2)  # Convert USDT to SOL, rounded to 2 decimal places

    if signal == 'buy':
        print(f"Buying {sol_quantity} SOL...")  # Print the buying action
        client.order_market_buy(symbol=symbol, quantity=sol_quantity)  # Place a market buy order
    elif signal == 'sell':
        print(f"Selling {sol_quantity} SOL...")  # Print the selling action
        client.order_market_sell(symbol=symbol, quantity=sol_quantity)  # Place a market sell order

def main():
    while True:  # Infinite loop to continuously check for trading signals
        # Get historical data
        data = get_historical_data(symbol, interval, lookback)
        
        # Calculate indicators
        data = calculate_indicators(data)
        
        # Get the latest values from the data
        last_row = data.iloc[-1]
        
        # Trading signals based on the indicators
        # Buy signal condition
        if last_row['Close'] < last_row['Bollinger_Low'] and last_row['RSI'] < 30 and last_row['QQE_Signal'] == 1:
            execute_trade('buy')  # Execute a buy trade
        # Sell signal condition
        elif last_row['Close'] > last_row['Bollinger_High'] and last_row['RSI'] > 70 and last_row['QQE_Signal'] == 0:
            execute_trade('sell')  # Execute a sell trade

        # Wait for the next interval before checking again
        time.sleep(300)  # Sleep for 5 minutes (300 seconds)

if __name__ == "__main__":
    main()  # Run the main function to start the trading bot
