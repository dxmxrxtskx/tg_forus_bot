"""Photo category handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_photo_categories, get_photo_category, add_photo_category, update_photo_category
)
from keyboards import (
    photos_menu_keyboard, list_keyboard, cancel_keyboard
)

logger = logging.getLogger(__name__)

TITLE, LINK, DESCRIPTION = range(3)

async def photos_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show photos menu."""
    query = update.callback_query if update.callback_query else None
    
    categories = get_photo_categories()
    
    if not categories:
        text = "📸 Раздел фотографий\n\nСписок категорий пуст"
        keyboard = photos_menu_keyboard()
    else:
        text = "📸 Раздел фотографий\n\nВыберите категорию:"
        items = [{'id': c['id'], 'title': c['title']} for c in categories]
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        base_keyboard = list_keyboard(items, "photo_cat", 0, 10)
        # Add "Add category" button
        new_keyboard = base_keyboard.inline_keyboard.copy()
        new_keyboard.append([InlineKeyboardButton("➕ Добавить категорию", callback_data="photos:add")])
        new_keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        keyboard = InlineKeyboardMarkup(new_keyboard)
    
    if query:
        await query.answer()
        await query.edit_message_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)

async def photo_category_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show photo category detail."""
    query = update.callback_query
    await query.answer()
    
    category_id = int(query.data.split(":")[-1])
    category = get_photo_category(category_id)
    
    if not category:
        await query.edit_message_text("Категория не найдена")
        return
    
    text = f"📸 {category['title']}\n"
    if category['link']:
        text += f"🔗 {category['link']}\n"
    if category['description']:
        text += f"📝 {category['description']}"
    
    from keyboards import photos_menu_keyboard
    await query.edit_message_text(text, reply_markup=photos_menu_keyboard())

async def photo_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding photo category."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название категории:",
        reply_markup=cancel_keyboard()
    )
    return TITLE

async def photo_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get category title."""
    context.user_data['photo_title'] = update.message.text
    await update.message.reply_text(
        "Добавить ссылку? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return LINK

async def photo_add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get category link."""
    if update.message.text and update.message.text != "/skip":
        context.user_data['photo_link'] = update.message.text
    else:
        context.user_data['photo_link'] = None
    
    await update.message.reply_text(
        "Добавить описание? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return DESCRIPTION

async def photo_add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save photo category."""
    if update.message.text and update.message.text != "/skip":
        description = update.message.text
    else:
        description = None
    
    title = context.user_data.get('photo_title')
    link = context.user_data.get('photo_link')
    
    add_photo_category(title, link, description)
    
    await update.message.reply_text("✅ Категория добавлена!", reply_markup=photos_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    from keyboards import photos_menu_keyboard
    if update.message:
        await update.message.reply_text("Операция отменена", reply_markup=photos_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.edit_message_text("Операция отменена", reply_markup=photos_menu_keyboard())
    return ConversationHandler.END

def get_photos_handlers():
    """Get all photo handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(photo_add_start, pattern="^photos:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, photo_add_title)],
            LINK: [MessageHandler(filters.TEXT, photo_add_link)],
            DESCRIPTION: [MessageHandler(filters.TEXT, photo_add_description)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^📸 Фотографии$"), photos_menu),
        CallbackQueryHandler(photo_category_detail, pattern="^photo_cat:\d+$"),
        CallbackQueryHandler(photos_menu, pattern="^photos:menu$"),
        add_handler,
    ]

