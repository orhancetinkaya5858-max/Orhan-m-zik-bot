import os
import asyncio
import yt_dlp
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import Response
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Render panelindeki BOT_TOKEN kutusundan şifreyi otomatik çeker
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "drmuzik-bot-1.onrender.com")
WEBHOOK_URL = f"https://{HOST}/webhook"

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

async def sarki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Şarkı adı yaz kral! Örn: /sarki Azer Bülbül")
        return

    query = " ".join(context.args)
    temp_id = uuid.uuid4().hex[:5]
    # Telefondan en hızlı ve hatasız inen format
    out_tmpl = f"track_{temp_id}.%(ext)s"
    
    msg = await update.message.reply_text(f"📥 '{query}' aranıyor, az bekle...")

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_tmpl,
            "noplaylist": True,
            "quiet": True,
            "geo_bypass": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            video_info = info['entries'][0]
            title = video_info.get("title", "Şarkı")
            filename = ydl.prepare_filename(video_info)

        # Müzik dosyasını gönderiyoruz
        with open(filename, "rb") as audio:
            await update.message.reply_audio(audio=audio, title=title, caption=f"🎵 {title} - Dr.Müzik Sunar")
        
        await msg.delete()
        if os.path.exists(filename): os.remove(filename)

    except Exception as e:
        print(f"Hata: {e}")
        await msg.edit_text("❌ İndirme başarısız. YouTube engeline takılmış olabiliriz.")

application.add_handler(CommandHandler("sarki", sarki))
application.add_handler(CommandHandler("start", lambda u,c: u.message.reply_text("Bot aktif Orhan abi! /sarki yazıp yanına şarkı adını ekle.")))

@app.post("/webhook")
async def webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, application.bot)
    asyncio.create_task(application.process_update(update))
    return Response(content="OK")

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
