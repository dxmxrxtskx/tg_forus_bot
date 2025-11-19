"""Main bot file."""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import BOT_TOKEN, is_authorized_user
from database import init_database
from keyboards import main_menu_keyboard

# Import all handlers
from handlers.movies import get_movies_handlers
from handlers.activities import get_activities_handlers
from handlers.trips import get_trips_handlers
from handlers.tiktok import get_tiktok_handlers
from handlers.photos import get_photos_handlers
from handlers.games import get_games_handlers
from handlers.sexual import get_sexual_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    """Handle /start command."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return
    
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\nВыберите раздел:",
        reply_markup=main_menu_keyboard()
    )

async def main_menu(update: Update, context):
    """Handle main menu callback."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "👋 Главное меню\n\nВыберите раздел:",
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "👋 Главное меню\n\nВыберите раздел:",
            reply_markup=main_menu_keyboard()
        )

async def unauthorized(update: Update, context):
    """Handle unauthorized users."""
    user_id = update.effective_user.id
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return False
    return True

def main():
    """Start the bot."""
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    
    # Register all section handlers
    for handler in get_movies_handlers():
        application.add_handler(handler)
    
    for handler in get_activities_handlers():
        application.add_handler(handler)
    
    for handler in get_trips_handlers():
        application.add_handler(handler)
    
    for handler in get_tiktok_handlers():
        application.add_handler(handler)
    
    for handler in get_photos_handlers():
        application.add_handler(handler)
    
    for handler in get_games_handlers():
        application.add_handler(handler)
    
    for handler in get_sexual_handlers():
        application.add_handler(handler)
    
    # Start bot
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

