from binance.client import Client  # Import the Binance client to interact with the Binance API
import time  # Import the time module to manage sleep intervals
import pandas as pd  # Import pandas for data manipulation and analysis
import numpy as np  # Import NumPy for numerical operations (correctly)
from binance.enums import *  # Import Binance enums for trading commands and options
import pandas_ta as ta  # Import pandas-ta for technical analysis indicators

# Your Binance API Key and Secret
api_key = '2K43KfmIgF63h5HcZTol0aXgdPVPeecOJX0u2AVOcrvwnA6VzrYPb1JTGOvYd9yu'
api_secret = 'amj2MYOqDLiXCjjivOp2kVXKvnseifwMa3LrNcAd2WP4Dj3Cj8XiFUNtJzNpAJ5C'

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

# Get historical data for SOLUSDT
def fetch_data(symbol, interval):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['close'] = df['close'].astype(float)
        print(df.tail())  # Display the most recent data
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")

# Test fetch for 12-hour interval
data = fetch_data('SOLUSDT', '12h')
