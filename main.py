import os
import subprocess
import traceback
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters # type: ignore

TOKEN = "7493471925:AAGbuzA-3s8QImQE1aLAxDCoS-b9yt3bj1A"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Please send a valid YouTube link.")
        return

    await update.message.reply_text("⏳ Downloading the audio…")

    try:
        output_filename = "yt_audio.%(ext)s"
        command = [
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "-o", output_filename,
            url
        ]
        subprocess.run(command, check=True)

        # Caută fișierul mp3 generat
        mp3_file = None
        for file in os.listdir():
            if file.startswith("yt_audio") and file.endswith(".mp3"):
                mp3_file = file
                break

        if not mp3_file:
            await update.message.reply_text("❌ The MP3 file could not be generated.")
            return

        # Verificăm dimensiunea fișierului
        size_mb = os.path.getsize(mp3_file) / (1024 * 1024)
        if size_mb > 50:
            await update.message.reply_text("❗ The file is too large (>50MB) to be sent via Telegram.")
            os.remove(mp3_file)
            return

        # Trimitem fișierul MP3 în Telegram
        with open(mp3_file, 'rb') as f:
            await update.message.reply_audio(f)

        os.remove(mp3_file)

    except subprocess.CalledProcessError as e:
        await update.message.reply_text("❌ Download error. Please check the link.")
    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        await update.message.reply_text("❌ The MP3 file could not be generated. Please contact me: @dorin_ciobanu")
        # print("❌ Eroare detaliată:\n", error_message)
        # await update.message.reply_text("❌ A apărut o eroare. Verific terminalul pentru detalii.")

# Setup bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 The bot is running…")
app.run_polling()