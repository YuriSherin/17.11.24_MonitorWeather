import info
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import datetime
from pprint import pprint


class Weather():
    """Класс для получения погоды в текущий момент времени.
    weather_date = {
    дата - тип datetime,
    восход солнца = тип datetime
    заход солнца - тпи datetime
    долгота дня - тип datetime
    }
    weather_info = {
    температура - тип int
    скорость ветра - тип int
    направление ветра - тип str
    давление - тип int
    влажность - тип int
    геомагнитная активность - тип int
    температура воды = тип int
    }
    """
    __instance = None       # вспомогательный атрибут, хранящий ссылку на экземпляр класса

    def __new__(cls, *args, **kwargs):
        """Метод гарантирует, что бедут создан только один экземпляр класса.
        Он получает ссылку на экземпляр класса, если такой экземпляр класса еще не создан,
        или просто возвращает ссылку на экземпляр класса."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, url:str):
        """Конструктор класса"""
        self.url_sity = url         # ссылка на сайт, с которого мы скрапингуем данные о погоде
        self.weather_data = {}      # словарь хранит в себе данные о дате запроса погоды
        self.weather_info = {}      # словарь хранит в себе информацию о погоде

    def get_weather(self):
        """Метод окрывает страницу сайта, считывает данные.
        При попытке открыть страницу сайта могут возникать ошибки,
        например страницы может просто не оказаться, мог смениться url и др."""
        try:  # попытка открыть страницу
            html = urlopen(self.url_sity)
            bs = BeautifulSoup(html.read(), 'html.parser')
            if not html.closed:
                html.close()
        except HTTPError as e:  # 404 Page Not Found, 500 Internal Server Error
            print(e)
        except URLError as e:  # ни один из указанных серверов недоступен
            print(e)
        else:   # ошибок не было. Продолжаем выполнение метода
            # получаем дату
            dt = datetime.datetime.now()    # получили текущую дату и время
            self.weather_data['date'] = dt.strftime('%Y-%m-%d %H:%M:%S')    # sqlite3 хранит дату в виде строки
            self.weather_data['day_count'] = int(f'{dt:%j}')    # номер дня в году

            # эти данные сохраняются на всякий случай )))
            self.weather_data['day'] = dt.day
            self.weather_data['month'] = dt.month
            self.weather_data['year'] = dt.year
            self.weather_data['hour'] = dt.hour
            self.weather_data['minute'] = dt.minute
            self.weather_data['second'] = dt.second

            widget_now = bs.find('div', {'class': {'widget now'}})      # тег содержит всю необходимую нам информацию

            """Получим время восхода солнца и время захода солнца"""
            wnd = widget_now.find_all('div', {'class':{'caption', 'time'}})
            time_sunrise = wnd[3].text
            if len(time_sunrise) < 5:
                time_sunrise = '0' + time_sunrise
            time_sunset = wnd[1].text
            if len(time_sunset) < 5:
                time_sunset = '0' + time_sunset
            self.weather_info['sunrise'] = time_sunrise
            self.weather_info['sunset'] = time_sunset

            # рассчитаем долготу дня
            time_rise = datetime.datetime.strptime(time_sunrise, '%H:%M')
            time_set = datetime.datetime.strptime(time_sunset, '%H:%M')
            len_day = time_set - time_rise      # долгота дня в секундах
            len_day_hour = len_day.seconds//3600
            len_day_min = (len_day.seconds - len_day_hour * 3600) // 60
            len_day_str = f'{str(len_day_hour)}:{str(len_day_min)}' if len_day_hour > 9 else f'0{str(len_day_hour)}:{str(len_day_min)}'
            self.weather_info['len_day'] = len_day_str

            wnd = widget_now.find('div', {'class': {'now-desc'}})
            # self.weather_info['state'] = wnd.text       # ????????????
            #
            wnd =widget_now.find('temperature-value', {})
            self.weather_info['temperature'] = int(wnd.attrs['value'])
            self.weather_info['temperature_measure'] = wnd.attrs['from-unit'].upper()

            wnd = widget_now.find_all('div', {'class': {'item-title', 'item-value', 'item-measure'}})

            """Ветер"""
            self.weather_info['wind'] = int(wnd[1].contents[0]['value'])
            self.weather_info['wind_measure'] = wnd[1].contents[0]['from-unit']
            if self.weather_info['wind_measure'] == 'ms':
                self.weather_info['wind_measure'] = 'м/сек'
            self.weather_info['wind_direct'] = wnd[2].text

            """Давление"""
            self.weather_info['pressure'] = int(wnd[4].contents[0]['value'])
            self.weather_info['pressure_measure'] = wnd[4].contents[0]['from-unit']
            if self.weather_info['pressure_measure'] == 'mmhg':
                self.weather_info['pressure_measure'] = 'мм.рт.ст.'

            """Влажность"""
            self.weather_info['humidity'] = int(wnd[7].contents[0])
            self.weather_info['humidity_measure'] = wnd[8].contents[0].text

            """Геомагнитная звисимость"""
            self.weather_info['geo_dependence'] = int(wnd[10].contents[0])
            get_tex= 'балл'
            if 1 < self.weather_info['geo_dependence'] < 5:
                get_tex = 'балла'
            elif self.weather_info['geo_dependence'] >= 5:
                get_tex = 'баллов'
            self.weather_info['geo_dependence_measure'] = f'{get_tex} из 9'

            """Вода"""
            self.weather_info['temperature_water'] = int(wnd[13].contents[0].attrs['value'])
            self.weather_info['temperature_water_measure'] = wnd[13].contents[0].attrs['from-unit'].upper()





if __name__ == '__main__':
    weather = Weather(info.url_weather)
    weather.get_weather()
    pprint(weather.weather_data)
    pprint((weather.weather_info))
