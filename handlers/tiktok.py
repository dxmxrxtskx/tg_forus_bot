"""TikTok trends handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_tiktok_trends, get_tiktok_trend, add_tiktok_trend,
    mark_tiktok_trend_done, delete_tiktok_trend
)
from keyboards import (
    tiktok_menu_keyboard, tiktok_trend_detail_keyboard, list_keyboard, cancel_keyboard
)

logger = logging.getLogger(__name__)

TITLE, VIDEO = range(2)

async def tiktok_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show TikTok menu."""
    await update.message.reply_text(
        "📱 Раздел трендов TikTok",
        reply_markup=tiktok_menu_keyboard()
    )

async def tiktok_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show todo trends."""
    query = update.callback_query
    await query.answer()
    
    trends = get_tiktok_trends(status='todo')
    
    if not trends:
        await query.edit_message_text("Список пуст", reply_markup=tiktok_menu_keyboard())
        return
    
    items = [{'id': t['id'], 'title': t['title']} for t in trends]
    await query.edit_message_text(
        "Выберите тренд:",
        reply_markup=list_keyboard(items, "tiktok", 0, 10)
    )

async def tiktok_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show done trends."""
    query = update.callback_query
    await query.answer()
    
    trends = get_tiktok_trends(status='done')
    
    if not trends:
        await query.edit_message_text("Список пуст", reply_markup=tiktok_menu_keyboard())
        return
    
    items = [{'id': t['id'], 'title': t['title']} for t in trends]
    await query.edit_message_text(
        "Выберите тренд:",
        reply_markup=list_keyboard(items, "tiktok", 0, 10)
    )

async def tiktok_trend_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trend detail with video."""
    query = update.callback_query
    await query.answer()
    
    trend_id = int(query.data.split(":")[1])
    trend = get_tiktok_trend(trend_id)
    
    if not trend:
        await query.edit_message_text("Тренд не найден")
        return
    
    text = f"📱 {trend['title']}"
    
    if trend['video_file_id']:
        try:
            await query.message.reply_video(
                video=trend['video_file_id'],
                caption=text,
                reply_markup=tiktok_trend_detail_keyboard(trend_id)
            )
            await query.delete_message()
        except Exception as e:
            logger.error(f"Error sending video: {e}")
            await query.edit_message_text(
                f"{text}\n\n⚠️ Видео недоступно",
                reply_markup=tiktok_trend_detail_keyboard(trend_id)
            )
    else:
        await query.edit_message_text(text, reply_markup=tiktok_trend_detail_keyboard(trend_id))

async def tiktok_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding trend."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название тренда:",
        reply_markup=cancel_keyboard()
    )
    return TITLE

async def tiktok_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get trend title."""
    context.user_data['tiktok_title'] = update.message.text
    await update.message.reply_text(
        "Приложите видео:",
        reply_markup=cancel_keyboard()
    )
    return VIDEO

async def tiktok_add_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save trend with video."""
    video_file_id = None
    if update.message.video:
        video_file_id = update.message.video.file_id
    elif update.message.document:
        video_file_id = update.message.document.file_id
    
    title = context.user_data.get('tiktok_title')
    add_tiktok_trend(title, video_file_id)
    
    await update.message.reply_text("✅ Тренд добавлен!", reply_markup=tiktok_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def tiktok_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark trend as done."""
    query = update.callback_query
    await query.answer()
    
    trend_id = int(query.data.split(":")[1])
    mark_tiktok_trend_done(trend_id)
    
    await query.edit_message_text("✅ Тренд отмечен как выполненный!", reply_markup=tiktok_menu_keyboard())

async def tiktok_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete trend."""
    query = update.callback_query
    await query.answer()
    
    trend_id = int(query.data.split(":")[1])
    delete_tiktok_trend(trend_id)
    
    await query.edit_message_text("✅ Тренд удален!", reply_markup=tiktok_menu_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("Операция отменена", reply_markup=tiktok_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.edit_message_text("Операция отменена", reply_markup=tiktok_menu_keyboard())
    return ConversationHandler.END

def get_tiktok_handlers():
    """Get all TikTok handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(tiktok_add_start, pattern="^tiktok:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, tiktok_add_title)],
            VIDEO: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, tiktok_add_video)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^📱 Тренды TikTok$"), tiktok_menu),
        CallbackQueryHandler(tiktok_todo, pattern="^tiktok:todo$"),
        CallbackQueryHandler(tiktok_done, pattern="^tiktok:done$"),
        CallbackQueryHandler(tiktok_trend_detail, pattern="^tiktok:\d+$"),
        CallbackQueryHandler(tiktok_done, pattern="^tiktok:\d+:done$"),
        CallbackQueryHandler(tiktok_delete, pattern="^tiktok:\d+:delete$"),
        add_handler,
    ]

