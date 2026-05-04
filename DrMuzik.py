import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp
from py_deezer import Deezer

# Deezer İstemcisi Tanımlama (Tam istediğin yer)
arl_code = "21b89f42e41e63299105fc9c31ffef9ed21bf6912e767ed862d99d6979c3d5433147d18d5c940cacbdb6a1c61c0ae29e703042c9d19bb82c840743988983d27b471e2fb3b8cd654a5766c1ca54126c93a303a1b986074d1103b66f882b0bee51"
deezer_client = Deezer(arl=arl_code)

# Flask Sunucusu (Render kapanmaması için)
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
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"🔍 '{query}' aranıyor, lütfen bekleyin...")
    
    success = False
    file_path = "music.mp3"

    # 1. ADIM: DEEZER İLE İNDİRME
    try:
        search = deezer_client.search_tracks(query)
        if search:
            track = search[0]
            deezer_client.download_track(track, output_dir=".", filename="music")
            # Dosya kontrolü ve isimlendirme
            if os.path.exists("music.mp3"):
                success = True
            elif os.path.exists("music"):
                os.rename("music", "music.mp3")
                success = True
            
            title = track.get('title', 'Bilinmeyen')
            performer = track.get('artist', {}).get('name', 'Sanatçı')
    except Exception as e:
        print(f"Deezer hatası: {e}")

    # 2. ADIM: GÖNDERİM
    if success and os.path.exists(file_path):
        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=open(file_path, 'rb'),
            title=title,
            performer=performer
        )
        await msg.delete()
        os.remove(file_path)
    else:
        await msg.edit_text("Üzgünüm, şarkı bulunamadı veya bir hata oluştu.")

if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    if TOKEN:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        app.run_polling()
