import os
import logging
import requests
import csv
from io import StringIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read variables from .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_movies():
    try:
        res = requests.get(SHEET_CSV_URL)
        text = res.content.decode('utf-8')
        f = StringIO(text)
        reader = csv.DictReader(f)
        return [
            {
                "name": row['Movie Name'].strip(),
                "year": row['Year'].strip(),
                "quality": row['Quality'].strip(),
                "link": row['GP Link'].strip()
            }
            for row in reader
        ]
    except Exception as e:
        logger.error(f"Sheet error: {e}")
        return []

def is_admin(uid):
    return uid == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """🎬 *Welcome to Movie Bot!*

📽 Use `/search movie` to find movies.
🔐 Admins use `/admin` for tools."""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Use `/search movie_name`")
        return
    query = ' '.join(context.args).lower()
    movies = get_movies()
    results = [m for m in movies if m['name'].lower().startswith(query[:3])]
    if not results:
        await update.message.reply_text("❌ No match found.")
        return

    text = "🎬 *Found Movies:*\n\n"
    btns = []
    for m in results[:5]:
        text += f"🎥 {m['name']} ({m['year']}) - {m['quality']}\n"
        btns.append([InlineKeyboardButton(f"📥 Download", url=m['link'])])

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Not authorized.")
        return
    kb = [
        [InlineKeyboardButton("📋 View Sheet", url=SHEET_CSV_URL.replace("export?format=csv", "edit"))],
        [InlineKeyboardButton("➕ Add Movie Manual", callback_data="add_manual")]
    ]
    await update.message.reply_text("🔐 *Admin Panel*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Not allowed.")
        return
    if len(context.args) < 4:
        await update.message.reply_text("⚠️ Use: `/addmovie Name Year Quality Link`", parse_mode="Markdown")
        return
    name, year, quality, link = context.args[0], context.args[1], context.args[2], context.args[3]
    await update.message.reply_text(
        f"✅ Movie:\n🎬 {name} ({year}) {quality}\n🔗 {link}\n\n⚠️ Add this in Google Sheet manually.",
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addmovie", add_movie))
    print("✅ Movie Bot Started.")
    app.run_polling()

if __name__ == "__main__":
    main()