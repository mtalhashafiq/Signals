import ccxt
import pandas as pd
import pandas_ta as ta
import configparser
import time
import matplotlib.pyplot as plt

# 1. Read API credentials from config file
config = configparser.ConfigParser()
config.read('config.ini')

api_key = '2K43KfmIgF63h5HcZTol0aXgdPVPeecOJX0u2AVOcrvwnA6VzrYPb1JTGOvYd9yu'
api_secret = 'amj2MYOqDLiXCjjivOp2kVXKvnseifwMa3LrNcAd2WP4Dj3Cj8XiFUNtJzNpAJ5C'

# 2. Connect to Binance account using CCXT
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret
})

symbol = 'SOL/USDT'
timeframe = '1m'
min_data_length = 500  # Minimum number of rows required for indicators

# Separate variable for USDT amount
usdt_amount = 5  # Define a variable for USDT amount for placing orders

# Variable for controlling the bot execution interval (in seconds)
execution_interval = 60  # Set to 60 seconds (1 minute)

# 3. Fetch market data (OHLCV)
def fetch_ohlcv(symbol, timeframe='1m', limit=20):
    print(f"Fetching {limit} rows of data for {symbol} on {timeframe} timeframe")
    try:
        # Fetch OHLCV data from Binance API
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        # Create a pandas DataFrame with proper labels
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Add 'COLOR' column: GREEN for bullish candles, RED for bearish
        df['COLOR'] = df.apply(lambda row: 'GREEN' if row['close'] > row['open'] else 'RED', axis=1)

        print(f"Fetched data length: {len(df)}")
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# 4. Apply Technical Indicators
def apply_indicators(df):
    if df.empty:
        print("No data to apply indicators.")
        return df

    # Check if there's enough data for indicators
    if len(df) < min_data_length:
        print(f"Not enough data to calculate indicators (requires at least {min_data_length} rows).")
        return df

    print("Applying indicators...")
    try:
        # Apply technical indicators
        df['EMA_50'] = ta.ema(df['close'], length=50)  # 50-period Exponential Moving Average
        df['EMA_200'] = ta.ema(df['close'], length=200)  # 200-period Exponential Moving Average
        df['RSI'] = ta.rsi(df['close'], length=14)  # 14-period Relative Strength Index

        # Bollinger Bands (20 periods, 2 standard deviations)
        bbands = ta.bbands(df['close'], length=20, std=2)
        df['Bollinger_upper_band'] = bbands['BBU_20_2.0']  # Upper Bollinger Band
        df['Bollinger_middle_band'] = bbands['BBM_20_2.0']  # Middle Bollinger Band
        df['Bollinger_lower_band'] = bbands['BBL_20_2.0']  # Lower Bollinger Band

        # MACD (Moving Average Convergence Divergence)
        macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_signal'] = macd['MACDs_12_26_9']

        print(df[['timestamp', 'open', 'close', 'high', 'low', 'COLOR', 'EMA_50', 'EMA_200', 'RSI', 'Bollinger_upper_band', 'Bollinger_lower_band', 'MACD']].tail(20))

    except Exception as e:
        print(f"Error applying indicators: {e}")

    return df

# 5. Buy and Sell Logic with MACD
def check_buy_sell_signals(df):
    # Drop rows where EMA_50, EMA_200, or MACD is NaN
    df_clean = df.dropna(subset=['EMA_50', 'EMA_200', 'MACD', 'MACD_signal'])

    if df_clean.empty:
        print("Not enough data to check buy/sell signals.")
        return False, False

    print("Checking buy/sell signals...")

    # Buy Signal Logic (including MACD):
    buy_signal = (df['EMA_50'].iloc[-1] > df['EMA_200'].iloc[-1] and  # Uptrend (EMA 50 above EMA 200)
                  df['RSI'].iloc[-1] < 40 and  # RSI indicates oversold market
                  df['close'].iloc[-1] < df['Bollinger_lower_band'].iloc[-1] and  # Price below lower Bollinger Band
                  df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1])  # MACD bullish crossover

    # Sell Signal Logic (including MACD):
    sell_signal = (df['EMA_50'].iloc[-1] < df['EMA_200'].iloc[-1] and  # Downtrend (EMA 50 below EMA 200)
                   df['RSI'].iloc[-1] > 70 and  # RSI indicates overbought market
                   df['close'].iloc[-1] > df['Bollinger_upper_band'].iloc[-1] and  # Price above upper Bollinger Band
                   df['MACD'].iloc[-1] < df['MACD_signal'].iloc[-1])  # MACD bearish crossover

    # Check why buy signal wasn't generated
    if not buy_signal:
        if df['EMA_50'].iloc[-1] <= df['EMA_200'].iloc[-1]:
            print("Buy Signal not generated: The 50-period EMA is below the 200-period EMA, indicating a downtrend.")
        if df['RSI'].iloc[-1] >= 40:
            print("Buy Signal not generated: The RSI is not below 40, so the market is not considered oversold.")
        if df['close'].iloc[-1] >= df['Bollinger_lower_band'].iloc[-1]:
            print("Buy Signal not generated: The price is not below the lower Bollinger Band, indicating it's not in a potential buying range.")
        if df['MACD'].iloc[-1] <= df['MACD_signal'].iloc[-1]:
            print("Buy Signal not generated: The MACD line is below the signal line, indicating a lack of bullish momentum.")

    # Check why sell signal wasn't generated
    if not sell_signal:
        if df['EMA_50'].iloc[-1] >= df['EMA_200'].iloc[-1]:
            print("Sell Signal not generated: The 50-period EMA is above the 200-period EMA, indicating an uptrend.")
        if df['RSI'].iloc[-1] <= 70:
            print("Sell Signal not generated: The RSI is not above 70, so the market is not considered overbought.")
        if df['close'].iloc[-1] <= df['Bollinger_upper_band'].iloc[-1]:
            print("Sell Signal not generated: The price is not above the upper Bollinger Band, indicating it's not in a potential selling range.")
        if df['MACD'].iloc[-1] >= df['MACD_signal'].iloc[-1]:
            print("Sell Signal not generated: The MACD line is above the signal line, indicating a lack of bearish momentum.")

    if buy_signal:
        print("Buy Signal detected!")
    if sell_signal:
        print("Sell Signal detected!")

    return buy_signal, sell_signal

# 6. Place buy/sell orders
def place_order(symbol, order_type, usdt_amount):  # Use the usdt_amount variable
    try:
        market_price = exchange.fetch_ticker(symbol)['close']
        amount = usdt_amount / market_price  # Calculate the amount based on USDT and current market price

        if order_type == 'buy':
            print(f"Placing buy order for {usdt_amount} USDT worth of {symbol}")
            order = exchange.create_market_buy_order(symbol, amount)
        elif order_type == 'sell':
            print(f"Placing sell order for {usdt_amount} USDT worth of {symbol}")
            order = exchange.create_market_sell_order(symbol, amount)

        print(f"Order executed: {order}")
    except Exception as e:
        print(f"Error executing order: {e}")

# 7. Plotting function
def plot_data(df):
    if df.empty:
        print("No data to plot.")
        return

    plt.figure(figsize=(14, 7))
    plt.plot(df['timestamp'], df['close'], label='Close Price', color='blue')
    plt.plot(df['timestamp'], df['EMA_50'], label='EMA 50', color='orange')
    plt.plot(df['timestamp'], df['EMA_200'], label='EMA 200', color='red')
    plt.fill_between(df['timestamp'], df['Bollinger_lower_band'], df['Bollinger_upper_band'], color='lightgrey', alpha=0.5, label='Bollinger Bands')

    plt.plot(df['timestamp'], df['high'], label='High', color='green', linestyle='dotted')
    plt.plot(df['timestamp'], df['low'], label='Low', color='red', linestyle='dotted')

    plt.title(f'{symbol} Price and Indicators')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 8. Main trading loop with variable row limit and fixed interval execution
def main_trading_loop(limit=500):
    print("Starting trading loop...")
    while True:
        start_time = time.time()  # Track the time at the start of each iteration
        try:
            df = fetch_ohlcv(symbol, timeframe, limit=limit)
            df = apply_indicators(df)
            buy_signal, sell_signal = check_buy_sell_signals(df)

            if buy_signal:
                place_order(symbol, 'buy', usdt_amount)  # Use usdt_amount here for buy order
            elif sell_signal:
                place_order(symbol, 'sell', usdt_amount)  # Use usdt_amount here for sell order

            plot_data(df)

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Calculate how long the loop took and ensure it waits for the execution interval (60 seconds)
        elapsed_time = time.time() - start_time
        sleep_time = max(0, execution_interval - elapsed_time)
        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)  # Wait for the remaining time of 60 seconds

# 9. Run the bot with a variable row limit


# Example minimum data length; set this to your actual minimum value
 # Adjust this value as necessary

# Set the duration for how long you want the program to run in minutes
RUNNING_DURATION_MINUTES = 1  # Change this value as needed for testing
RUNNING_DURATION_SECONDS = RUNNING_DURATION_MINUTES * 60

def execute_trading_strategy(limit):
    """Main trading logic."""
    print(f"Running trading strategy with limit: {limit}")
    # Here you would include your trading logic (data fetching, processing, etc.)

if __name__ == "__main__":
    print("Program started. Initializing trading strategy...")

    row_limit = max(500, min_data_length)  # Ensure at least 500 rows are fetched
    start_time = time.time()

    # Initial execution before entering the loop
    try:
        print("Executing trading strategy...")
        execute_trading_strategy(limit=row_limit)
    except Exception as e:
        print(f"An error occurred during initial execution: {e}")

    while (time.time() - start_time) < RUNNING_DURATION_SECONDS:
        print("Waiting for the next execution... (1 minute interval)")
        row_limit = max(500, min_data_length)
        main_trading_loop(limit=row_limit)
        time.sleep(60)  # Wait for 1 minute before running the loop again

        try:
            print("Executing trading strategy...")
            execute_trading_strategy(limit=row_limit)
        except Exception as e:
            print(f"An error occurred during execution: {e}")

    print("Running duration complete. Exiting program.")

