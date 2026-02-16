import requests
import time
import os
from datetime import datetime
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
    
    # Ambil waktu berdasarkan timezone kota (dalam detik)
    timezone_offset = data.get("timezone", 0)  # offset dalam detik dari UTC
    
    # Waktu UTC + offset timezone kota
    utc_time = datetime.utcnow()
    local_time = datetime.fromtimestamp(utc_time.timestamp() + timezone_offset)
    
    # Format tanggal: 15-Feb-2026
    tanggal = local_time.strftime("%d-%b-%Y")
    jam = local_time.strftime("%H:%M:%S")
    
    return f"🌤 {city}\n🌡 Suhu: {temp}°C\n💧 Kelembapan: {humidity}%\n📝 {desc}\n📅 {tanggal} {jam} (Waktu {city})"

def send_weather(context):
    for user_id, city in user_city.items():
        weather = get_weather(city)
        context.bot.send_message(chat_id=user_id, text=weather)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("set", set_city))

    job_queue = updater.job_queue
    job_queue.run_repeating(send_weather, interval=3600, first=10)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
