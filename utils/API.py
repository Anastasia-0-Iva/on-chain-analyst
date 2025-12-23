import requests

API_KEY = 'R4281GPWBHNIGIHTGB6UAHCJ7ZVZPJYE74'
url = f'https://api.etherscan.io/v2/api?module=account&action=balance&address=0x...&chainid=1&apikey={API_KEY}'

response = requests.get(url)
data = response.json()
#print(data)