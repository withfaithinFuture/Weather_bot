import requests
import telebot
from telebot import types
from datetime import datetime
import os



class WeatherBot:

    # Получение URL и обозначение headers
    URL_kr = 'https://yandex.ru/pogoda/?lat=55.8310051&lon=37.33039856'
    URL_msc = 'https://yandex.ru/pogoda/?via=hl'
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    headers = {
        'User-Agent': 'YOUR HEADERS'}

    # Конструктор, содержащий API бота, создание бота, вызов метода, который будет проверять погоду
    def __init__(self, api_key):
        self.api_key = api_key
        self.bot = telebot.TeleBot(api_key)
        self.init_commands()

    # Главный метод, который отвечает на команду "старт". Создает 2 кнопки в меню и спрашивает, чего хочет пользователь. Передает данные в следующий метод, который будет выводить данные погоды
    def init_commands(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_kr = types.KeyboardButton('Погода в Красногорске')
            button_msc = types.KeyboardButton('Погода в Москве')
            keyboard.add(button_kr, button_msc)

            self.bot.send_message(message.chat.id, 'Здравствуйте! 👋🏻\n\nУ вас действует <b>бесплатный пробный период</b> на <u>30 дней</u>: когда вам понравятся функции бота, вы сможете продлевать его услуги <u>всего</u> за 100 рублей в месяц :)\n\nПо вопросам оплаты обращаться к кому-то\n\nВ каком городе хотите узнать погоду?', reply_markup=keyboard, parse_mode='html')

        # Метод, передающий данные Красногорска
        @self.bot.message_handler(func=lambda message: message.text == 'Погода в Красногорске')
        def handle_weather_kr(message):
            self.handle_weather(message, city="Красногорске")

        # Метод, передающий данные Москвы
        @self.bot.message_handler(func=lambda message: message.text == 'Погода в Москве')
        def handle_weather_moscow(message):
            self.handle_weather(message, city="Москве")

    conditions_dict = {
        'clear': 'Ясно ☀️',
        'partly-cloudy': 'Малооблачно 🌤',
        'cloudy': 'Облачно с прояснениями ⛅️',
        'overcast': 'Пасмурно ☁️',
        'light-rain': 'Небольшой дождь 🌧',
        'rain': 'Дождь 🌧',
        'heavy-rain': 'Сильный дождь 🌧',
        'showers': 'Ливень 🌧',
        'wet-snow': 'Дождь со снегом 🌧 🌨',
        'light-snow': 'Небольшой снег 🌨',
        'snow': 'Снег 🌨',
        'snow-showers': 'Снегопад 🌨',
        'hail': 'Град 🌧 🧊',
        'thunderstorm': 'Гроза 🌩',
        'thunderstorm-with-rain': 'Дождь с грозой ⛈',
        'thunderstorm-with-hail': 'Гроза с градом 🌩 🧊'
    }

    months = {
        '01': "Января",
        '02': "Февраля",
        '03': "Марта",
        '04': "Апреля",
        '05': "Мая",
        '06': "Июня",
        '07': "Июля",
        '08': "Августа",
        '09': "Сентября",
        '10': "Октября",
        '11': "Ноября",
        '12': "Декабря"
    }

    def get_hourly_forecast(self, data):
        forecast_today = data['forecasts'][0]['hours']
        hourly_forecast = []

        for hour_data in forecast_today:
            if len(hour_data['hour']) == 1:

                translated_condition = self.conditions_dict.get(hour_data['condition'])

                hourly_forecast.append({f"0{hour_data['hour']}:00": f"{hour_data['temp']}°\n{translated_condition}\nВероятность осадков - {hour_data['prec_prob']}%\n💦 - {hour_data['humidity']}%"})

            elif len(hour_data['hour']) == 2:

                translated_condition = self.conditions_dict.get(hour_data['condition'])

                hourly_forecast.append({f"{hour_data['hour']}:00": f"{hour_data['temp']}°\n{translated_condition}\nВероятность осадков - {hour_data['prec_prob']}%\n💦 - {hour_data['humidity']}%"})

        hourly_forecast_str = '\n'.join([f"{hour}:\n{data}\n" for hour_data in hourly_forecast for hour, data in hour_data.items()])

        return hourly_forecast_str

    def get_week_forecast(self, data):
        forecast_7days = {
            f'{data["forecasts"][0]["date"]}': f'{data["forecasts"][0]["parts"]["day"]["temp_max"]}°\n{self.conditions_dict.get(data["forecasts"][0]["parts"]["day"]["condition"])}',

            f'{data["forecasts"][1]["date"]}': f'{data["forecasts"][1]["parts"]["day"]["temp_max"]}°\n{self.conditions_dict.get(data["forecasts"][1]["parts"]["day"]["condition"])}',

            f'{data["forecasts"][2]["date"]}': f'{data["forecasts"][2]["parts"]["day"]["temp_max"]}°\n{self.conditions_dict.get(data["forecasts"][2]["parts"]["day"]["condition"])}',

            f'{data["forecasts"][3]["date"]}': f'{data["forecasts"][3]["parts"]["day"]["temp_max"]}°\n{self.conditions_dict.get(data["forecasts"][3]["parts"]["day"]["condition"])}',

            f'{data["forecasts"][4]["date"]}': f'{data["forecasts"][4]["parts"]["day"]["temp_max"]}°\n{self.conditions_dict.get(data["forecasts"][4]["parts"]["day"]["condition"])}',

            f'{data["forecasts"][5]["date"]}': f'{data["forecasts"][5]["parts"]["day"]["temp_max"]}°\n{self.conditions_dict.get(data["forecasts"][5]["parts"]["day"]["condition"])}',

            f'{data["forecasts"][6]["date"]}': f'{data["forecasts"][6]["parts"]["day"]["temp_max"]}°\n{self.conditions_dict.get(data["forecasts"][0]["parts"]["day"]["condition"])}'

        }

        formatted_forecast_data = {}
        for date, temp in forecast_7days.items():
            date_str = date.split('-')
            month = self.months.get(date_str[1])
            day = date_str[-1]
            formatted_data = day + ' ' + month
            formatted_forecast_data[formatted_data] = temp

        week_forecast_str = '\n'.join([f"{day[:-1]}я: {data}\n" for day, data in formatted_forecast_data.items()])

        return week_forecast_str

    def get_weather_kr(self):
        url = 'https://api.weather.yandex.ru/v2/forecast?lat=55.8310051&lon=37.33039856&hours=true&extra=false'
        Api = "YOUR API"
        headers_API = {'X-Yandex-API-Key': f'{Api}'}
        params = {'lang': "ru_RU"}
        response = requests.get(url, headers=headers_API, params=params)
        data = response.json()
        kr_week_forecast = self.get_week_forecast(data)
        kr_hourly_forecast = self.get_hourly_forecast(data)
        return kr_hourly_forecast, kr_week_forecast

    def get_weather_msc(self):
        url = 'https://api.weather.yandex.ru/v2/forecast?lat=55.75554452682161&lon=37.61990478791612&hours=true&extra=false'
        Api = "YOUR API"
        headers_API = {'X-Yandex-API-Key': f'{Api}'}
        params = {'lang': "ru_RU"}
        response = requests.get(url, headers=headers_API, params=params)
        data = response.json()
        msc_week_forecast = self.get_week_forecast(data)
        msc_hourly_forecast = self.get_hourly_forecast(data)
        return msc_hourly_forecast, msc_week_forecast

    # Выводит данные погоды пользователю
    def handle_weather(self, message, city):
        if city == 'Красногорске':
            forecast_today, forecast_7days = self.get_weather_kr()

        elif city == 'Москве':
            forecast_today, forecast_7days = self.get_weather_msc()

        response = f"<b><u>Погода в {city} на сегодня:</u></b>\n\n{forecast_today}\n\n<b><u>Погода в {city} на ближайшие 7 дней:</u></b>\n\n{forecast_7days}"
        self.bot.send_message(message.chat.id, response, parse_mode='html')



API_KEY = 'BOT API'
weather_bot = WeatherBot(API_KEY)
weather_bot.init_commands()
weather_bot.bot.polling(none_stop=True)
