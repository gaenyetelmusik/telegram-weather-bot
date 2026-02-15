import requests
import time
import os
from telegram import Bot
from telegram.ext import Updater, CommandHandler

TOKEN = os.environ.get("BOT_TOKEN")
WEATHER_API = os.environ.get("WEATHER_API")

user_city = {}

def set_city(update, context):
    user_id = update.message.chat_id
    if len(context.args) == 0:
        update.message.reply_text("Gunakan: /set namakota")
        return
    city = " ".join(context.args)
    user_city[user_id] = city
    update.message.reply_text(f"Kota diset ke {city}. Update tiap 1 jam dimulai.")

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric&lang=id"
    data = requests.get(url).json()
    if data.get("cod") != 200:
        return "Kota tidak ditemukan."
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    return f"🌤 {city}\n🌡 Suhu: {temp}°C\n💧 Kelembapan: {humidity}%\n📝 {desc}"

def send_weather(context):
    for user_id, city in user_city.items():
        weather = get_weather(city)
        context.bot.send_message(chat_id=user_id, text=weather)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("set", set_city))

    job_queue = updater.job_queue
    job_queue.run_repeating(send_weather, interval=60, first=10)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

