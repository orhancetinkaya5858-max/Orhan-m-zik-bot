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

# YouTube engellerini aşmak ve SoundCloud'u zorlamak için en sağlam ayarlar
YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "default_search": "scsearch", # Önce SoundCloud'da ara (YouTube engeline takılmaz)
    "nocheckcertificate": True,
    "geo_bypass": True,
    "source_address": "0.0.0.0",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
            # 1. Şans: SoundCloud üzerinden ara (Genelde hata vermez)
            info = ydl.extract_info(f"scsearch1:{query}", download=True)
            
            # Eğer SoundCloud'da bulamazsa, YouTube üzerinden dener
            if not info or not info.get("entries"):
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                
        except Exception as e:
            print(f"Hata: {e}")
            return None, None

    if info and "entries" in info and len(info["entries"]) > 0:
        entry = info["entries"][0]
        # İndirilen dosyayı bulalım
        for f in os.listdir(tmpdir):
            if f.endswith(".mp3"):
                return os.path.join(tmpdir, f), entry.get("title")

    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selamı kısaltmayalım Allah'ın selamını tam verelim lütfen 😊\n\nHoş geldin Orhan usta! Şarkı adını yaz, senin için hemen bulayım.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Selam kontrolü
    text = update.message.text.lower()
    if text in ["s.a", "slm", "sa", "selam"]:
        await update.message.reply_text("Selamı kısaltmayalım Allah'ın selamını tam verelim lütfen 😊")
        return

    query = update.message.text.strip()
    msg = await update.message.reply_text("🔍 Arıyorum Orhan abi, bir saniye...")

    loop = asyncio.get_running_loop()
    mp3_path = None
    try:
        mp3_path, title = await loop.run_in_executor(None, download_song, query)

        if not mp3_path:
            await msg.edit_text("Aradım ama bulamadım usta. YouTube engeline takılmış olabiliriz.")
            return

        await msg.edit_text("Buldum! Gönderiyorum...")

        with open(mp3_path, "rb") as f:
            await update.message.reply_audio(audio=f, title=title)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"Bir hata oluştu usta: {e}")

    finally:
        if mp3_path:
            try:
                shutil.rmtree(os.path.dirname(mp3_path), ignore_errors=True)
            except:
                pass

def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN eksik! Render ayarlarından kontrol et.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Orhan usta için hazır!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
                
