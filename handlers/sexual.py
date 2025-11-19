"""Sexual handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_sexual_all, add_sexual, get_sexual
)
from keyboards import (
    list_keyboard, cancel_keyboard
)

logger = logging.getLogger(__name__)

TITLE, LINK, DESCRIPTION = range(3)

async def sexual_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sexual menu - простой список без категорий."""
    if update.message:
        # Обработка сообщения (кнопка из главного меню)
        entries = get_sexual_all()
        
        if not entries:
            text = "🔞 Раздел Sexual\n\nСписок пуст"
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ])
        else:
            text = "🔞 Раздел Sexual\n\nВыберите запись:"
            items = [{'id': e['id'], 'title': e['title']} for e in entries]
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            base_keyboard = list_keyboard(items, "sexual", 0, 10)
            new_keyboard = list(base_keyboard.inline_keyboard)
            new_keyboard.append([InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")])
            new_keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
            keyboard = InlineKeyboardMarkup(new_keyboard)
        
        await update.message.reply_text(text, reply_markup=keyboard)
    elif update.callback_query:
        # Обработка callback_query (кнопка "Назад")
        query = update.callback_query
        await query.answer()
        
        entries = get_sexual_all()
        
        if not entries:
            text = "🔞 Раздел Sexual\n\nСписок пуст"
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ])
        else:
            text = "🔞 Раздел Sexual\n\nВыберите запись:"
            items = [{'id': e['id'], 'title': e['title']} for e in entries]
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            base_keyboard = list_keyboard(items, "sexual", 0, 10)
            new_keyboard = list(base_keyboard.inline_keyboard)
            new_keyboard.append([InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")])
            new_keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
            keyboard = InlineKeyboardMarkup(new_keyboard)
        
        await query.edit_message_text(text, reply_markup=keyboard)

async def sexual_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sexual entry detail."""
    query = update.callback_query
    await query.answer()
    
    entry_id = int(query.data.split(":")[1])
    entry = get_sexual(entry_id)
    
    if not entry:
        await query.edit_message_text("Запись не найдена")
        return
    
    text = f"🔞 {entry['title']}\n"
    if entry['link']:
        text += f"🔗 {entry['link']}\n"
    if entry['description']:
        text += f"📝 {entry['description']}"
    
    # Создать клавиатуру с кнопкой "Назад" к списку
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="sexual:menu")]
    ])
    
    await query.edit_message_text(text, reply_markup=keyboard)

async def sexual_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding sexual entry."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название:",
        reply_markup=cancel_keyboard()
    )
    return TITLE

async def sexual_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get entry title."""
    context.user_data['sexual_title'] = update.message.text
    await update.message.reply_text(
        "Добавить ссылку? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return LINK

async def sexual_add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get entry link."""
    if update.message.text and update.message.text != "/skip":
        context.user_data['sexual_link'] = update.message.text
    else:
        context.user_data['sexual_link'] = None
    
    await update.message.reply_text(
        "Добавить описание? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return DESCRIPTION

async def sexual_add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save sexual entry."""
    if update.message.text and update.message.text != "/skip":
        description = update.message.text
    else:
        description = None
    
    title = context.user_data.get('sexual_title')
    link = context.user_data.get('sexual_link')
    
    add_sexual(title, link, description)
    
    # Вернуться к списку
    entries = get_sexual_all()
    if not entries:
        await update.message.reply_text("✅ Запись добавлена!", reply_markup=cancel_keyboard())
    else:
        text = "✅ Запись добавлена!\n\n🔞 Раздел Sexual\n\nВыберите запись:"
        items = [{'id': e['id'], 'title': e['title']} for e in entries]
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        base_keyboard = list_keyboard(items, "sexual", 0, 10)
        new_keyboard = list(base_keyboard.inline_keyboard)
        new_keyboard.append([InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")])
        new_keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        keyboard = InlineKeyboardMarkup(new_keyboard)
        await update.message.reply_text(text, reply_markup=keyboard)
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    
    # Вернуться к списку
    entries = get_sexual_all()
    if not entries:
        text = "Операция отменена\n\n🔞 Раздел Sexual\n\nСписок пуст"
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ])
    else:
        text = "Операция отменена\n\n🔞 Раздел Sexual\n\nВыберите запись:"
        items = [{'id': e['id'], 'title': e['title']} for e in entries]
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        base_keyboard = list_keyboard(items, "sexual", 0, 10)
        new_keyboard = list(base_keyboard.inline_keyboard)
        new_keyboard.append([InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")])
        new_keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        keyboard = InlineKeyboardMarkup(new_keyboard)
    
    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=keyboard)
    return ConversationHandler.END

def get_sexual_handlers():
    """Get all sexual handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(sexual_add_start, pattern="^sexual:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sexual_add_title)],
            LINK: [MessageHandler(filters.TEXT, sexual_add_link)],
            DESCRIPTION: [MessageHandler(filters.TEXT, sexual_add_description)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^🔞 Sexual$"), sexual_menu),
        CallbackQueryHandler(sexual_menu, pattern="^sexual:menu$"),
        CallbackQueryHandler(sexual_detail, pattern="^sexual:\d+$"),
        add_handler,
    ]
