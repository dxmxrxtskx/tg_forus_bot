"""Trip handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_trips, get_trip, add_trip, update_trip, delete_trip,
    get_trip_categories, add_trip_category
)
from keyboards import (
    trips_menu_keyboard, trip_detail_keyboard, list_keyboard,
    category_selection_keyboard, cancel_keyboard
)

logger = logging.getLogger(__name__)

TITLE, NOTE, CATEGORY, NEW_CATEGORY, EDIT_TITLE, EDIT_NOTE = range(6)

async def trips_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trips menu."""
    if update.message:
        await update.message.reply_text(
            "✈️ Раздел поездок",
            reply_markup=trips_menu_keyboard()
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "✈️ Раздел поездок",
            reply_markup=trips_menu_keyboard()
        )

async def trips_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trips by category."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data.split(":")
    category_type = callback_data[-1]
    
    category_id = None
    if category_type != "add":
        categories = get_trip_categories()
        category_map = {"walk": "Пешком", "trips": "Поездки", "places": "Места в Херцег-Нови"}
        if category_type in category_map:
            for cat in categories:
                if cat['name'] == category_map[category_type]:
                    category_id = cat['id']
                    break
    
    trips = get_trips(category_id=category_id)
    
    if not trips:
        await query.edit_message_text("Список пуст", reply_markup=trips_menu_keyboard())
        return
    
    items = [{'id': t['id'], 'title': t['title']} for t in trips]
    await query.edit_message_text(
        "Выберите поездку:",
        reply_markup=list_keyboard(items, "trip", 0, 10, 
                                   back_button="🔙 Главное меню", 
                                   back_callback="main_menu")
    )

async def trip_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trip detail."""
    query = update.callback_query
    await query.answer()
    
    trip_id = int(query.data.split(":")[1])
    trip = get_trip(trip_id)
    
    if not trip:
        await query.edit_message_text("Поездка не найдена")
        return
    
    category = next((c for c in get_trip_categories() if c['id'] == trip['category_id']), None)
    text = f"✈️ {trip['title']}\n"
    if trip['note']:
        text += f"📝 {trip['note']}\n"
    if category:
        text += f"🏷️ {category['name']}"
    
    await query.edit_message_text(text, reply_markup=trip_detail_keyboard(trip_id))

async def trip_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding trip."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название поездки:",
        reply_markup=cancel_keyboard()
    )
    return TITLE

async def trip_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get trip title."""
    context.user_data['trip_title'] = update.message.text
    await update.message.reply_text(
        "Добавить примечание? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return NOTE

async def trip_add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get trip note."""
    if update.message.text and update.message.text != "/skip":
        context.user_data['trip_note'] = update.message.text
    else:
        context.user_data['trip_note'] = None
    
    categories = get_trip_categories()
    cat_list = [{'id': c['id'], 'name': c['name']} for c in categories]
    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=category_selection_keyboard(cat_list, "trip_add", add_new=True)
    )
    return CATEGORY

async def trip_add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get trip category."""
    query = update.callback_query
    await query.answer()
    
    if query.data.endswith(":new_cat"):
        await query.edit_message_text(
            "Введите название новой категории:",
            reply_markup=cancel_keyboard()
        )
        return NEW_CATEGORY
    
    category_id = int(query.data.split(":")[-1])
    title = context.user_data.get('trip_title')
    note = context.user_data.get('trip_note')
    
    add_trip(title, note, category_id)
    await query.edit_message_text("✅ Поездка добавлена!", reply_markup=trips_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def trip_add_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new trip category."""
    cat_name = update.message.text
    cat_id = add_trip_category(cat_name)
    
    title = context.user_data.get('trip_title')
    note = context.user_data.get('trip_note')
    
    add_trip(title, note, cat_id)
    await update.message.reply_text("✅ Поездка добавлена!", reply_markup=trips_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def trip_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing trip."""
    query = update.callback_query
    await query.answer()
    
    trip_id = int(query.data.split(":")[1])
    context.user_data['trip_id'] = trip_id
    
    await query.edit_message_text(
        "Введите новое название (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_TITLE

async def trip_edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get edited title."""
    if update.message.text != "/skip":
        context.user_data['trip_title'] = update.message.text
    else:
        context.user_data['trip_title'] = None
    
    await update.message.reply_text(
        "Введите новое примечание (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_NOTE

async def trip_edit_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save edited trip."""
    if update.message.text != "/skip":
        context.user_data['trip_note'] = update.message.text
    else:
        context.user_data['trip_note'] = None
    
    trip_id = context.user_data['trip_id']
    update_trip(trip_id, context.user_data.get('trip_title'), context.user_data.get('trip_note'))
    
    await update.message.reply_text("✅ Поездка обновлена!", reply_markup=trips_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def trip_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete trip."""
    query = update.callback_query
    await query.answer()
    
    trip_id = int(query.data.split(":")[1])
    delete_trip(trip_id)
    
    await query.edit_message_text("✅ Поездка удалена!", reply_markup=trips_menu_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("Операция отменена", reply_markup=trips_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.edit_message_text("Операция отменена", reply_markup=trips_menu_keyboard())
    return ConversationHandler.END

def get_trips_handlers():
    """Get all trip handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(trip_add_start, pattern="^trips:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, trip_add_title)],
            NOTE: [MessageHandler(filters.TEXT, trip_add_note)],
            CATEGORY: [CallbackQueryHandler(trip_add_category, pattern="^trip_add:")],
            NEW_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, trip_add_new_category)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    edit_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(trip_edit_start, pattern="^trip:\d+:edit$")],
        states={
            EDIT_TITLE: [MessageHandler(filters.TEXT, trip_edit_title)],
            EDIT_NOTE: [MessageHandler(filters.TEXT, trip_edit_note)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^✈️ Поездки$"), trips_menu),
        CallbackQueryHandler(trips_menu, pattern="^trips:menu$"),
        CallbackQueryHandler(trips_list, pattern="^trips:(walk|trips|places)$"),
        CallbackQueryHandler(trip_detail, pattern="^trip:\d+$"),
        CallbackQueryHandler(trip_delete, pattern="^trip:\d+:delete$"),
        add_handler,
        edit_handler,
    ]

