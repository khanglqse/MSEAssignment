import requests

API_KEY = '97TPEXSZA2755456'
BASE_URL = 'https://www.alphavantage.co/query'

def get_exchange_rate():
    params = {
        'function': 'CURRENCY_EXCHANGE_RATE',
        'from_currency': 'USD',
        'to_currency': 'VND',
        'apikey': API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    print(data)
    if "Realtime Currency Exchange Rate" not in data:
        return 24000
        print(f"Error fetching data: {data.get('Note', '')}")
        return None

    exchange_rate = data["Realtime Currency Exchange Rate"]
    print(exchange_rate)
    return float(exchange_rate['5. Exchange Rate'])
