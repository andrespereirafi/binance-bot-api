from fastapi import FastAPI
import json

app = FastAPI()

# Datos simulados (debes actualizar esto con datos en tiempo real)
latest_signal = {
    "price": 64700.5,
    "order_block": "High",
    "liquidity_zone": "Strong"
}

@app.get("/signal")
def get_signal():
    return latest_signal
