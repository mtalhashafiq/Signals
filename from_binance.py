
from binance.client import Client  # Importing the Binance library

# Example usage
api_key = 'KR7alBIRB5LSbSr0R47eu80Z3pf3lyEsv9OqIrD2jWGgmmtcJcM7Qn61Uq19n6bm'
api_secret = 'OLhcJkBS3Uji0SAM9Al3vJSdcn46XYfM4w8YIPQGVfmTcpBTBfYh0MGFYkqZIegE'
client = Client(api_key, api_secret)

# Get account info to check if it works
account_info = client.get_account()
print(account_info)
