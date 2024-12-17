import ccxt  # Library for connecting to cryptocurrency exchanges like Binance
import pandas as pd  # Library for data manipulation
import pandas_ta as ta  # Library for technical indicators
import configparser  # Library for reading configuration files
import time  # Library for handling time-based functions

# 1. Read API credentials from config file
# 'configparser' reads the API credentials from a 'config.ini' file to securely access your Binance account.
config = configparser.ConfigParser()
config.read('config.ini')

# API key and secret key obtained from the Binance account
api_key = '2K43KfmIgF63h5HcZTol0aXgdPVPeecOJX0u2AVOcrvwnA6VzrYPb1JTGOvYd9yu'
api_secret = 'amj2MYOqDLiXCjjivOp2kVXKvnseifwMa3LrNcAd2WP4Dj3Cj8XiFUNtJzNpAJ5C'

# 2. Connect to Binance account using CCXT
# 'ccxt' allows us to interact with Binance's API, authenticate using your API key and secret.
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True  # This prevents hitting the rate limits set by Binance.
})

# Define trading pair and timeframe
symbol = 'SOL/USDT'  # Trading pair, SOLANA/USDT
timeframe = '1m'  # 1-minute timeframe

# 3. Fetch market data (OHLCV)
def fetch_ohlcv(symbol, timeframe='1m', limit=500):
    """
    Fetches the latest OHLCV (Open, High, Low, Close, Volume) data from Binance.
    - symbol: the trading pair.
    - timeframe: the interval for the candles.
    - limit: the number of candles to fetch.
    """
    print(f"Fetching data for {symbol} on {timeframe} timeframe")
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Convert timestamp to a readable format
    return df

# 4. Apply Technical Indicators (EMA, RSI, Bollinger Bands, MACD, QQE, Stochastic RSI)
def apply_indicators(df):
    """
    Apply various technical indicators to the fetched OHLCV data.
    - df: DataFrame containing OHLCV data.
    """
    print("Applying indicators...")
    
    # EMA (Exponential Moving Average)
    df['EMA_50'] = ta.ema(df['close'], length=50)
    df['EMA_200'] = ta.ema(df['close'], length=200)
    
    # RSI (Relative Strength Index)
    df['RSI'] = ta.rsi(df['close'], length=14)
    
    # Bollinger Bands (Upper, Middle, Lower)
    bbands = ta.bbands(df['close'], length=20, std=2)
    df['upper_band'], df['middle_band'], df['lower_band'] = bbands['BBU_20_2.0'], bbands['BBM_20_2.0'], bbands['BBL_20_2.0']
    
    # MACD (Moving Average Convergence Divergence)
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df['MACD'], df['MACD_signal'] = macd['MACD_12_26_9'], macd['MACDs_12_26_9']
    
    # QQE (Approximation using RSI and EMA)
    df['QQE'] = ta.ema(df['RSI'], length=5)
    
    # Stochastic RSI
    stochrsi = ta.stochrsi(df['close'], length=14)
    df['StochRSI_k'], df['StochRSI_d'] = stochrsi['STOCHRSIk_14_14_3_3'], stochrsi['STOCHRSId_14_14_3_3']
    
    return df

# 5. Buy and Sell Logic
def check_buy_sell_signals(df):
    """
    Check for buy and sell signals based on indicators:
    - Buy signal if EMA 50 > EMA 200, RSI < 30, and close price is below the lower Bollinger band.
    - Sell signal if EMA 50 < EMA 200, RSI > 70, and close price is above the upper Bollinger band.
    """
    print("Checking buy/sell signals...")
    buy_signal = False
    sell_signal = False
    
    # Buy conditions
    if df['EMA_50'].iloc[-1] > df['EMA_200'].iloc[-1] and df['RSI'].iloc[-1] < 30 and df['close'].iloc[-1] < df['lower_band'].iloc[-1]:
        buy_signal = True
        print("Buy Signal detected!")
    
    # Sell conditions
    if df['EMA_50'].iloc[-1] < df['EMA_200'].iloc[-1] and df['RSI'].iloc[-1] > 70 and df['close'].iloc[-1] > df['upper_band'].iloc[-1]:
        sell_signal = True
        print("Sell Signal detected!")
    
    return buy_signal, sell_signal

# 6. Place buy/sell orders
def place_order(symbol, order_type, usdt_amount):
    """
    Places a buy or sell order based on the signals:
    - symbol: the trading pair (SOL/USDT).
    - order_type: either 'buy' or 'sell'.
    - usdt_amount: the amount in USDT to trade.
    """
    try:
        if order_type == 'buy':
            print(f"Placing buy order for {usdt_amount} USDT worth of {symbol}")
            order = exchange.create_market_buy_order(symbol, usdt_amount / exchange.fetch_ticker(symbol)['close'])
        elif order_type == 'sell':
            print(f"Placing sell order for {usdt_amount} USDT worth of {symbol}")
            order = exchange.create_market_sell_order(symbol, usdt_amount / exchange.fetch_ticker(symbol)['close'])
        print(f"Order executed: {order}")
    except Exception as e:
        print(f"Error executing order: {e}")

# 7. Main trading loop
def main_trading_loop():
    """
    The main loop that keeps fetching new data, checking for signals, and placing orders accordingly.
    """
    print("Starting trading loop...")
    while True:
        try:
            # Fetch the latest market data
            df = fetch_ohlcv(symbol, timeframe)
            # Apply technical indicators to the data
            df = apply_indicators(df)
            
            # Check if any buy or sell signals are generated
            buy_signal, sell_signal = check_buy_sell_signals(df)
            
            # Place a buy order if a buy signal is detected
            if buy_signal:
                place_order(symbol, 'buy', 2)  # Buy 2 USDT worth of SOL/USDT
            # Place a sell order if a sell signal is detected
            elif sell_signal:
                place_order(symbol, 'sell', 2)  # Sell 2 USDT worth of SOL/USDT
            
            # Sleep for 60 seconds (1 minute) before checking again
            print("Sleeping for 1 minute...")
            time.sleep(60)
        
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Wait for 60 seconds before retrying

# 8. Run the bot
if __name__ == "__main__":
    main_trading_loop()
