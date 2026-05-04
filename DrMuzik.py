import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp

# Flask Web Sunucusu (Render'da botun kapanmaması için şart)
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
    await update.message.reply_text("Hoş geldin Orhan abi! '/muzik Sanatçı Şarkı' yazarak her şeyi indirebilirsin.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yaz abi. Örnek: /muzik Müslüm Gürses")
        return

    query = " ".join(context.args)
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor, hemen gönderiyorum Orhan abi...")
    
    # GARANTİ ARAMA AYARI (YouTube üzerinden en sağlam kaynak)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'default_search': 'ytsearch1',
        'noplaylist': True,
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
            performer = info.get('uploader', 'Sanatçı')

        # Dosyayı Gönder
        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=open('music.mp3', 'rb'),
            title=title,
            performer=performer
        )
        await msg.delete()
        
        # Temizlik
        if os.path.exists('music.mp3'):
            os.remove('music.mp3')
            
    except Exception as e:
        await update.message.reply_text("Abi bu şarkıda bir sorun çıktı, ama başka bir tane hemen bulabilirim.")

if __name__ == '__main__':
    # Web sunucusunu başlat
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    if not TOKEN:
        print("HATA: BOT_TOKEN yok!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        
        print("Bot başarıyla başlatıldı!")
        app.run_polling()
