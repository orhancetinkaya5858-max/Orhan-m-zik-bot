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
    await update.message.reply_text("Hoş geldiniz! '/muzik şarkı adı' yazarak en hızlı şekilde indirebilirsiniz.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın.")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor ve doğrudan indiriliyor...")
    output_template = "music_file.%(ext)s"

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'default_search': 'scsearch1',
            'nocheckcertificate': True,
            'external_downloader_args': ['-loglevel', 'panic'],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            await update.message.reply_audio(
                audio=open(filename, 'rb'), 
                title=info.get('title', query),
                performer=info.get('uploader', 'SoundCloud')
            )
            await msg.delete()
            os.remove(filename)
        else:
            await msg.edit_text("Müzik dosyası bulunamadı.")

    except Exception as e:
        await msg.edit_text(f"Hata oluştu: {e}")
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
