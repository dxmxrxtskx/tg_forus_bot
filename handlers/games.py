"""Game handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_games, get_game, add_game, update_game, mark_game_done, delete_game,
    get_random_game, get_game_top10
)
from keyboards import (
    games_menu_keyboard, games_done_menu_keyboard, games_top_menu_keyboard,
    game_detail_keyboard, list_keyboard, rating_keyboard, cancel_keyboard
)
from config import USER_DISPLAY_NAMES, USER_IDS

logger = logging.getLogger(__name__)

TITLE, NOTE, GENRE, EDIT_TITLE, EDIT_NOTE, EDIT_GENRE, RATING_USER1, RATING_USER2 = range(8)

async def games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show games menu."""
    if update.message:
        await update.message.reply_text(
            "🎮 Раздел компьютерных игр",
            reply_markup=games_menu_keyboard()
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "🎮 Раздел компьютерных игр",
            reply_markup=games_menu_keyboard()
        )

async def games_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending games."""
    query = update.callback_query
    await query.answer()
    
    games = get_games(status='pending')
    
    if not games:
        await query.edit_message_text("Список пуст", reply_markup=games_menu_keyboard())
        return
    
    items = [{'id': g['id'], 'title': g['title']} for g in games]
    await query.edit_message_text(
        "Выберите игру:",
        reply_markup=list_keyboard(items, "game", 0, 10)
    )

async def games_done_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show done games submenu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✅ Пройденные игры",
        reply_markup=games_done_menu_keyboard()
    )

async def games_done_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show done games list."""
    query = update.callback_query
    await query.answer()
    
    games = get_games(status='done')
    
    if not games:
        await query.edit_message_text("Список пуст", reply_markup=games_done_menu_keyboard())
        return
    
    items = [{'id': g['id'], 'title': g['title']} for g in games]
    await query.edit_message_text(
        "Выберите игру:",
        reply_markup=list_keyboard(items, "game", 0, 10)
    )

async def games_top_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top games submenu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏆 Топ-10 игр",
        reply_markup=games_top_menu_keyboard()
    )

async def games_top_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top games list."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data.split(":")
    top_type = callback_data[-1]
    
    user_num = None
    if top_type == "user1":
        user_num = 1
    elif top_type == "user2":
        user_num = 2
    
    games = get_game_top10(user_num)
    
    if not games:
        await query.edit_message_text("Список пуст", reply_markup=games_top_menu_keyboard())
        return
    
    text = "🏆 Топ-10:\n\n"
    for i, game in enumerate(games, 1):
        if user_num:
            rating = game[f'user{user_num}_rating']
            text += f"{i}. {game['title']} - {rating}/10\n"
        else:
            avg = (game.get('user1_rating', 0) or 0 + game.get('user2_rating', 0) or 0) / 2.0
            text += f"{i}. {game['title']} - {avg:.1f}/10\n"
    
    await query.edit_message_text(text, reply_markup=games_top_menu_keyboard())

async def games_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get random game."""
    query = update.callback_query
    await query.answer()
    
    game = get_random_game()
    
    if not game:
        await query.edit_message_text("Нет доступных игр")
        return
    
    text = f"🎲 Случайная игра:\n\n🎮 {game['title']}\n"
    if game['note']:
        text += f"📝 {game['note']}\n"
    if game['genre']:
        text += f"🏷️ {game['genre']}"
    
    await query.edit_message_text(text, reply_markup=game_detail_keyboard(game['id']))

async def game_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show game detail."""
    query = update.callback_query
    await query.answer()
    
    game_id = int(query.data.split(":")[1])
    game = get_game(game_id)
    
    if not game:
        await query.edit_message_text("Игра не найдена")
        return
    
    text = f"🎮 {game['title']}\n"
    if game['note']:
        text += f"📝 {game['note']}\n"
    if game['genre']:
        text += f"🏷️ {game['genre']}"
    
    await query.edit_message_text(text, reply_markup=game_detail_keyboard(game_id))

async def game_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding game."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название игры:",
        reply_markup=cancel_keyboard()
    )
    return TITLE

async def game_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get game title."""
    context.user_data['game_title'] = update.message.text
    await update.message.reply_text(
        "Добавить примечание? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return NOTE

async def game_add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get game note."""
    if update.message.text and update.message.text != "/skip":
        context.user_data['game_note'] = update.message.text
    else:
        context.user_data['game_note'] = None
    
    await update.message.reply_text(
        "Указать жанр? (или отправьте /skip чтобы пропустить)",
        reply_markup=cancel_keyboard()
    )
    return GENRE

async def game_add_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save game."""
    if update.message.text and update.message.text != "/skip":
        genre = update.message.text
    else:
        genre = None
    
    title = context.user_data.get('game_title')
    note = context.user_data.get('game_note')
    
    add_game(title, note, genre)
    
    await update.message.reply_text("✅ Игра добавлена!", reply_markup=games_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def game_done_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start rating process for done game."""
    query = update.callback_query
    await query.answer()
    
    game_id = int(query.data.split(":")[1])
    context.user_data['game_id'] = game_id
    
    user1_name = USER_DISPLAY_NAMES.get(USER_IDS[0], "Пользователь 1")
    await query.edit_message_text(
        f"Оценка от {user1_name} (1-10):",
        reply_markup=rating_keyboard(game_id, "game", 1)
    )
    return RATING_USER1

async def game_rating_user1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get rating from user 1."""
    query = update.callback_query
    await query.answer()
    
    rating = int(query.data.split(":")[-1])
    context.user_data['rating1'] = rating
    
    if len(USER_IDS) > 1:
        user2_name = USER_DISPLAY_NAMES.get(USER_IDS[1], "Пользователь 2")
        await query.edit_message_text(
            f"Оценка от {user2_name} (1-10):",
            reply_markup=rating_keyboard(context.user_data['game_id'], "game", 2)
        )
        return RATING_USER2
    else:
        game_id = context.user_data['game_id']
        mark_game_done(game_id, rating, None)
        await query.edit_message_text("✅ Игра отмечена как пройденная!", reply_markup=games_menu_keyboard())
        context.user_data.clear()
        return ConversationHandler.END

async def game_rating_user2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get rating from user 2."""
    query = update.callback_query
    await query.answer()
    
    rating = int(query.data.split(":")[-1])
    game_id = context.user_data['game_id']
    rating1 = context.user_data.get('rating1')
    
    mark_game_done(game_id, rating1, rating)
    await query.edit_message_text("✅ Игра отмечена как пройденная!", reply_markup=games_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def game_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing game."""
    query = update.callback_query
    await query.answer()
    
    game_id = int(query.data.split(":")[1])
    context.user_data['game_id'] = game_id
    
    await query.edit_message_text(
        "Введите новое название (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_TITLE

async def game_edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get edited title."""
    if update.message.text != "/skip":
        context.user_data['game_title'] = update.message.text
    else:
        context.user_data['game_title'] = None
    
    await update.message.reply_text(
        "Введите новое примечание (или /skip чтобы оставить текущее):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_NOTE

async def game_edit_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get edited note."""
    if update.message.text != "/skip":
        context.user_data['game_note'] = update.message.text
    else:
        context.user_data['game_note'] = None
    
    await update.message.reply_text(
        "Введите новый жанр (или /skip чтобы оставить текущий):",
        reply_markup=cancel_keyboard()
    )
    return EDIT_GENRE

async def game_edit_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save edited game."""
    if update.message.text != "/skip":
        context.user_data['game_genre'] = update.message.text
    else:
        context.user_data['game_genre'] = None
    
    game_id = context.user_data['game_id']
    update_game(
        game_id,
        context.user_data.get('game_title'),
        context.user_data.get('game_note'),
        context.user_data.get('game_genre')
    )
    
    await update.message.reply_text("✅ Игра обновлена!", reply_markup=games_menu_keyboard())
    
    context.user_data.clear()
    return ConversationHandler.END

async def game_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete game."""
    query = update.callback_query
    await query.answer()
    
    game_id = int(query.data.split(":")[1])
    delete_game(game_id)
    
    await query.edit_message_text("✅ Игра удалена!", reply_markup=games_menu_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("Операция отменена", reply_markup=games_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.edit_message_text("Операция отменена", reply_markup=games_menu_keyboard())
    return ConversationHandler.END

def get_games_handlers():
    """Get all game handlers."""
    add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(game_add_start, pattern="^games:add$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_add_title)],
            NOTE: [MessageHandler(filters.TEXT, game_add_note)],
            GENRE: [MessageHandler(filters.TEXT, game_add_genre)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    edit_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(game_edit_start, pattern="^game:\d+:edit$")],
        states={
            EDIT_TITLE: [MessageHandler(filters.TEXT, game_edit_title)],
            EDIT_NOTE: [MessageHandler(filters.TEXT, game_edit_note)],
            EDIT_GENRE: [MessageHandler(filters.TEXT, game_edit_genre)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    rating_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(game_done_start, pattern="^game:\d+:done$")],
        states={
            RATING_USER1: [CallbackQueryHandler(game_rating_user1, pattern="^game:\d+:rate:1:\d+$")],
            RATING_USER2: [CallbackQueryHandler(game_rating_user2, pattern="^game:\d+:rate:2:\d+$")],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
    )
    
    return [
        MessageHandler(filters.Regex("^🎮 Игры$"), games_menu),
        CallbackQueryHandler(games_menu, pattern="^games:menu$"),
        CallbackQueryHandler(games_pending, pattern="^games:pending$"),
        CallbackQueryHandler(games_done_menu, pattern="^games:done$"),
        CallbackQueryHandler(games_done_list, pattern="^games:done:all$"),
        CallbackQueryHandler(games_top_menu, pattern="^games:done:top$"),
        CallbackQueryHandler(games_top_list, pattern="^games:top:"),
        CallbackQueryHandler(games_random, pattern="^games:random$"),
        CallbackQueryHandler(game_detail, pattern="^game:\d+$"),
        CallbackQueryHandler(game_delete, pattern="^game:\d+:delete$"),
        add_handler,
        edit_handler,
        rating_handler,
    ]

