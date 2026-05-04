
import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp
from py_deezer import Deezer

# Deezer Kurulumu
arl = "21b89f42e41e63299105fc9c31ffef9ed21bf6912e767ed862d99d6979c3d5433147d18d5c940cacbdb6a1c61c0ae29e703042c9d19bb82c840743988983d27b471e2fb3b8cd654a5766c1ca54126c93a303a1b986074d1103b66f882b0bee51"
deezer_client = Deezer(arl=arl)

# Flask Web Sunucusu Kurulumu
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Aktif"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

# Loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hoş geldin Orhan abi! '/muzik Sanatçı Şarkı' yazarak indirme yapabilirsin.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın. Örnek: /muzik Müslüm Gürses Hatıralar")
        return

    query = " ".join(context.args)
    chat_id = update.message.chat_id
    
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor, hemen gönderiyorum Orhan abi...")
    
    # 1. ADIM: SOUNDCLOUD DENEMESİ
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'default_search': 'scsearch1',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        success = False
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                title = info.get('title', 'Bilinmeyen Şarkı')
                performer = info.get('uploader', 'Bilinmeyen Sanatçı')
                success = True
        except:
            # 2. ADIM: DEEZER DENEMESİ (Soundcloud bulamazsa)
            await msg.edit_text("🎵 SoundCloud'da bulunamadı, Deezer arşivine bakıyorum...")
            search_results = deezer_client.search_tracks(query)
            if search_results:
                track = search_results[0]
                deezer_client.download_track(track, output_dir=".", filename="music")
                title = track.get('title', 'Bilinmeyen')
                performer = track.get('artist', {}).get('name', 'Bilinmeyen')
                # Deezer indirdiğinde dosya ismi music.mp3 olmalı
                if os.path.exists("music.mp3"):
                    success = True

        if success:
            await context.bot.send_audio(
                chat_id=chat_id, 
                audio=open('music.mp3', 'rb'),
                title=title,
                performer=performer
            )
            await msg.delete()
        else:
            await msg.edit_text("Maalesef bu şarkıyı hiçbir yerde bulamadım abi.")
            
        if os.path.exists('music.mp3'):
            os.remove('music.mp3')
            
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu abi: {e}")

if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    if not TOKEN:
        print("KRİTİK HATA: BOT_TOKEN bulunamadı!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        
        print("Bot başlatıldı...")
        app.run_polling()
