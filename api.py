from fastapi import FastAPI
import pandas as pd
import pandas_ta as ta
import ccxt

app = FastAPI()

# Configuración de Binance
binance = ccxt.binance()

symbol = "BTC/USDT"
timeframe = "15m"

def get_market_data(symbol, timeframe, limit=100):
    """Obtiene datos OHLCV del mercado"""
    bars = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def analyze_market():
    """Realiza análisis técnico"""
    df = get_market_data(symbol, timeframe)
    
    # Aplicar indicadores
    df['rsi'] = df.ta.rsi(length=14)
    df['adx'] = df.ta.adx(length=14)['ADX_14']
    df['market_trend'] = df['close'].diff().apply(lambda x: "Bullish" if x > 0 else "Bearish")
    
    # Extraer últimos valores
    latest_data = df.iloc[-1][['timestamp', 'close', 'rsi', 'adx', 'market_trend']].to_dict()
    return latest_data

@app.get("/data")
def get_data():
    """Endpoint para enviar datos a TradingView"""
    return analyze_market()
