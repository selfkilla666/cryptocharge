import streamlit as st

import pandas as pd
from datetime import datetime

from cryptocharger.exchanges import *


# Инициализация API для всех бирж
exchanges = [
    BinanceAPI(),
    CoinbaseAPI(),
    KrakenAPI(),
    BitfinexAPI(),
    HuobiAPI()
]

# Список криптовалютных пар
crypto_pairs = ["BTC/USD", "ETH/USD", "XRP/USD"]

# Получение данных и отображение в таблице
data = []

for exchange in exchanges:
    for pair in crypto_pairs:
        price = exchange.get_price(pair)
        if price is not None:
            data.append([exchange.name, pair, price])

# Создание DataFrame
df = pd.DataFrame(data, columns=["Биржа", "Пара", "Цена"])

# Пивотирование таблицы для нужного отображения
pivot_df = df.pivot(index="Пара", columns="Биржа", values="Цена")

# Отображение данных в Streamlit
st.title("Арбитраж криптовалют в реальном времени")
st.dataframe(pivot_df)