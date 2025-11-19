"""Keyboard builders for inline and reply keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard (reply keyboard for messages)."""
    keyboard = [
        [KeyboardButton("🎬 Фильмы")],
        [KeyboardButton("📋 Активности")],
        [KeyboardButton("✈️ Поездки")],
        [KeyboardButton("📱 Тренды TikTok")],
        [KeyboardButton("📸 Фотографии")],
        [KeyboardButton("🎮 Игры")],
        [KeyboardButton("🔞 Sexual")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    """Main menu inline keyboard (for callback queries)."""
    keyboard = [
        [InlineKeyboardButton("🎬 Фильмы", callback_data="section:movies")],
        [InlineKeyboardButton("📋 Активности", callback_data="section:activities")],
        [InlineKeyboardButton("✈️ Поездки", callback_data="section:trips")],
        [InlineKeyboardButton("📱 Тренды TikTok", callback_data="section:tiktok")],
        [InlineKeyboardButton("📸 Фотографии", callback_data="section:photos")],
        [InlineKeyboardButton("🎮 Игры", callback_data="section:games")],
        [InlineKeyboardButton("🔞 Sexual", callback_data="section:sexual")]
    ]
    return InlineKeyboardMarkup(keyboard)

def movies_menu_keyboard() -> InlineKeyboardMarkup:
    """Movies section menu."""
    keyboard = [
        [InlineKeyboardButton("📺 Ожидающие просмотра", callback_data="movies:pending")],
        [InlineKeyboardButton("✅ Просмотренные", callback_data="movies:watched")],
        [InlineKeyboardButton("🎲 Случайный фильм", callback_data="movies:random")],
        [InlineKeyboardButton("➕ Добавить фильм", callback_data="movies:add")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def movies_pending_menu_keyboard() -> InlineKeyboardMarkup:
    """Movies pending submenu."""
    keyboard = [
        [InlineKeyboardButton("📋 Общий список", callback_data="movies:pending:all")],
        [InlineKeyboardButton("🎬 Фильмы", callback_data="movies:pending:films")],
        [InlineKeyboardButton("📺 Сериалы", callback_data="movies:pending:series")],
        [InlineKeyboardButton("🎨 Мультики", callback_data="movies:pending:cartoons")],
        [InlineKeyboardButton("🔙 Назад", callback_data="movies:menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def movies_watched_menu_keyboard() -> InlineKeyboardMarkup:
    """Movies watched submenu."""
    keyboard = [
        [InlineKeyboardButton("📋 Общий список", callback_data="movies:watched:all")],
        [InlineKeyboardButton("🏆 Топ-10", callback_data="movies:watched:top")],
        [InlineKeyboardButton("🔙 Назад", callback_data="movies:menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def movies_top_menu_keyboard() -> InlineKeyboardMarkup:
    """Movies top submenu."""
    from config import USERS
    keyboard = [
        [InlineKeyboardButton("🏆 Общий топ", callback_data="movies:top:all")],
    ]
    
    # Добавить кнопки для каждого пользователя
    if len(USERS) >= 1:
        user1_name = USERS[0].get('display_name', 'Пользователь 1')
        keyboard.append([InlineKeyboardButton(f"👤 Топ {user1_name}", callback_data="movies:top:user1")])
    if len(USERS) >= 2:
        user2_name = USERS[1].get('display_name', 'Пользователь 2')
        keyboard.append([InlineKeyboardButton(f"👤 Топ {user2_name}", callback_data="movies:top:user2")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="movies:watched")])
    return InlineKeyboardMarkup(keyboard)

def movie_detail_keyboard(movie_id: int, watched: bool = False) -> InlineKeyboardMarkup:
    """Movie detail actions."""
    keyboard = []
    
    # Кнопка "Просмотрено" только для непросмотренных фильмов
    if not watched:
        keyboard.append([InlineKeyboardButton("✅ Просмотрено", callback_data=f"movie:{movie_id}:watched")])
    
    keyboard.append([InlineKeyboardButton("✏️ Редактировать", callback_data=f"movie:{movie_id}:edit")])
    keyboard.append([InlineKeyboardButton("🗑️ Удалить", callback_data=f"movie:{movie_id}:delete")])
    
    # Кнопка "Назад" - возврат к соответствующему списку
    if watched:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="movies:watched:all")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="movies:pending:all")])
    
    return InlineKeyboardMarkup(keyboard)

def activities_menu_keyboard() -> InlineKeyboardMarkup:
    """Activities section menu."""
    keyboard = [
        [InlineKeyboardButton("📝 Планируемые", callback_data="activities:planned")],
        [InlineKeyboardButton("✅ Выполненные", callback_data="activities:done")],
        [InlineKeyboardButton("➕ Добавить", callback_data="activities:add")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def activity_detail_keyboard(activity_id: int, status: str = "planned") -> InlineKeyboardMarkup:
    """Activity detail actions."""
    keyboard = []
    
    # Кнопка "Выполнено" только для планируемых активностей
    if status == "planned":
        keyboard.append([InlineKeyboardButton("✅ Выполнено", callback_data=f"activity:{activity_id}:done")])
    
    keyboard.append([InlineKeyboardButton("✏️ Редактировать", callback_data=f"activity:{activity_id}:edit")])
    keyboard.append([InlineKeyboardButton("🗑️ Удалить", callback_data=f"activity:{activity_id}:delete")])
    
    # Кнопка "Назад" - возврат к соответствующему списку
    if status == "planned":
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="activities:planned")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="activities:done")])
    
    return InlineKeyboardMarkup(keyboard)

def trips_menu_keyboard() -> InlineKeyboardMarkup:
    """Trips section menu."""
    keyboard = [
        [InlineKeyboardButton("🚶 Пешком", callback_data="trips:walk")],
        [InlineKeyboardButton("🚗 Поездки", callback_data="trips:trips")],
        [InlineKeyboardButton("📍 Места в Херцег-Нови", callback_data="trips:places")],
        [InlineKeyboardButton("➕ Добавить", callback_data="trips:add")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def trip_detail_keyboard(trip_id: int, category_type: Optional[str] = None, visited: bool = False) -> InlineKeyboardMarkup:
    """Trip detail actions."""
    keyboard = []
    if not visited:
        keyboard.append([InlineKeyboardButton("✅ Посещено", callback_data=f"trip:{trip_id}:visited")])
    keyboard.append([InlineKeyboardButton("✏️ Редактировать", callback_data=f"trip:{trip_id}:edit")])
    keyboard.append([InlineKeyboardButton("🗑️ Удалить", callback_data=f"trip:{trip_id}:delete")])
    # Добавить кнопку "Назад" к списку поездок
    if category_type:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"trips:{category_type}")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="trips:menu")])
    return InlineKeyboardMarkup(keyboard)

def tiktok_menu_keyboard() -> InlineKeyboardMarkup:
    """TikTok trends section menu."""
    keyboard = [
        [InlineKeyboardButton("📝 Надо снять", callback_data="tiktok:todo")],
        [InlineKeyboardButton("✅ Снятые", callback_data="tiktok:done")],
        [InlineKeyboardButton("➕ Добавить", callback_data="tiktok:add")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def tiktok_trend_detail_keyboard(trend_id: int, status: str = "todo") -> InlineKeyboardMarkup:
    """TikTok trend detail actions."""
    keyboard = []
    
    # Кнопка "Выполнено" только для невыполненных трендов
    if status == "todo":
        keyboard.append([InlineKeyboardButton("✅ Выполнено", callback_data=f"tiktok:{trend_id}:done")])
    
    keyboard.append([InlineKeyboardButton("🗑️ Удалить", callback_data=f"tiktok:{trend_id}:delete")])
    
    # Кнопка "Назад" - возврат к соответствующему списку
    if status == "todo":
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tiktok:todo")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tiktok:done")])
    
    return InlineKeyboardMarkup(keyboard)

def photos_menu_keyboard() -> InlineKeyboardMarkup:
    """Photos section menu."""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить категорию", callback_data="photos:add")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_menu_keyboard() -> InlineKeyboardMarkup:
    """Games section menu."""
    keyboard = [
        [InlineKeyboardButton("📋 Ожидающие", callback_data="games:pending")],
        [InlineKeyboardButton("✅ Пройденные", callback_data="games:done")],
        [InlineKeyboardButton("🎲 Случайная игра", callback_data="games:random")],
        [InlineKeyboardButton("➕ Добавить", callback_data="games:add")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_done_menu_keyboard() -> InlineKeyboardMarkup:
    """Games done submenu."""
    keyboard = [
        [InlineKeyboardButton("📋 Общий список", callback_data="games:done:all")],
        [InlineKeyboardButton("🏆 Топ-10", callback_data="games:done:top")],
        [InlineKeyboardButton("🔙 Назад", callback_data="games:menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_top_menu_keyboard() -> InlineKeyboardMarkup:
    """Games top submenu."""
    keyboard = [
        [InlineKeyboardButton("🏆 Общий топ", callback_data="games:top:all")],
        [InlineKeyboardButton("👤 Топ пользователя 1", callback_data="games:top:user1")],
        [InlineKeyboardButton("👤 Топ пользователя 2", callback_data="games:top:user2")],
        [InlineKeyboardButton("🔙 Назад", callback_data="games:done")]
    ]
    return InlineKeyboardMarkup(keyboard)

def game_detail_keyboard(game_id: int, status: str = "pending") -> InlineKeyboardMarkup:
    """Game detail actions."""
    keyboard = []
    
    # Кнопка "Пройдено" только для непройденных игр
    if status == "pending":
        keyboard.append([InlineKeyboardButton("✅ Пройдено", callback_data=f"game:{game_id}:done")])
    
    keyboard.append([InlineKeyboardButton("✏️ Редактировать", callback_data=f"game:{game_id}:edit")])
    keyboard.append([InlineKeyboardButton("🗑️ Удалить", callback_data=f"game:{game_id}:delete")])
    
    # Кнопка "Назад" - возврат к соответствующему списку
    if status == "pending":
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="games:pending")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="games:done:all")])
    
    return InlineKeyboardMarkup(keyboard)

def sexual_menu_keyboard() -> InlineKeyboardMarkup:
    """Sexual section menu."""
    keyboard = [
        [InlineKeyboardButton("🏪 Магазины", callback_data="sexual:shops")],
        [InlineKeyboardButton("➕ Добавить", callback_data="sexual:add")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def list_keyboard(items: List[dict], prefix: str, page: int = 0, per_page: int = 10, 
                 back_button: Optional[str] = None, back_callback: Optional[str] = None) -> InlineKeyboardMarkup:
    """Create paginated list keyboard."""
    keyboard = []
    start = page * per_page
    end = start + per_page
    page_items = items[start:end]
    
    for item in page_items:
        keyboard.append([InlineKeyboardButton(
            item.get('title', f"Item {item.get('id')}"),
            callback_data=f"{prefix}:{item.get('id')}"
        )])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"{prefix}:page:{page-1}"))
    if end < len(items):
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"{prefix}:page:{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Добавить кнопку "Назад" или "Главное меню" если указано
    if back_button and back_callback:
        keyboard.append([InlineKeyboardButton(back_button, callback_data=back_callback)])
    
    return InlineKeyboardMarkup(keyboard)

def category_selection_keyboard(categories: List[dict], prefix: str, add_new: bool = True) -> InlineKeyboardMarkup:
    """Create category selection keyboard."""
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(
            cat.get('name', cat.get('title', 'Category')),
            callback_data=f"{prefix}:cat:{cat.get('id')}"
        )])
    
    if add_new:
        keyboard.append([InlineKeyboardButton("➕ Добавить новую категорию", callback_data=f"{prefix}:new_cat")])
    
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=f"{prefix}:cancel")])
    return InlineKeyboardMarkup(keyboard)

def rating_keyboard(item_id: int, item_type: str, user_num: int) -> InlineKeyboardMarkup:
    """Create rating selection keyboard (1-10)."""
    keyboard = []
    row = []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(str(i), callback_data=f"{item_type}:{item_id}:rate:{user_num}:{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel button."""
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

