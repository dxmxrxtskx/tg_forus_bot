#!/bin/bash
# Скрипт для обновления бота на сервере Ubuntu
# Использование: ./update.sh

echo "========================================"
echo "Обновление бота с GitHub"
echo "========================================"
echo

# Проверка, что мы в правильной директории
if [ ! -f "docker-compose.yml" ]; then
    echo "ОШИБКА: docker-compose.yml не найден"
    echo "Убедитесь, что вы находитесь в директории проекта"
    exit 1
fi

echo "[1/3] Получение изменений с GitHub..."
git pull
if [ $? -ne 0 ]; then
    echo "ОШИБКА: Не удалось получить изменения"
    exit 1
fi
echo

echo "[2/3] Остановка контейнера..."
docker compose down
echo

echo "[3/3] Пересборка и запуск..."
docker compose build
docker compose up -d
if [ $? -ne 0 ]; then
    echo "ОШИБКА: Не удалось запустить контейнер"
    exit 1
fi
echo

echo "========================================"
echo "Обновление завершено!"
echo "========================================"
echo
echo "Проверьте логи: docker compose logs -f"

