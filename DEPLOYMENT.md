# Руководство по развёртыванию Telegram Multi-List Bot

Подробный сценарий развёртывания бота на выделенном сервере **Ubuntu**. 

Исходный код хранится в репозитории [dxmxrxtskx/tg_forus_bot](https://github.com/dxmxrxtskx/tg_forus_bot).

Следуйте шагам последовательно, чтобы обеспечить корректный запуск и дальнейшую поддержку.

---

## 1. Необходимые компоненты

| Компонент | Назначение | Минимальная версия |
|-----------|------------|--------------------|
| Python | запуск утилит и скриптов | 3.11 |
| Git | загрузка обновлений | актуальная |
| Docker Engine | окружение выполнения | 24.x |
| Docker Compose plugin | оркестрация контейнеров | 2.x |
| Telegram Bot Token | авторизация бота | — |
| Telegram ID пользователей | контроль доступа | ≥ 2 |

Проверка версий:
```
git --version
python3 --version
pip --version
docker --version
docker compose version
```

---

## 2. Подготовка сервера (Ubuntu/Debian)

### Вариант A: Автоматическая установка (рекомендуется)

```bash
# После клонирования репозитория
cd /opt/tg_forus_bot
chmod +x setup_server.sh
sudo ./setup_server.sh
```

Скрипт автоматически установит все необходимые компоненты:
- Обновит систему
- Установит Git, Python, pip, curl
- Установит Docker Engine
- Установит Docker Compose plugin
- Настроит права доступа

### Вариант B: Ручная установка

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip

# Docker Engine
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker $USER

# Docker Compose plugin
sudo apt install -y docker-compose-plugin
```

> После добавления пользователя в группу `docker` выйдите и зайдите снова (`exit`, затем повторное `ssh`).

---

## 3. Получение кода

### Вариант A: Клонирование с GitHub (рекомендуется)
```
cd /opt
sudo git clone https://github.com/YOUR_USERNAME/FU_bot.git
cd FU_bot
sudo chown -R $USER:$USER .
```

### Вариант B: Ручная загрузка
Если проект копируется вручную, убедитесь, что структура каталогов совпадает с описанной в `README.md`.

> **Примечание:** Подробная инструкция по работе с GitHub находится в файле **[GITHUB.md](GITHUB.md)**

---

## 4. Автоматическая настройка (`deploy.py`)

Скрипт создаёт `.env`, `config.json` и каталог `data/`.

```
python3 deploy.py
```

Необходимо ввести:
1. `BOT_TOKEN` (из BotFather)
2. Telegram ID пользователей (минимум два) и отображаемые имена

В результате появятся:
- `.env` — секреты и переменные окружения
- `config.json` — список разрешённых пользователей
- `data/` — каталог с базой `multilists.db`

> Скрипт не запускает контейнер автоматически. Для старта перейдите к шагу с Docker.

---

## 5. Ручная конфигурация (альтернатива)

Если скрипт использовать нельзя:

1. Создайте `.env`:
    ```
    BOT_TOKEN=your_token_here
    ```
2. Создайте `config.json`:
    ```
    {
      "users": [
        {"telegram_id": 123456789, "display_name": "User 1"},
        {"telegram_id": 987654321, "display_name": "User 2"}
      ]
    }
    ```
3. Создайте каталог `data/`:
    ```
    mkdir -p data
    ```

---

## 6. Запуск через Docker Compose

```
docker compose up -d
```

Полезные команды:
```
# Проверить статус
docker compose ps

# Логи
docker compose logs -f

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Обновление с GitHub
git pull
docker compose down
docker compose build
docker compose up -d
```

> База данных хранится на хосте в `./data/multilists.db`, поэтому переустановка контейнера безопасна для данных.

---

## 7. Ручной запуск без Docker (опционально)

1. Создайте виртуальное окружение:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2. Установите зависимости:
    ```
    pip install -r requirements.txt
    ```
3. Убедитесь, что `.env` и `config.json` созданы
4. Запустите:
    ```
    python bot.py
    ```

Для автозапуска без Docker можно настроить systemd-сервис (пример юнита добавьте по необходимости).

---

## 8. Резервное копирование и восстановление

- Настройки: `.env`, `config.json`
- Данные: `data/multilists.db`

Резервная копия:
```
cp data/multilists.db backups/multilists-$(date +%F).db
```

Восстановление:
```
docker compose down
cp backups/multilists-YYYY-MM-DD.db data/multilists.db
docker compose up -d
```

---

## 9. Частые задачи

| Задача | Команда |
|--------|---------|
| Проверить контейнеры | `docker compose ps` |
| Посмотреть логи | `docker compose logs -f` |
| Посмотреть последние логи | `docker compose logs --tail=100` |
| Посмотреть логи конкретного контейнера | `docker compose logs -f bot` |
| Добавить пользователя | обновить `config.json`, затем `docker compose restart` |
| Обновить код с GitHub | `git pull` + сборка/перезапуск |
| Быстрое обновление (скрипт) | `chmod +x update.sh && ./update.sh` |
| Очистить старые образы | `docker image prune -f` |

### Обновление с GitHub (Windows → Ubuntu workflow)

Если вы разрабатываете на **Windows**, а бот работает на **Ubuntu сервере**:

1. **На Windows** (после изменений):
   ```bash
   git_push.bat "Описание изменений"
   ```

2. **На Ubuntu сервере** (через SSH):
   ```bash
   ssh user@your-server-ip
   cd /opt/FU_bot
   ./update.sh
   # Или вручную (ВАЖНО: нужна пересборка!):
   git pull
   docker compose build
   docker compose up -d
   # Или одной командой:
   docker compose up -d --build
   ```
   
   ⚠️ **ВАЖНО**: `docker compose restart` НЕ пересобирает образ и не применяет изменения в коде!

---

## 10. Контрольный чек-лист

- [ ] Установлены Docker, Compose и зависимости
- [ ] Получен Bot Token и Telegram ID
- [ ] Созданы `.env`, `config.json`, `data/`
- [ ] Выполнен `docker compose up -d`
- [ ] Проверены логи (`docker compose logs -f`)
- [ ] Бот отвечает на `/start`
- [ ] Настроено резервное копирование `data/multilists.db`

После выполнения всех шагов бот готов к эксплуатации. Рекомендуется периодически обновлять репозиторий и проверять актуальность зависимостей.
