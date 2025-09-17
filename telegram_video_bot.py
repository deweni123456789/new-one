# file: telegram_video_bot.py

import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- BOT CONFIG ---
BOT_TOKEN = "8464050626:AAGVZG11RJ-oDW4OhWgUEM7oGr0TLX3Q9Yc"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# --- Download Function ---
def download_video(url: str) -> str:
    """Download video from URL using yt-dlp and return file path."""
    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).80s.%(ext)s"),
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a Facebook, Instagram, or YouTube link to download.")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not any(domain in url for domain in ["youtube.com", "youtu.be", "facebook.com", "instagram.com"]):
        await update.message.reply_text("❌ Unsupported link. Only FB, IG, YT allowed.")
        return

    await update.message.reply_text("⏳ Downloading... Please wait.")

    try:
        filepath = download_video(url)

        # Check file size limit
        if os.path.getsize(filepath) > 2 * 1024 * 1024 * 1024:
            await update.message.reply_text("❌ File too large for Telegram (max 2GB).")
            os.remove(filepath)
            return

        await update.message.reply_video(video=open(filepath, "rb"))
        os.remove(filepath)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")


# --- Main Function ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("🤖 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
