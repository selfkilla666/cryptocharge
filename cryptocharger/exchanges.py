import streamlit as st
import requests


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
        symbol: str = pair.replace("/", "").upper()  # Формируем нужный формат пары
        response: requests.Response = requests.get(f"{self.base_url}?symbol={symbol}")
        if response.status_code == 451:
            response = requests.get(f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}")
        data = response.json()
        return float(data["price"])

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
        super().__init__("Bitfinex", "https://api.bitfinex.com/v2/ticker/")

    def get_price(self, pair):
        # Преобразование пары в формат Bitfinex, например, BTC/USD -> BTCUSD
        symbol = pair.replace("/", "").upper()  # Преобразуем в формат без косой черты, и делаем все заглавными
        try:
            # Отправляем запрос на API Bitfinex
            response = requests.get(f"{self.base_url}t{symbol}")
            response.raise_for_status()  # Проверяем успешность запроса

            # Получаем данные из ответа API
            data = response.json()

            # Проверяем, что данные содержат цену
            if data and isinstance(data, list) and len(data) > 6:
                # На Bitfinex цена — это элемент с индексом 6 в списке данных
                price = data[6]
                return price
            else:
                raise ValueError("Ответ не содержит необходимой информации о цене")
        
        except requests.exceptions.RequestException as e:
            st.warning(f"Ошибка при запросе к API Bitfinex: {e}")
        except ValueError as e:
            st.warning(f"Ошибка обработки данных: {e}")
        except Exception as e:
            st.warning(f"Неизвестная ошибка: {e}")

        return None

# Класс для Huobi
class HuobiAPI(ExchangeAPI):
    def __init__(self):
        super().__init__("Huobi", "https://api.huobi.pro/market/trade?symbol=")

    def get_price(self, pair):
        # Преобразование пары в формат Huobi, например, BTC/USD -> btcusdt
        symbol = pair.replace("/", "").lower()  # Преобразуем в формат без косой черты
        
        # Выполняем запрос
        try:
            response = requests.get(f"{self.base_url}{symbol}")
            response.raise_for_status()  # Проверяем, что запрос прошел успешно
            
            data = response.json()
            
            # Проверяем, что в ответе есть нужная информация о цене
            if 'tick' in data and 'close' in data['tick']:
                price = data['tick']['close']
                return price
            else:
                raise ValueError("Ответ не содержит цены")
        
        except requests.exceptions.RequestException as e:
            st.warning(f"Ошибка при запросе к API: {e}")
        except ValueError as e:
            st.warning(f"Ошибка обработки данных: {e}")
        except Exception as e:
            st.warning(f"Неизвестная ошибка: {e}")

        return None