import ccxt
from config import API_KEY, API_SECRET  # Importar claves desde config.py

# Conectarse a Binance con las API Keys
binance = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {'defaultType': 'future'}  # Para operar en futuros
})

# Obtener saldo disponible en USDT
balance = binance.fetch_balance()
print("Saldo disponible en USDT:", balance['USDT']['free'])
