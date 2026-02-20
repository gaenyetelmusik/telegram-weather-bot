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
    
    # Konfirmasi kota tersimpan
    update.message.reply_text(f"Kota diset ke {city}. Update tiap 1 jam dimulai.")
    
    # Langsung kirim cuaca saat ini
    weather = get_weather(city)
    update.message.reply_text(weather)

def get_weather(city):
    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric&lang=id"
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API}&units=metric&lang=id"
    
    current_data = requests.get(current_url).json()
    forecast_data = requests.get(forecast_url).json()

    if current_data.get("cod") != 200:
        return "Kota tidak ditemukan."
    
    temp = current_data["main"]["temp"]
    desc = current_data["weather"][0]["description"]
    humidity = current_data["main"]["humidity"]

    timezone_offset = current_data.get("timezone", 0)
    utc_time = datetime.utcnow()
    local_time = datetime.fromtimestamp(utc_time.timestamp() + timezone_offset)

    tanggal = local_time.strftime("%d-%b-%Y")
    jam = local_time.strftime("%H:%M:%S")

    # =========================
    # Ambil prediksi 1 interval ke depan (±3 jam)
    # =========================
    if forecast_data.get("cod") == "200":
        next_forecast = forecast_data["list"][1]  # data berikutnya
        next_temp = next_forecast["main"]["temp"]
        next_desc = next_forecast["weather"][0]["description"]
        forecast_text = f"\n🔮 Perkiraan 3 jam lagi:\n🌡 {next_temp}°C\n📝 {next_desc}"
    else:
        forecast_text = "\n🔮 Prediksi tidak tersedia."

    return (
        f"🌤 {city}\n"
        f"🌡 Suhu: {temp}°C\n"
        f"💧 Kelembapan: {humidity}%\n"
        f"📝 {desc}\n"
        f"📅 {tanggal} {jam} (Waktu {city})"
        f"{forecast_text}"
    )


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
