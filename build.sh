#!/bin/bash

# Instalar dependencias del sistema
apt-get update && apt-get install -y \
    build-essential \
    gcc \
    make \
    libta-lib0 \
    libta-lib-dev \
    python3-dev \
    python3-pip

# Descargar e instalar TA-Lib manualmente
mkdir -p /opt/ta-lib
cd /opt/ta-lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xvzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
make install

# Volver al directorio principal
cd /opt/render/project/src

# Instalar librerías de Python (sin TA-Lib en requirements.txt)
pip install numpy pandas ccxt
pip install TA-Lib
