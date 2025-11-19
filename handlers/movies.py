"""Movie handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_movies, get_movie, add_movie, update_movie, delete_movie, mark_movie_watched,
    get_random_movie, get_movie_top10, get_movie_categories, add_movie_category
)
from keyboards import (
    movies_menu_keyboard, movies_pending_menu_keyboard, movies_watched_menu_keyboard,
    movies_top_menu_keyboard, movie_detail_keyboard, list_keyboard, category_selection_keyboard,
    rating_keyboard, cancel_keyboard
)
from config import USER_DISPLAY_NAMES, USER_IDS

logger = logging.getLogger(__name__)

# Conversation states
TITLE, NOTE, CATEGORY, NEW_CATEGORY, EDIT_TITLE, EDIT_NOTE, RATING_USER1, RATING_USER2 = range(8)

async def movies_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show movies menu."""
    if update.message:
        await update.message.reply_text(
            "🎬 Раздел фильмов",
            reply_markup=movies_menu_keyboard()
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "🎬 Раздел фильмов",
            reply_markup=movies_menu_keyboard()
        )

async def movies_pending_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending movies submenu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📺 Фильмы ожидающие просмотра",
        reply_markup=movies_pending_menu_keyboard()
    )

async def movies_pending_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending movies list."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data.split(":")
    category_name = callback_data[-1] if len(callback_data) > 2 else "all"
    
    category_id = None
    if category_name != "all":
        categories = get_movie_categories()
        category_map = {"films": "Фильм", "series": "Сериал", "cartoons": "Мультик"}
        if category_name in category_map:
            for cat in categories:
                if cat['name'] == category_map[category_name]:
                    category_id = cat['id']
                    break
    
    movies = get_movies(watched=False, category_id=category_id)
    
    if not movies:
        await query.edit_message_text("Список пуст", reply_markup=movies_pending_menu_keyboard())
        return
    
    items = [{'id': m['id'], 'title': m['title']} for m in movies]
    await query.edit_message_text(
        "Выберите фильм:",
        reply_markup=list_keyboard(items, "movie", 0, 10)
    )

async def movie_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show movie detail."""
    query = update.callback_query
    await query.answer()
    
    movie_id = int(query.data.split(":")[1])
    movie = get_movie(movie_id)
    
    if not movie:
        await query.edit_message_text("Фильм не найден")
        return
    
    category = next((c for c in get_movie_categories() if c['id'] == movie['category_id']), None)
    text = f"🎬 {movie['title']}\n"
    if movie['note']:
        text += f"📝 {movie['note']}\n"
    if category:
        text += f"🏷️ {category['name']}"
    
    await query.edit_message_text(text, reply_markup=movie_detail_keyboard(movie_id))

async def movies_watched_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show watched movies submenu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✅ Просмотренные фильмы",
        reply_markup=movies_watched_menu_keyboard()
    )

async def movies_watched_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show watched movies list."""
    query = update.callback_query
    await query.answer()
    
    movies = get_movies(watched=True)
    
    if not movies:
        await query.edit_message_text("Список пуст", reply_markup=movies_watched_menu_keyboard())
        return
    
    items = [{'id': m['id'], 'title': m['title']} for m in movies]
    await query.edit_message_text(
        "Выберите фильм:",
        reply_markup=list_keyboard(items, "movie", 0, 10)
    )

async def movies_top_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top movies submenu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏆 Топ-10 фильмов",
        reply_markup=movies_top_menu_keyboard()
    )

async def movies_top_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top movies list."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data.split(":")
    top_type = callback_data[-1]
    
    user_num = None
    if top_type == "user1":
        user_num = 1
    elif top_type == "user2":
        user_num = 2
    
    movies = get_movie_top10(user_num)
    
    if not movies:
        await query.edit_message_text("Список пуст", reply_markup=movies_top_menu_keyboard())
        return
    
    text = "🏆 Топ-10:\n\n"
    for i, movie in enumerate(movies, 1):
        if user_num:
            rating = movie[f'user{user_num}_rating']
            text += f"{i}. {movie['title']} - {rating}/10\n"
        else:
            avg = (movie.get('user1_rating', 0) or 0 + movie.get('user2_rating', 0) or 0) / 2.0
            text += f"{i}. {movie['title']} - {avg:.1f}/10\n"
    
    await query.edit_message_text(text, reply_markup=movies_top_menu_keyboard())

async def movies_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get random movie."""
    query = update.callback_query
    await query.answer()
    
    movie = get_random_movie(exclude_series=True)
    
    if not movie:
        await query.edit_message_text("Нет доступных фильмов")
        return
    
    category = next((c for c in get_movie_categories() if c['id'] == movie['category_id']), None)
    text = f"🎲 Случайный фильм:\n\n🎬 {movie['title']}\n"
    if movie['note']:
        text += f"📝 {movie['note']}\n"
    if category:
        text += f"🏷️ {category['name']}"
    
    await query.edit_message_text(text, reply_markup=movie_detail_keyboard(movie['id']))

async def movie_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding movie."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название фильма:",
        reply_markup=cancel_keyboard()
    )
    return TITLE

async def movie_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get movie title."""
    context.user_data['movie_title'] = update.message.text
    await update.message.reply_text(
        "Добавить примечание? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return NOTE

async def movie_add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get movie note."""
    if update.message.text and update.message.text != "/skip":
        context.user_data['movie_note'] = update.message.text
    else:
        context.user_data['movie_note'] = None
    
    categories = get_movie_categories()
    cat_list = [{'id': c['id'], 'name': c['name']} for c in categories]
    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=category_selection_keyboard(cat_list, "movie_add", add_new=True)
    )
    return CATEGORY

async def movie_add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get movie category."""
    query = update.callback_query
    await query.answer()
    
    if query.data.endswith(":new_cat"):
        await query.edit_message_text(
            "Введите название новой категории:",
            reply_markup=cancel_keyboard()
        )
        return NEW_CATEGORY
    
    category_id = int(query.data.split(":")[-1])
    title = context.user_data.get('movie_title')
    note = context.user_data.get('movie_note')
    
    add_movie(title, note, category_id)
    await query.edit_message_text("✅ Фильм добавлен!", reply_markup=movies_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def movie_add_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new movie category."""
    cat_name = update.message.text
    cat_id = add_movie_category(cat_name)
    
    title = context.user_data.get('movie_title')
    note = context.user_data.get('movie_note')
    
    add_movie(title, note, cat_id)
    await update.message.reply_text("✅ Фильм добавлен!", reply_markup=movies_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def movie_watched(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start rating process for watched movie."""
    query = update.callback_query
    await query.answer()
    
    movie_id = int(query.data.split(":")[1])
    context.user_data['movie_id'] = movie_id
    context.user_data['rating_user'] = 1
    
    user1_name = USER_DISPLAY_NAMES.get(USER_IDS[0], "Пользователь 1")
    await query.edit_message_text(
        f"Оценка от {user1_name} (1-10):",
        reply_markup=rating_keyboard(movie_id, "movie", 1)
    )
    return RATING_USER1

async def movie_rating_user1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get rating from user 1."""
    query = update.callback_query
    await query.answer()
    
    rating = int(query.data.split(":")[-1])
    context.user_data['rating1'] = rating
    
    if len(USER_IDS) > 1:
        user2_name = USER_DISPLAY_NAMES.get(USER_IDS[1], "Пользователь 2")
        await query.edit_message_text(
            f"Оценка от {user2_name} (1-10):",
            reply_markup=rating_keyboard(context.user_data['movie_id'], "movie", 2)
        )
        return RATING_USER2
    else:
        movie_id = context.user_data['movie_id']
        mark_movie_watched(movie_id, rating, None)
        await query.edit_message_text("✅ Фильм отмечен как просмотренный!", reply_markup=movies_menu_keyboard())
        context.user_data.clear()
        return ConversationHandler.END

async def movie_rating_user2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get rating from user 2."""
    query = update.callback_query
    await query.answer()
    
    rating = int(query.data.split(":")[-1])
    movie_id = context.user_data['movie_id']
    rating1 = context.user_data.get('rating1')
    
    mark_movie_watched(movie_id, rating1, rating)
    await query.edit_message_text("✅ Фильм отмечен как просмотренный!", reply_markup=movies_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def movie_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing movie."""
    query = update.callback_query
    await query.answer()
    
    movie_id = int(query.data.split(":")[1])
    context.user_data['movie_id'] = movie_id
    
    await query.edit_message_text(
        "Введите новое название (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_TITLE

async def movie_edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get edited title."""
    if update.message.text != "/skip":
        context.user_data['movie_title'] = update.message.text
    else:
        context.user_data['movie_title'] = None
    
    await update.message.reply_text(
        "Введите новое примечание (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_NOTE

async def movie_edit_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save edited movie."""
    if update.message.text != "/skip":
        context.user_data['movie_note'] = update.message.text
    else:
        context.user_data['movie_note'] = None
    
    movie_id = context.user_data['movie_id']
    update_movie(movie_id, context.user_data.get('movie_title'), context.user_data.get('movie_note'))
    
    await update.message.reply_text("✅ Фильм обновлен!", reply_markup=movies_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def movie_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete movie."""
    query = update.callback_query
    await query.answer()
    
    movie_id = int(query.data.split(":")[1])
    delete_movie(movie_id)
    
    await query.edit_message_text("✅ Фильм удален!", reply_markup=movies_menu_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("Операция отменена", reply_markup=movies_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.edit_message_text("Операция отменена", reply_markup=movies_menu_keyboard())
    return ConversationHandler.END

def get_movies_handlers():
    """Get all movie handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(movie_add_start, pattern="^movies:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, movie_add_title)],
            NOTE: [MessageHandler(filters.TEXT, movie_add_note)],
            CATEGORY: [CallbackQueryHandler(movie_add_category, pattern="^movie_add:")],
            NEW_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, movie_add_new_category)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    edit_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(movie_edit_start, pattern="^movie:\d+:edit$")],
        states={
            EDIT_TITLE: [MessageHandler(filters.TEXT, movie_edit_title)],
            EDIT_NOTE: [MessageHandler(filters.TEXT, movie_edit_note)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    rating_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(movie_watched, pattern="^movie:\d+:watched$")],
        states={
            RATING_USER1: [CallbackQueryHandler(movie_rating_user1, pattern="^movie:\d+:rate:1:\d+$")],
            RATING_USER2: [CallbackQueryHandler(movie_rating_user2, pattern="^movie:\d+:rate:2:\d+$")],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^🎬 Фильмы$"), movies_menu),
        CallbackQueryHandler(movies_menu, pattern="^movies:menu$"),
        CallbackQueryHandler(movies_pending_menu, pattern="^movies:pending$"),
        CallbackQueryHandler(movies_pending_list, pattern="^movies:pending:"),
        CallbackQueryHandler(movies_watched_menu, pattern="^movies:watched$"),
        CallbackQueryHandler(movies_watched_list, pattern="^movies:watched:all$"),
        CallbackQueryHandler(movies_top_menu, pattern="^movies:watched:top$"),
        CallbackQueryHandler(movies_top_list, pattern="^movies:top:"),
        CallbackQueryHandler(movies_random, pattern="^movies:random$"),
        CallbackQueryHandler(movie_detail, pattern="^movie:\d+$"),
        CallbackQueryHandler(movie_delete, pattern="^movie:\d+:delete$"),
        add_handler,
        edit_handler,
        rating_handler,
    ]

