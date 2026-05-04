import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp
from deezer import Client

# Deezer Ayarı
deezer_client = Client()

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Aktif"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hoş geldiniz! '/muzik şarkı-adı' şeklinde arama yapabilirsiniz.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın.")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor...")
    
    file_path = "music.mp3"

    try:
        # Önce Deezer'da ara
        search = deezer_client.search(query)
        if search:
            track = search[0]
            # En sağlam yöntem: Deezer linkini yt-dlp ile indirmek
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
            await msg.edit_text("Şarkı bulunamadı.")
            
    except Exception as e:
        await msg.edit_text(f"Hata oluştu: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        app.run_polling()
