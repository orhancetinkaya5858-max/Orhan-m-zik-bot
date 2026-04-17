import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logları ayarla ki hatayı görelim
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Orhan abi, sistem SoundCloud üzerinden hazır!")

if __name__ == '__main__':
    if not TOKEN:
        print("KRİTİK HATA: BOT_TOKEN Render ayarlarında bulunamadı!")
    else:
        print("Bot başlatılıyor...")
        try:
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler('start', start))
            print("Bot başarıyla bağlandı, komutlar bekleniyor.")
            app.run_polling()
        except Exception as e:
            print(f"BAĞLANTI HATASI: {e}")
