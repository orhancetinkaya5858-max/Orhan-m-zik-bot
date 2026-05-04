import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp
from deezer import Client # Kütüphane ismini listene göre düzelttim

# Deezer Kurulumu
arl_code = "21b89f42e41e63299105fc9c31ffef9ed21bf6912e767ed862d99d6979c3d5433147d18d5c940cacbdb6a1c61c0ae29e703042c9d19bb82c840743988983d27b471e2fb3b8cd654a5766c1ca54126c93a303a1b986074d1103b66f882b0bee51"
deezer_client = Client(max_retries=3) # Standart deezer-python kullanımı

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Aktif"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hoş geldiniz! '/muzik Sanatçı Şarkı' yazarak indirme yapabilirsiniz.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın.")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor, lütfen bekleyin...")
    
    file_path = "music.mp3"

    try:
        # DEEZER ARAMA
        search_results = deezer_client.search(query)
        if search_results:
            track = search_results[0]
            # Not: deezer-python indirme için track.preview kullanabilir veya yt-dlp'ye paslayabilir
            # En sağlamı: Deezer linkini yt-dlp ile indirmek
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'music.%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([track.link])
            
            await update.message.reply_audio(
                audio=open(file_path, 'rb'),
                title=track.title,
                performer=track.artist.name
            )
            await msg.delete()
        else:
            await msg.edit_text("Maalesef şarkı bulunamadı.")
            
    except Exception as e:
        await msg.edit_text(f"Bir hata oluştu: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        app.run_polling()
