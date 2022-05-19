import requests
from dpath.util import values as path_values

class Ticker:
    # URL запрос
    session = requests.session()

    # заголовок для URL запроса
    headers = 'Mozilla/5.0 (Windows NT 10.0; WOW64 ' \
              'AppleWebKit/537.36 (KHTML, like Gecko) '\
              'Chrome/91.0.4472.135 Safari/537.36'

    # запрашиваемые поля
    value = {
        'price': 'regularMarketPrice',
        'percent': 'regularMarketChangePercent'
    }

    # конструктор класса
    def __init__(self, name):
        # определяем первоначальные значения
        self.name = name
        self.price = 0.00
        self.percent = 0.00

    def update(self):
        self.price, self.percent = self.__get_upd()

    def __get_upd(self):
        # ссылка на обновление данных json с сайта
        link = f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{self.name}?modules=price'

        # отправляем запрос на сайт по ссылке
        response = self.session.get(link, headers={'User-Agent':self.headers})

        # получаем json-массив
        arr = response.json()

        # список для возврата результата
        return_value = []

        # перебераем ключи словаря
        for key in self.value:
            n = path_values(arr, f'/**/{self.value[key]}/raw')

            if len(n):
                return_value.append(float(path_values(arr, f'/**/{self.value[key]}/raw')[0]))
                # возвращаем результат
            else:
                return_value = [0,0]

            return return_value



    def checkTicket(self):
        # ссылка на обновление данных json с сайта
        link = f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{self.name}?modules=price'

        # отправляем запрос на сайт по ссылке
        response = self.session.get(link, headers={'User-Agent':self.headers})

        # получаем json-массив
        arr = response.json()

        # разбираем ответ сервера
        answer = path_values(arr, 'quoteSummary/error/code')
        if len(answer) == 0:
            return True
        else:
            return False


