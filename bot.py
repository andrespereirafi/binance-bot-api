import ccxt
import pandas as pd
import numpy as np
import talib
import json
from bokeh.plotting import figure, show, output_file
from config import API_KEY, API_SECRET  # Claves API Binance

# Configuración de Binance
binance = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {'defaultType': 'future'}  # Para operar en futuros
})

# Parámetros del bot
symbol = "BTC/USDT"
timeframe = "15m"
order_block_periods = 20

def get_market_data(symbol, timeframe, limit=100):
    """Obtiene datos OHLCV del mercado"""
    bars = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def detect_market_structure(df):
    """Detecta estructura del mercado (HH, LL, LH, HL)"""
    df['hh'] = df['high'].rolling(5).max()
    df['ll'] = df['low'].rolling(5).min()
    df['market_trend'] = np.where(df['close'] > df['hh'], "Bullish",
                                  np.where(df['close'] < df['ll'], "Bearish", "Neutral"))
    return df

def detect_order_blocks(df):
    """Detecta Order Blocks en zonas de reversión"""
    df['order_block'] = np.where(
        (df['close'].shift(1) > df['open'].shift(1)) & (df['close'] < df['open']), "Bearish OB",
        np.where((df['close'].shift(1) < df['open'].shift(1)) & (df['close'] > df['open']), "Bullish OB", "None")
    )
    return df

def detect_liquidity_zones(df):
    """Encuentra zonas de liquidez donde hay barridos de stops"""
    df['liquidity_zone'] = np.where(
        (df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(2)), "Stop Hunt Low",
        np.where((df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(2)), "Stop Hunt High", "None")
    )
    return df

def order_flow_analysis(df):
    """Usa TA-Lib para analizar el Order Flow"""
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['volume_ma'] = talib.SMA(df['volume'], timeperiod=10)
    return df

def place_order(order_type, quantity):
    """Ejecuta una orden en Binance"""
    params = {
        'symbol': symbol.replace("/", ""),
        'side': "BUY" if order_type == "long" else "SELL",
        'type': "MARKET",
        'quantity': quantity
    }
    order = binance.create_order(**params)
    print("Orden ejecutada:", order)

# Obtener datos y analizar
df = get_market_data(symbol, timeframe)
df = detect_market_structure(df)
df = detect_order_blocks(df)
df = detect_liquidity_zones(df)
df = order_flow_analysis(df)

# Detección de entrada a mercado
latest = df.iloc[-1]
if latest['order_block'] == "Bullish OB" and latest['liquidity_zone'] == "Stop Hunt Low":
    print("📈 Señal de Compra (LONG)")
    place_order("long", 0.001)  # Ajusta la cantidad según tu balance
elif latest['order_block'] == "Bearish OB" and latest['liquidity_zone'] == "Stop Hunt High":
    print("📉 Señal de Venta (SHORT)")
    place_order("short", 0.001)

# 📊 Graficar con Bokeh
output_file("market_analysis.html")
p = figure(title="BTC/USDT Market Analysis", x_axis_type="datetime", width=800, height=400)
p.line(df['timestamp'], df['close'], legend_label="Precio", color="blue")
p.scatter(df[df['order_block'] == "Bullish OB"]['timestamp'],
          df[df['order_block'] == "Bullish OB"]['close'], color="green", legend_label="Bullish OB")
p.scatter(df[df['order_block'] == "Bearish OB"]['timestamp'],
          df[df['order_block'] == "Bearish OB"]['close'], color="red", legend_label="Bearish OB")
show(p)

# Mostrar señales detectadas
print(df[['timestamp', 'close', 'market_trend', 'order_block', 'liquidity_zone', 'rsi', 'adx', 'volume_ma']].tail(20))

import asyncio
import websockets

async def send_signal_to_tradingview(signal):
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        await websocket.send(json.dumps(signal))

# Ejemplo de señal que enviará el bot
latest_signal = {
    "symbol": "BTC/USDT",
    "order_block": df.iloc[-1]["order_block"],
    "liquidity_zone": df.iloc[-1]["liquidity_zone"],
    "price": df.iloc[-1]["close"]
}

# Enviar señal a TradingView
asyncio.run(send_signal_to_tradingview(latest_signal))
