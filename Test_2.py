from binance.client import Client  # Import the Binance client to interact with the Binance API
import time  # Import the time module to manage sleep intervals
import pandas as pd  # Import pandas for data manipulation and analysis
# import numpy as np  # Import NumPy for numerical operations (correctly)
from binance.enums import *  # Import Binance enums for trading commands and options
import pandas_ta as ta  # Import pandas-ta for technical analysis indicators

# Your Binance API Key and Secret
api_key = '2K43KfmIgF63h5HcZTol0aXgdPVPeecOJX0u2AVOcrvwnA6VzrYPb1JTGOvYd9yu'
api_secret = 'amj2MYOqDLiXCjjivOp2kVXKvnseifwMa3LrNcAd2WP4Dj3Cj8XiFUNtJzNpAJ5C'

# Define the trading symbol and other parameters
symbol = 'SOLUSDT'  # Trading pair for Solana against USDT
interval = Client.KLINE_INTERVAL_1MINUTE  # Set the interval for 5 minutes
lookback = '1 minute ago UTC'  # Define the lookback period to fetch historical data
usdt_quantity = 3  # Set the quantity in USDT for buying/selling; adjust based on your balance

# Create a client instance to interact with the Binance API
client = Client(api_key, api_secret)
account_info = client.get_account()
balances = account_info['balances']

# Print non-zero balances
for balance in balances:
    asset = balance['asset']
    free = float(balance['free'])
    locked = float(balance['locked'])
    
    if free > 0 or locked > 0:
        print(f"Asset: {asset}, Free: {free}, Locked: {locked}")
        
        
        
def get_historical_data(symbol, interval, lookback):
    try:
        klines = client.get_historical_klines(symbol, interval, lookback)
        data = pd.DataFrame(klines, columns=[
            'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close Time', 'Quote Asset Volume', 'Number of Trades',
            'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
        ])
        data['Close'] = pd.to_numeric(data['Close'])  # Convert the 'Close' column to numeric values
        data['Open Time'] = pd.to_datetime(data['Open Time'], unit='ms')  # Convert timestamps to datetime
        return data[['Open Time', 'Close']]  # Return only the relevant columns
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def execute_trade(signal):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)  
        price = float(ticker['price'])  # Get the current price of SOL
        sol_quantity = round(usdt_quantity / price, 2)  # Convert USDT to SOL

        if sol_quantity <= 0:
            print("Calculated quantity is zero or negative, cannot execute trade.")
            return

        if signal == 'buy':
            print(f"Buying {sol_quantity} SOL at price {price}...")  # Print the buying action
            client.order_market_buy(symbol=symbol, quantity=sol_quantity)  # Place a market buy order
        elif signal == 'sell':
            print(f"Selling {sol_quantity} SOL at price {price}...")  # Print the selling action
            client.order_market_sell(symbol=symbol, quantity=sol_quantity)  # Place a market sell order
    except Exception as e:
        print(f"Error executing trade: {e}")

# Main trading loop
def main():
    while True:
        data = get_historical_data(symbol, interval, lookback)
        
        if data.empty:
            print("No data retrieved, skipping iteration...")
            time.sleep(300)
            continue
        
        data = calculate_indicators(data)
        
        last_row = data.iloc[-1]
        
        # Trading signals
        if last_row['Close'] < last_row['Bollinger_Low'] and last_row['RSI'] < 30 and last_row['QQE_Signal'] == 1:
            execute_trade('buy')
        elif last_row['Close'] > last_row['Bollinger_High'] and last_row['RSI'] > 70 and last_row['QQE_Signal'] == 0:
            execute_trade('sell')

        time.sleep(300)

if __name__ == "__main__":
    main()
