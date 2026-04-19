import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp
from flask import Flask
from threading import Thread

# Hataları görmek için loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# --- Flask Web Sunucusu (Botun uyumaması için) ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot ayakta ve çalışıyor!"

def run_web():
    app_flask.run(host='0.0.0.0', port=8080)
# -------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hoş geldin! '/muzik Sanatçı Şarkı' yazarak indirme yapabilirsin.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın. Örnek: /muzik Müslüm Gürses Hatıralar")
        return

    query = " ".join(context.args)
    chat_id = update.message.chat_id
    
    await update.message.reply_text("Hoş geldiniz, istediğiniz müziği hemen gönderiyorum, iyi dinlemeler.")
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor...")
    
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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            
            title = info.get('title', 'Bilinmeyen Şarkı')
            performer = info.get('uploader', 'Bilinmeyen Sanatçı')

        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=open('music.mp3', 'rb'),
            title=title,
            performer=performer
        )
        await msg.delete() 
        
        if os.path.exists('music.mp3'):
            os.remove('music.mp3')
            
    except Exception as e:
        await update.message.reply_text(f"Hata oluştu abi: {e}")

if __name__ == '__main__':
    if not TOKEN:
        print("KRİTİK HATA: BOT_TOKEN Render ortam değişkenlerinde bulunamadı!")
    else:
        # Web sunucusunu başlat
        t = Thread(target=run_web)
        t.start()
        
        # Botu başlat
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        
        print("Bot ve Web Sunucusu başlatılıyor...")
        app.run_polling()
