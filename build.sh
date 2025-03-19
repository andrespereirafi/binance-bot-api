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

# Instalar TA-Lib con pip
pip install TA-Lib
