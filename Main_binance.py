from binance.client import Client
import time

# Your Binance API Key and Secret

api_key = '2K43KfmIgF63h5HcZTol0aXgdPVPeecOJX0u2AVOcrvwnA6VzrYPb1JTGOvYd9yu'
api_secret = 'amj2MYOqDLiXCjjivOp2kVXKvnseifwMa3LrNcAd2WP4Dj3Cj8XiFUNtJzNpAJ5C'

# Create a client instance
client = Client(api_key, api_secret)

# Set the trading parameters
symbol = 'BTCUSDT'  # Trading pair
quantity = 0.001    # Quantity to buy/sell
price_threshold = 50000  # Example price threshold to trigger a buy

def get_current_price(symbol):
    """Get the current price of the specified symbol."""
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def place_market_order(symbol, quantity, side):
    """Place a market order."""
    try:
        order = client.order_market(
            symbol=symbol,
            side=side,
            quantity=quantity
        )
        print(f"Market order placed: {order}")
    except Exception as e:
        print(f"An error occurred: {e}")

def trading_bot():
    while True:
        try:
            current_price = get_current_price(symbol)
            print(f"Current price of {symbol}: {current_price}")

            # Example condition: Buy if the price drops below the threshold
            if current_price < price_threshold:
                print(f"Price is below threshold ({price_threshold}). Buying...")
                place_market_order(symbol, quantity, 'BUY')

            # Wait for a while before the next check
            time.sleep(1)  # Check every 30 seconds

        except Exception as e:
            print(f"An error occurred in the trading loop: {e}")
            time.sleep(60)  # Wait before retrying in case of error

if __name__ == "__main__":
    trading_bot()
