import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Базовый класс для работы с биржами
class ExchangeAPI:
    def __init__(self, name, base_url):
        self.name = name
        self.base_url = base_url

    def get_price(self, pair):
        """Метод для получения цены. Переопределяется в дочерних классах."""
        raise NotImplementedError("Этот метод должен быть реализован в подклассе")

# Класс для Binance
class BinanceAPI(ExchangeAPI):
    def __init__(self):
        super().__init__("Binance", "https://api.binance.com/api/v3/ticker/price")

    def get_price(self, pair):
        # Преобразование пары в формат Binance, например, BTC/USD -> BTCUSDT
        symbol = pair.replace("/", "").upper()  # Формируем нужный формат пары
        try:
            response = requests.get(self.base_url, params={"symbol": symbol})
            if response.status_code == 200:
                data = response.json()
                return float(data["price"])
            else:
                st.error(f"Ошибка Binance API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Ошибка подключения к Binance: {e}")
            return None

# Класс для Coinbase
class CoinbaseAPI(ExchangeAPI):
    def __init__(self):
        super().__init__("Coinbase", "https://api.coinbase.com/v2/prices")

    def get_price(self, pair):
        # Преобразование пары в формат Coinbase, например, BTC/USD
        try:
            response = requests.get(f"{self.base_url}/{pair.replace('/', '-')}/spot")
            if response.status_code == 200:
                data = response.json()
                return float(data["data"]["amount"])
            else:
                st.error(f"Ошибка Coinbase API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Ошибка подключения к Coinbase: {e}")
            return None

# Класс для Kraken
class KrakenAPI(ExchangeAPI):
    def __init__(self):
        super().__init__("Kraken", "https://api.kraken.com/0/public/Ticker")

    def get_price(self, pair):
        # Преобразование пары в формат Kraken, например, BTC/USD -> XBTUSD
        symbol = pair.replace("BTC", "XBT").replace("/", "")
        try:
            response = requests.get(self.base_url, params={"pair": symbol})
            if response.status_code == 200:
                data = response.json()
                price = float(data["result"][list(data["result"].keys())[0]]["c"][0])
                return price
            else:
                st.error(f"Ошибка Kraken API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Ошибка подключения к Kraken: {e}")
            return None

# Класс для Bitfinex
class BitfinexAPI(ExchangeAPI):
    def __init__(self):
        super().__init__("Bitfinex", "https://api.bitfinex.com/v1/pubticker/")

    def get_price(self, pair):
        # Преобразование пары в формат Bitfinex, например, BTC/USD -> btcusd
        symbol = pair.replace("/", "").lower()
        try:
            response = requests.get(f"{self.base_url}{symbol}")
            if response.status_code == 200:
                data = response.json()
                return float(data["last_price"])
            else:
                st.error(f"Ошибка Bitfinex API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Ошибка подключения к Bitfinex: {e}")
            return None

# Класс для Huobi
class HuobiAPI(ExchangeAPI):
    def __init__(self):
        super().__init__("Huobi", "https://api.huobi.pro/market/detail/merged")

    def get_price(self, pair):
        # Преобразование пары в формат Huobi, например, BTC/USD -> btcusdt
        symbol = pair.replace("/", "").lower()  # Преобразуем в формат без косой черты
        try:
            response = requests.get(self.base_url, params={"symbol": symbol})
            if response.status_code == 200:
                data = response.json()
                # Проверим, есть ли ключ 'tick' и 'close' в ответе
                if "tick" in data and "close" in data["tick"]:
                    return float(data["tick"]["close"])
                else:
                    st.error(f"Не удалось найти цену для {pair} на Huobi")
                    return None
            else:
                st.error(f"Ошибка Huobi API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Ошибка подключения к Huobi: {e}")
            return None

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
