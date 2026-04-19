import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import yt_dlp

# Hataları görmek için loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hoş geldin! '/muzik Sanatçı Şarkı' yazarak indirme yapabilirsin.")

async def handle_muzik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Eğer kullanıcı hiçbir şey yazmadıysa uyarı ver
    if not context.args:
        await update.message.reply_text("Lütfen bir şarkı ismi yazın. Örnek: /muzik Müslüm Gürses Hatıralar")
        return

    # Kullanıcının gönderdiği şarkı ismini birleştir
    query = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Kullanıcıya yanıt ver
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
        # İndirme ve Bilgi Çekme
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            # Eğer liste gelirse ilkini al
            if 'entries' in info:
                info = info['entries'][0]
            
            title = info.get('title', 'Bilinmeyen Şarkı')
            performer = info.get('uploader', 'Bilinmeyen Sanatçı')

        # Dosyayı gönder (Başlık ve Sanatçı bilgisiyle)
        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=open('music.mp3', 'rb'),
            title=title,
            performer=performer
        )
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
        
        # Komutları tanımlıyoruz
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('muzik', handle_muzik))
        
        print("Bot başlatılıyor...")
        app.run_polling()
