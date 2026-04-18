import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

# Hataları görmek için loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selam Orhan abi! SoundCloud sistemi aktif. Şarkı adını yaz, hemen getireyim.")

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.message.chat_id
    
    # Kullanıcıya mesaj gönder
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
        # İndirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        
        # Dosyayı gönder
        await context.bot.send_audio(chat_id=chat_id, audio=open('music.mp3', 'rb'))
        await msg.delete() # 'Aranıyor' mesajını sil
        
        # Dosyayı temizle
        if os.path.exists('music.mp3'):
            os.remove('music.mp3')
            
    except Exception as e:
        await update.message.reply_text(f"Hata oluştu abi: {e}")

if __name__ == '__main__':
    if not TOKEN:
        print("KRİTİK HATA: BOT_TOKEN Render ortam değişkenlerinde bulunamadı!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_music))
        print("Bot başlatılıyor...")
        app.run_polling()
