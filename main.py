import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import requests
import csv
from io import StringIO
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variable to store user states for adding movies
user_states = {}

def get_movies():
    """Fetch movies from Google Sheets CSV"""
    try:
        response = requests.get(SHEET_CSV_URL, timeout=10)
        response.raise_for_status()
        text = response.content.decode('utf-8')
        f = StringIO(text)
        reader = csv.DictReader(f)
        
        movies = []
        for row in reader:
            if row.get('Movie Name') and row.get('GP Link'):  # Ensure required fields exist
                movies.append({
                    "name": row.get('Movie Name', '').strip(),
                    "year": row.get('Year', '').strip(),
                    "quality": row.get('Quality', '').strip(),
                    "link": row.get('GP Link', '').strip()
                })
        
        logger.info(f"Successfully fetched {len(movies)} movies from sheet")
        return movies
    except requests.RequestException as e:
        logger.error(f"Network error fetching sheet: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing sheet data: {e}")
        return []

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    msg = f"""🎬 *Welcome to Movie Bot, {user.first_name}!*

🔍 Use `/search movie_name` to find movies
📝 Use `/list` to see all available movies
💡 Use `/help` for more commands

{"🔐 Use `/admin` for admin tools" if is_admin(user.id) else ""}

_Enjoy watching!_ 🍿"""
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """🆘 *Available Commands:*

🔍 `/search movie_name` - Search for movies
📝 `/list` - Show all movies (paginated)
🆘 `/help` - Show this help message

*How to search:*
• `/search avengers` - Find movies starting with "avengers"
• `/search 2023` - Find movies from 2023
• `/search hd` - Find HD quality movies

*Tips:*
• Search is case-insensitive
• You can search by movie name, year, or quality
• Results are limited to 10 movies per search"""

    if is_admin(update.effective_user.id):
        help_text += """

🔐 *Admin Commands:*
• `/admin` - Access admin panel
• `/addmovie` - Add movie via command
• `/stats` - View bot statistics"""

    await update.message.reply_text(help_text, parse_mode="Markdown")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search movies command handler"""
    if not context.args:
        await update.message.reply_text(
            "❗ Please provide a search term.\n\n*Usage:* `/search movie_name`\n*Example:* `/search avengers`",
            parse_mode="Markdown"
        )
        return

    query = ' '.join(context.args).lower()
    movies = get_movies()
    
    if not movies:
        await update.message.reply_text("❌ Unable to fetch movies. Please try again later.")
        return

    # Enhanced search - search in name, year, and quality
    results = []
    for movie in movies:
        if (query in movie['name'].lower() or 
            query in movie['year'].lower() or 
            query in movie['quality'].lower()):
            results.append(movie)

    if not results:
        await update.message.reply_text(
            f"❌ No movies found for '*{query}*'.\n\nTry:\n• Different spelling\n• Shorter search term\n• `/list` to see all movies",
            parse_mode="Markdown"
        )
        return

    # Limit results to 10
    results = results[:10]
    
    text = f"🎬 *Found {len(results)} movie(s) for '{query}':*\n\n"
    buttons = []
    
    for i, movie in enumerate(results, 1):
        text += f"{i}. 🎥 *{movie['name']}* ({movie['year']}) - {movie['quality']}\n"
        buttons.append([InlineKeyboardButton(
            f"📥 Download {movie['name'][:20]}{'...' if len(movie['name']) > 20 else ''}", 
            url=movie['link']
        )])

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def list_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all movies with pagination"""
    movies = get_movies()
    
    if not movies:
        await update.message.reply_text("❌ No movies available at the moment.")
        return

    page = 1
    if context.args and context.args[0].isdigit():
        page = int(context.args[0])

    per_page = 10
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    total_pages = (len(movies) + per_page - 1) // per_page

    if page > total_pages:
        await update.message.reply_text(f"❌ Page {page} doesn't exist. Total pages: {total_pages}")
        return

    page_movies = movies[start_idx:end_idx]
    
    text = f"📝 *Movie List (Page {page}/{total_pages}):*\n\n"
    
    for i, movie in enumerate(page_movies, start_idx + 1):
        text += f"{i}. 🎥 *{movie['name']}* ({movie['year']}) - {movie['quality']}\n"

    # Pagination buttons
    buttons = []
    nav_buttons = []
    
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"list_page_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"list_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)

    # Add download buttons for current page
    for movie in page_movies:
        buttons.append([InlineKeyboardButton(
            f"📥 {movie['name'][:25]}{'...' if len(movie['name']) > 25 else ''}", 
            url=movie['link']
        )])

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You are not authorized to use admin commands.")
        return

    movies = get_movies()
    keyboard = [
        [InlineKeyboardButton("📋 View/Edit Sheet", url=SHEET_CSV_URL.replace("export?format=csv", "edit"))],
        [InlineKeyboardButton("➕ Add Movie", callback_data="add_movie_start")],
        [InlineKeyboardButton("📊 Statistics", callback_data="show_stats")]
    ]
    
    await update.message.reply_text(
        f"🔐 *Admin Panel*\n\n📊 Total Movies: {len(movies)}\n🤖 Bot Status: Active",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Not authorized.")
        return

    movies = get_movies()
    
    # Count by quality
    quality_count = {}
    year_count = {}
    
    for movie in movies:
        quality = movie['quality'] or 'Unknown'
        year = movie['year'] or 'Unknown'
        
        quality_count[quality] = quality_count.get(quality, 0) + 1
        year_count[year] = year_count.get(year, 0) + 1

    stats_text = f"📊 *Bot Statistics*\n\n"
    stats_text += f"🎬 Total Movies: {len(movies)}\n\n"
    
    stats_text += "*By Quality:*\n"
    for quality, count in sorted(quality_count.items()):
        stats_text += f"• {quality}: {count}\n"
    
    stats_text += "\n*Recent Years:*\n"
    recent_years = sorted(year_count.items(), reverse=True)[:5]
    for year, count in recent_years:
        stats_text += f"• {year}: {count}\n"

    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def add_movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add movie via command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Not authorized.")
        return

    if len(context.args) < 4:
        await update.message.reply_text(
            "⚠️ *Usage:* `/addmovie \"Movie Name\" Year Quality Link`\n\n"
            "*Example:* `/addmovie \"Avengers Endgame\" 2019 \"HD 1080p\" https://drive.google.com/...`",
            parse_mode="Markdown"
        )
        return

    name = context.args[0]
    year = context.args[1]
    quality = context.args[2]
    link = context.args[3]

    confirmation_text = f"✅ *Movie Details:*\n\n"
    confirmation_text += f"🎬 *Name:* {name}\n"
    confirmation_text += f"📅 *Year:* {year}\n"
    confirmation_text += f"🎥 *Quality:* {quality}\n"
    confirmation_text += f"🔗 *Link:* {link}\n\n"
    confirmation_text += "⚠️ *Please add this movie to the Google Sheet manually.*\n\n"
    confirmation_text += f"📋 [Open Google Sheet]({SHEET_CSV_URL.replace('export?format=csv', 'edit')})"

    await update.message.reply_text(confirmation_text, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("list_page_"):
        page = int(query.data.split("_")[-1])
        movies = get_movies()
        
        per_page = 10
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        total_pages = (len(movies) + per_page - 1) // per_page

        page_movies = movies[start_idx:end_idx]
        
        text = f"📝 *Movie List (Page {page}/{total_pages}):*\n\n"
        
        for i, movie in enumerate(page_movies, start_idx + 1):
            text += f"{i}. 🎥 *{movie['name']}* ({movie['year']}) - {movie['quality']}\n"

        buttons = []
        nav_buttons = []
        
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"list_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"list_page_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)

        for movie in page_movies:
            buttons.append([InlineKeyboardButton(
                f"📥 {movie['name'][:25]}{'...' if len(movie['name']) > 25 else ''}", 
                url=movie['link']
            )])

        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    elif query.data == "show_stats":
        movies = get_movies()
        quality_count = {}
        
        for movie in movies:
            quality = movie['quality'] or 'Unknown'
            quality_count[quality] = quality_count.get(quality, 0) + 1

        stats_text = f"📊 *Statistics*\n\n🎬 Total: {len(movies)}\n\n*By Quality:*\n"
        for quality, count in sorted(quality_count.items()):
            stats_text += f"• {quality}: {count}\n"

        await query.edit_message_text(stats_text, parse_mode="Markdown")

    elif query.data == "add_movie_start":
        await query.edit_message_text(
            "➕ *Add New Movie*\n\n"
            "Use: `/addmovie \"Name\" Year Quality Link`\n\n"
            "Or manually add to the Google Sheet:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📋 Open Sheet", url=SHEET_CSV_URL.replace("export?format=csv", "edit"))
            ]])
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Main function to run the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return

    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("list", list_movies))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addmovie", add_movie_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    app.add_error_handler(error_handler)

    # Log startup
    logger.info("🎬 Movie Bot Started Successfully!")
    print("✅ Movie Bot is running...")

    # Run the bot
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()