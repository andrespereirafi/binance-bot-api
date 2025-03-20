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
    latest_data = df.iloc[-1]
    response_text = f"{latest_data['close']},{latest_data['rsi']},{latest_data['adx']},{latest_data['market_trend']}"
    return response_text

@app.get("/data")
def get_data():
    """Endpoint para enviar datos a TradingView en formato texto"""
    return analyze_market()
