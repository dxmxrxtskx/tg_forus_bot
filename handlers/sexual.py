"""Sexual handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_sexual_by_category, get_sexual_categories, add_sexual, add_sexual_category
)
from keyboards import (
    sexual_menu_keyboard, list_keyboard, category_selection_keyboard, cancel_keyboard
)

logger = logging.getLogger(__name__)

TITLE, LINK, DESCRIPTION, CATEGORY, NEW_CATEGORY = range(5)

async def sexual_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sexual menu."""
    if update.message:
        await update.message.reply_text(
            "🔞 Раздел Sexual",
            reply_markup=sexual_menu_keyboard()
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "🔞 Раздел Sexual",
            reply_markup=sexual_menu_keyboard()
        )

async def sexual_shops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show shops by category."""
    query = update.callback_query
    await query.answer()
    
    categories = get_sexual_categories()
    
    if not categories:
        await query.edit_message_text("Список категорий пуст", reply_markup=sexual_menu_keyboard())
        return
    
    items = [{'id': c['id'], 'title': c['name']} for c in categories]
    await query.edit_message_text(
        "Выберите категорию:",
        reply_markup=list_keyboard(items, "sexual_cat", 0, 10)
    )

async def sexual_category_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show entries in category."""
    query = update.callback_query
    await query.answer()
    
    category_id = int(query.data.split(":")[-1])
    entries = get_sexual_by_category(category_id)
    
    if not entries:
        await query.edit_message_text("Список пуст", reply_markup=sexual_menu_keyboard())
        return
    
    items = [{'id': e['id'], 'title': e['title']} for e in entries]
    await query.edit_message_text(
        "Выберите магазин:",
        reply_markup=list_keyboard(items, "sexual", 0, 10)
    )

async def sexual_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sexual entry detail."""
    query = update.callback_query
    await query.answer()
    
    entry_id = int(query.data.split(":")[1])
    from database import get_sexual
    entry = get_sexual(entry_id)
    
    if not entry:
        await query.edit_message_text("Запись не найдена")
        return
    
    category = next((c for c in get_sexual_categories() if c['id'] == entry['category_id']), None)
    text = f"🏪 {entry['title']}\n"
    if entry['link']:
        text += f"🔗 {entry['link']}\n"
    if entry['description']:
        text += f"📝 {entry['description']}\n"
    if category:
        text += f"🏷️ {category['name']}"
    
    await query.edit_message_text(text, reply_markup=sexual_menu_keyboard())

async def sexual_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding sexual entry."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название магазина:",
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
    """Get entry description."""
    if update.message.text and update.message.text != "/skip":
        context.user_data['sexual_description'] = update.message.text
    else:
        context.user_data['sexual_description'] = None
    
    categories = get_sexual_categories()
    cat_list = [{'id': c['id'], 'name': c['name']} for c in categories]
    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=category_selection_keyboard(cat_list, "sexual_add", add_new=True)
    )
    return CATEGORY

async def sexual_add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get entry category."""
    query = update.callback_query
    await query.answer()
    
    if query.data.endswith(":new_cat"):
        await query.edit_message_text(
            "Введите название новой категории:",
            reply_markup=cancel_keyboard()
        )
        return NEW_CATEGORY
    
    category_id = int(query.data.split(":")[-1])
    title = context.user_data.get('sexual_title')
    link = context.user_data.get('sexual_link')
    description = context.user_data.get('sexual_description')
    
    add_sexual(title, link, description, category_id)
    await query.edit_message_text("✅ Магазин добавлен!", reply_markup=sexual_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def sexual_add_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new sexual category."""
    cat_name = update.message.text
    cat_id = add_sexual_category(cat_name)
    
    title = context.user_data.get('sexual_title')
    link = context.user_data.get('sexual_link')
    description = context.user_data.get('sexual_description')
    
    add_sexual(title, link, description, cat_id)
    await update.message.reply_text("✅ Магазин добавлен!", reply_markup=sexual_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("Операция отменена", reply_markup=sexual_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.edit_message_text("Операция отменена", reply_markup=sexual_menu_keyboard())
    return ConversationHandler.END

def get_sexual_handlers():
    """Get all sexual handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(sexual_add_start, pattern="^sexual:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sexual_add_title)],
            LINK: [MessageHandler(filters.TEXT, sexual_add_link)],
            DESCRIPTION: [MessageHandler(filters.TEXT, sexual_add_description)],
            CATEGORY: [CallbackQueryHandler(sexual_add_category, pattern="^sexual_add:")],
            NEW_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, sexual_add_new_category)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^🔞 Sexual$"), sexual_menu),
        CallbackQueryHandler(sexual_menu, pattern="^sexual:menu$"),
        CallbackQueryHandler(sexual_shops, pattern="^sexual:shops$"),
        CallbackQueryHandler(sexual_category_list, pattern="^sexual_cat:\d+$"),
        CallbackQueryHandler(sexual_detail, pattern="^sexual:\d+$"),
        add_handler,
    ]

