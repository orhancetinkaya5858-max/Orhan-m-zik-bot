import os
import asyncio
import tempfile
import shutil
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

# YOUTUBE'A GİRİŞİ KESİNLİKLE YASAKLAYAN AYARLAR
YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "default_search": "scsearch", # Sadece SoundCloud araması
    # YouTube eklentisini (extractor) tamamen kapatıyoruz ki takılmasın
    "allowed_extractors": ["soundcloud.*", "generic"], 
    "nocheckcertificate": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

def download_song(query: str):
    tmpdir = tempfile.mkdtemp()
    outtmpl = os.path.join(tmpdir, "%(title)s.%(ext)s")

    opts = dict(YDL_OPTS)
    opts["outtmpl"] = outtmpl

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            # YouTube'a gitmemesi için aramanın başına SoundCloud kodunu zorla ekliyoruz
            info = ydl.extract_info(f"scsearch1:{query}", download=True)
            
            if not info or "entries" not in info or len(info["entries"]) == 0:
                return None, None
            
            entry = info["entries"][0]
            for f in os.listdir(tmpdir):
                if f.endswith(".mp3"):
                    return os.path.join(tmpdir, f), entry.get("title")
        except Exception as e:
            print(f"İndirme hatası: {e}")
            return None, None

    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # İstediğin genel hitap şekli
    await update.message.reply_text("Hoş geldiniz, şarkı adını yazınız.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Selam kontrolü
    text = update.message.text.lower()
    if text in ["s.a", "slm", "sa", "selam"]:
        await update.message.reply_text("Selamı kısaltmayalım Allah'ın selamını tam verelim lütfen 😊")
        return

    query = update.message.text.strip()
    msg = await update.message.reply_text("🔍 Arıyorum, lütfen bekleyiniz...")

    loop = asyncio.get_running_loop()
    mp3_path = None
    try:
        mp3_path, title = await loop.run_in_executor(None, download_song, query)

        if not mp3_path:
            await msg.edit_text("Üzgünüm, aradığınız şarkı bulunamadı.")
            return

        await msg.edit_text("Şarkı bulundu, gönderiliyor...")

        with open(mp3_path, "rb") as f:
            await update.message.reply_audio(audio=f, title=title)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"Bir hata oluştu: {e}")
    finally:
        if mp3_path:
            shutil.rmtree(os.path.dirname(mp3_path), ignore_errors=True)

def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN eksik!")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot aktif ve YouTube'dan uzak duruyor!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
