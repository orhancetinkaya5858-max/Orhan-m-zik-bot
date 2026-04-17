import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

# Günlük kayıtlarını ayarla
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot tokenini Render ortam değişkenlerinden al
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selam Orhan abi! SoundCloud sistemi aktif. Şarkı adını yaz, hemen getireyim.")

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.message.chat_id
    
    await update.message.reply_text(f"'{query}' aranıyor (SoundCloud)...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'default_search': 'scsearch1', # Sadece SoundCloud araması yapar
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        
        # Şarkıyı gönder
        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=open('music.mp3', 'rb'),
            caption=f"✅ {query} hazır! İyi dinlemeler abi."
        )
        
        # Dosyayı temizle
        os.remove('music.mp3')
        
    except Exception as e:
        await update.message.reply_text(f"Hata oluştu Orhan abi: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Komut ve mesaj işleyicileri
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_music))
    
    # Botu çalıştır
    application.run_polling()
