import os
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp
from flask import Flask
from threading import Thread

# Hataları görmek için loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# Web sunucusu
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot ayakta!"
def run_web(): app_flask.run(host='0.0.0.0', port=8080)

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın.")
        return

    query = " ".join(context.args)
    chat_id = update.message.chat_id
    
    msg = await update.message.reply_text(f"🔍 '{query}' indiriliyor...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_music.%(ext)s',
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
            if 'entries' in info: info = info['entries'][0]
            
            # Şarkı adını temizle (Dosya sistemine uygun hale getir)
            title = info.get('title', 'muzik')
            clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
            new_filename = f"{clean_title}.mp3"
            
            # Dosyayı adlandır
            os.rename('temp_music.mp3', new_filename)

        # Dosyayı gönder
        with open(new_filename, 'rb') as audio_file:
            await context.bot.send_audio(chat_id=chat_id, audio=audio_file, title=title)
        
        await msg.delete()
        
        # Dosyayı temizle
        if os.path.exists(new_filename):
            os.remove(new_filename)
            
    except Exception as e:
        logging.error(f"Hata: {e}")
        await update.message.reply_text(f"Hata oluştu abi: {e}")

if __name__ == '__main__':
    t = Thread(target=run_web)
    t.start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('muzik', handle_muzik))
    app.run_polling()
