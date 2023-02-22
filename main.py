from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
meeting_date = os.environ['MEETING_DATE']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
    city_url = f'https://geoapi.qweather.com/v2/city/lookup?location={city}&key=9501d2e96cc54d47ae016ccdc6fb5b13'
    city_json = requests.get(city_url).json()
    if city_json.get('code') == '200':
        location_id = city_json.get('location')[0].get('id')
    else:
        print("Error, not get city's location id.")

    url = f'https://devapi.qweather.com/v7/weather/3d?location={location_id}&key=9501d2e96cc54d47ae016ccdc6fb5b13' 
    weather_json = requests.get(url).json()
    if weather_json.get('code') == '200':
        res = weather_json['daily'][0]
        weather = res['textDay'] + "（白天） ~ " + res['textNight'] + "（晚上）"
        temp = res['tempMin'] + ' ~ ' + res['tempMax'] + '°C'
        return weather, temp
    else:
        print("Error, not get weather info.")

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_meeting_date():
  next = datetime.strptime(str(date.today().year) + "-" + meeting_date, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
data = {"weather":{"value":wea},"temperature":{"value":temperature},"start_days":{"value":get_count()},"meeting_days":{"value":get_meeting_date()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
