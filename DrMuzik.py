import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Aktif"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hoş geldiniz! '/muzik şarkı adı' yazarak indirebilirsiniz.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın.")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor...")
    
    # Dosya adı şablonu
    output_template = "music_file.%(ext)s"

    try:
        ydl_opts = {
            # SoundCloud araması için en stabil format ayarı
            'format': 'bestaudio', 
            'outtmpl': output_template,
            'default_search': 'scsearch',
            'noplaylist': True,
            'nocheckcertificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Şarkıyı aratıp indiriyoruz
            info = ydl.extract_info(f"scsearch1:{query}", download=True)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
                filename = ydl.prepare_filename(video_info)
                title = video_info.get('title', query)
                performer = video_info.get('uploader', 'SoundCloud')
            else:
                filename = ydl.prepare_filename(info)
                title = info.get('title', query)
                performer = info.get('uploader', 'SoundCloud')

        # İndirilen dosyanın uzantısını bulup kontrol ediyoruz
        actual_filename = None
        for f in os.listdir('.'):
            if f.startswith("music_file."):
                actual_filename = f
                break

        if actual_filename and os.path.exists(actual_filename):
            await update.message.reply_audio(
                audio=open(actual_filename, 'rb'), 
                title=title,
                performer=performer
            )
            await msg.delete()
            os.remove(actual_filename)
        else:
            await msg.edit_text("Müzik dosyası bulunamadı.")

    except Exception as e:
        await msg.edit_text(f"Hata oluştu: {e}")
        # Kalıntı dosya varsa temizle
        for f in os.listdir('.'):
            if f.startswith("music_file."):
                try: os.remove(f)
                except: pass

if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        app.run_polling()
