"""Activity handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_activities, get_activity, add_activity, update_activity,
    mark_activity_done, delete_activity
)
from keyboards import (
    activities_menu_keyboard, activity_detail_keyboard, list_keyboard, cancel_keyboard
)

logger = logging.getLogger(__name__)

TITLE, NOTE, EDIT_TITLE, EDIT_NOTE = range(4)

async def activities_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show activities menu."""
    if update.message:
        await update.message.reply_text(
            "📋 Раздел активностей",
            reply_markup=activities_menu_keyboard()
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "📋 Раздел активностей",
            reply_markup=activities_menu_keyboard()
        )

async def activities_planned(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show planned activities."""
    query = update.callback_query
    await query.answer()
    
    activities = get_activities(status='planned')
    
    if not activities:
        await query.edit_message_text("Список пуст", reply_markup=activities_menu_keyboard())
        return
    
    items = [{'id': a['id'], 'title': a['title']} for a in activities]
    await query.edit_message_text(
        "Выберите активность:",
        reply_markup=list_keyboard(items, "activity", 0, 10,
                                   back_button="🔙 Назад",
                                   back_callback="activities:menu")
    )

async def activities_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show done activities."""
    query = update.callback_query
    await query.answer()
    
    activities = get_activities(status='done')
    
    if not activities:
        await query.edit_message_text("Список пуст", reply_markup=activities_menu_keyboard())
        return
    
    items = [{'id': a['id'], 'title': a['title']} for a in activities]
    await query.edit_message_text(
        "Выберите активность:",
        reply_markup=list_keyboard(items, "activity", 0, 10,
                                   back_button="🔙 Назад",
                                   back_callback="activities:menu")
    )

async def activity_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show activity detail."""
    query = update.callback_query
    await query.answer()
    
    activity_id = int(query.data.split(":")[1])
    activity = get_activity(activity_id)
    
    if not activity:
        await query.edit_message_text("Активность не найдена")
        return
    
    text = f"📋 {activity['title']}\n"
    if activity['note']:
        text += f"📝 {activity['note']}"
    
    # Определить статус активности для кнопки "Назад"
    status = activity['status'] if 'status' in activity.keys() else 'planned'
    await query.edit_message_text(text, reply_markup=activity_detail_keyboard(activity_id, status=status))

async def activity_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding activity."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название активности:",
        reply_markup=cancel_keyboard()
    )
    return TITLE

async def activity_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get activity title."""
    context.user_data['activity_title'] = update.message.text
    await update.message.reply_text(
        "Добавить примечание? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return NOTE

async def activity_add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save activity."""
    if update.message.text and update.message.text != "/skip":
        note = update.message.text
    else:
        note = None
    
    title = context.user_data.get('activity_title')
    add_activity(title, note)
    
    await update.message.reply_text("✅ Активность добавлена!", reply_markup=activities_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def activity_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark activity as done."""
    query = update.callback_query
    await query.answer()
    
    activity_id = int(query.data.split(":")[1])
    mark_activity_done(activity_id)
    
    # Получить обновленную информацию об активности
    activity = get_activity(activity_id)
    if activity:
        text = f"✅ Активность выполнена!\n\n📋 {activity['title']}"
        if activity['note']:
            text += f"\n📝 {activity['note']}"
        await query.edit_message_text(text, reply_markup=activity_detail_keyboard(activity_id, status='done'))
    else:
        await query.edit_message_text("✅ Активность выполнена!", reply_markup=activities_menu_keyboard())

async def activity_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing activity."""
    query = update.callback_query
    await query.answer()
    
    activity_id = int(query.data.split(":")[1])
    context.user_data['activity_id'] = activity_id
    
    await query.edit_message_text(
        "Введите новое название (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_TITLE

async def activity_edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get edited title."""
    if update.message.text != "/skip":
        context.user_data['activity_title'] = update.message.text
    else:
        context.user_data['activity_title'] = None
    
    await update.message.reply_text(
        "Введите новое примечание (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_NOTE

async def activity_edit_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save edited activity."""
    if update.message.text != "/skip":
        context.user_data['activity_note'] = update.message.text
    else:
        context.user_data['activity_note'] = None
    
    activity_id = context.user_data['activity_id']
    update_activity(activity_id, context.user_data.get('activity_title'), context.user_data.get('activity_note'))
    
    await update.message.reply_text("✅ Активность обновлена!", reply_markup=activities_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def activity_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete activity."""
    query = update.callback_query
    await query.answer()
    
    activity_id = int(query.data.split(":")[1])
    delete_activity(activity_id)
    
    await query.edit_message_text("✅ Активность удалена!", reply_markup=activities_menu_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("Операция отменена", reply_markup=activities_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.edit_message_text("Операция отменена", reply_markup=activities_menu_keyboard())
    return ConversationHandler.END

def get_activities_handlers():
    """Get all activity handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(activity_add_start, pattern="^activities:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, activity_add_title)],
            NOTE: [MessageHandler(filters.TEXT, activity_add_note)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    edit_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(activity_edit_start, pattern="^activity:\d+:edit$")],
        states={
            EDIT_TITLE: [MessageHandler(filters.TEXT, activity_edit_title)],
            EDIT_NOTE: [MessageHandler(filters.TEXT, activity_edit_note)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^📋 Активности$"), activities_menu),
        CallbackQueryHandler(activities_menu, pattern="^activities:menu$"),
        CallbackQueryHandler(activities_planned, pattern="^activities:planned$"),
        CallbackQueryHandler(activities_done, pattern="^activities:done$"),
        CallbackQueryHandler(activity_detail, pattern="^activity:\d+$"),
        CallbackQueryHandler(activity_done, pattern="^activity:\d+:done$"),
        CallbackQueryHandler(activity_delete, pattern="^activity:\d+:delete$"),
        add_handler,
        edit_handler,
    ]

