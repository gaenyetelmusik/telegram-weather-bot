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
    # Ambil forecast terdekat dari sekarang
    # =========================
    
    forecast_text = "\n🔮 Prediksi tidak tersedia."
    
    if forecast_data.get("cod") == "200":
        now_utc = datetime.utcnow().timestamp()
        
        closest_forecast = None
        min_diff = float("inf")
    
        for item in forecast_data["list"]:
            forecast_time = item["dt"]  # timestamp UTC
            diff = forecast_time - now_utc
            
            if diff > 0 and diff < min_diff:
                min_diff = diff
                closest_forecast = item
    
        if closest_forecast:
            next_temp = closest_forecast["main"]["temp"]
            next_desc = closest_forecast["weather"][0]["description"]
            
            forecast_time_local = datetime.fromtimestamp(
                closest_forecast["dt"] + timezone_offset
            )
            
            jam_forecast = forecast_time_local.strftime("%H:%M")
    
            forecast_text = (
                f"\n🔮 Perkiraan sekitar jam {jam_forecast}:\n"
                f"🌡 {next_temp}°C\n"
                f"📝 {next_desc}"
            )


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
