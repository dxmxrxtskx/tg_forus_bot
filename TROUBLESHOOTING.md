# Устранение неполадок

## Как проверить логи на сервере

### 1. Подключитесь к серверу по SSH:
```bash
ssh user@your-server-ip
cd /opt/tg_forus_bot  # или ваш путь к проекту
```

### 2. Просмотр логов:

**Посмотреть последние 100 строк логов:**
```bash
docker compose logs --tail=100
```

**Следить за логами в реальном времени:**
```bash
docker compose logs -f
```

**Посмотреть логи только бота:**
```bash
docker compose logs -f bot
```

**Посмотреть логи с фильтрацией по ошибкам:**
```bash
docker compose logs | grep -i error
docker compose logs | grep -i exception
docker compose logs | grep -i traceback
```

### 3. Проверка состояния контейнера:
```bash
docker compose ps
```

Если контейнер не запущен или перезапускается, проверьте логи.

---

## Частые проблемы и решения

### Проблема: Раздел не открывается

**Проверьте:**
1. Логи на наличие ошибок:
   ```bash
   docker compose logs --tail=50 | grep -i error
   ```

2. Что обработчик зарегистрирован в `bot.py`

3. Что функция меню правильно обрабатывает `callback_query`:
   - Должна проверять `if update.callback_query`
   - Должна вызывать `await query.answer()`
   - Должна использовать `await query.edit_message_text()`

### Проблема: Кнопка не работает

**Проверьте:**
1. Что `callback_data` в клавиатуре совпадает с паттерном в обработчике
2. Что обработчик зарегистрирован в `get_*_handlers()`
3. Логи на наличие ошибок при нажатии кнопки

### Проблема: Данные не сохраняются

**Проверьте:**
1. Что база данных существует:
   ```bash
   ls -la data/multilists.db
   ```

2. Права доступа к файлу базы данных:
   ```bash
   ls -la data/
   ```

3. Логи на наличие ошибок SQL

### Проблема: После обновления ничего не работает

**Решение:**
1. Убедитесь, что пересобрали образ:
   ```bash
   docker compose build
   docker compose up -d
   ```

2. Проверьте, что код обновился:
   ```bash
   git pull
   git log -1
   ```

3. Перезапустите контейнер:
   ```bash
   docker compose restart
   ```

---

## Диагностика конкретных разделов

### TikTok - тренды не открываются

**Проверьте в логах:**
- Ошибки при вызове `get_tiktok_trend()`
- Ошибки при обработке `tiktok_trend_detail`
- Правильность `callback_data` в `list_keyboard`

**Проверьте в коде:**
- Обработчик `tiktok_trend_detail` зарегистрирован с паттерном `^tiktok:\d+$`
- Функция `get_tiktok_trend()` существует в `database.py`

### Фотографии - раздел не работает

**Проверьте в логах:**
- Ошибки при вызове `photos_menu`
- Ошибки при обработке `callback_query` из `section_handler`
- Ошибки при вызове `get_photo_categories()`

**Проверьте в коде:**
- Обработчик `photos_menu` зарегистрирован
- Функция правильно обрабатывает `update.callback_query`
- `section_handler` вызывает `photos_menu` для секции "photos"

### Игры - список "Ожидающие" не открывается

**Проверьте в логах:**
- Ошибки при вызове `games_pending`
- Ошибки при вызове `games_pending_list`
- Конфликты паттернов обработчиков

**Проверьте в коде:**
- Обработчик `games_pending` зарегистрирован с паттерном `^games:pending$`
- Обработчик `games_pending_list` зарегистрирован с паттерном `^games:pending:`
- Порядок регистрации (более специфичный паттерн должен быть первым)

### Sexual - раздел не работает

**Проверьте в логах:**
- Ошибки при вызове `sexual_menu`
- Ошибки при обработке `callback_query` из `section_handler`
- Ошибки при вызове `get_sexual_categories()`

**Проверьте в коде:**
- Импорт `get_sexual` в `handlers/sexual.py`
- Обработчик `sexual_menu` правильно обрабатывает `update.callback_query`
- `section_handler` вызывает `sexual_menu` для секции "sexual"

---

## Полезные команды для отладки

```bash
# Проверить статус контейнеров
docker compose ps

# Перезапустить контейнер
docker compose restart

# Остановить и запустить заново
docker compose down
docker compose up -d

# Войти в контейнер (для отладки)
docker compose exec bot bash

# Проверить файлы в контейнере
docker compose exec bot ls -la /app

# Проверить базу данных
docker compose exec bot python3 -c "from database import get_connection; conn = get_connection(); print('DB OK')"
```

---

## Если ничего не помогает

1. **Соберите информацию:**
   ```bash
   docker compose logs --tail=200 > logs.txt
   docker compose ps > status.txt
   ```

2. **Проверьте версии:**
   ```bash
   python3 --version
   docker --version
   docker compose version
   ```

3. **Проверьте конфигурацию:**
   ```bash
   cat .env
   cat config.json
   ```

4. **Пересоздайте контейнер:**
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

