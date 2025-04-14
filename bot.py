from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
import subprocess

VIDEO_URL, STREAM_KEY = range(2)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send me the video URL you want to stream to Facebook Live.")
    return VIDEO_URL

async def get_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id] = {'video_url': update.message.text}
    await update.message.reply_text("🔑 Now send me your Facebook **Stream Key**.")
    return STREAM_KEY

async def get_stream_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_data[user_id]['stream_key'] = update.message.text

    video_url = user_data[user_id]['video_url']
    stream_key = user_data[user_id]['stream_key']
    fb_url = f"rtmps://live-api-s.facebook.com:443/rtmp/{stream_key}"

    await update.message.reply_text("🚀 Starting the stream to Facebook...")

    cmd = [
        'ffmpeg',
        '-re', '-i', video_url,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-f', 'flv',
        fb_url
    ]

    subprocess.Popen(cmd)
    await update.message.reply_text("✅ Streaming started! Enjoy 🎥")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Canceled.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token("7681013349:AAGJqaVenEszmq1amV4VUhjVddN-ftx1zOc").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            VIDEO_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_video_url)],
            STREAM_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stream_key)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()
