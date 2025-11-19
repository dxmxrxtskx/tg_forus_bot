#!/bin/bash
# Скрипт автоматической установки бота на Ubuntu сервере
# Использование: ./setup_server.sh

set -e  # Остановить при ошибке

echo "========================================"
echo "Установка Telegram Multi-List Bot"
echo "========================================"
echo

# Проверка, что скрипт запущен от root или с sudo
if [ "$EUID" -ne 0 ]; then 
    echo "ОШИБКА: Скрипт должен быть запущен с правами root или через sudo"
    echo "Использование: sudo ./setup_server.sh"
    exit 1
fi

echo "[1/7] Обновление системы..."
apt update && apt upgrade -y
echo "✅ Готово"
echo

echo "[2/7] Установка базовых зависимостей..."
apt install -y git python3 python3-pip curl
echo "✅ Готово"
echo

echo "[3/7] Установка Docker Engine..."
if command -v docker &> /dev/null; then
    echo "Docker уже установлен, пропускаем..."
else
    curl -fsSL https://get.docker.com | bash
    echo "✅ Docker установлен"
fi
echo

echo "[4/7] Установка Docker Compose plugin..."
if command -v docker compose &> /dev/null; then
    echo "Docker Compose уже установлен, пропускаем..."
else
    apt install -y docker-compose-plugin
    echo "✅ Docker Compose установлен"
fi
echo

echo "[5/7] Проверка установки..."
docker --version
docker compose version
echo

echo "[6/7] Настройка прав доступа..."
# Если скрипт запущен не от root, добавить пользователя в группу docker
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    echo "✅ Пользователь $SUDO_USER добавлен в группу docker"
    echo "⚠️  ВНИМАНИЕ: Выйдите и зайдите снова, чтобы права вступили в силу"
else
    echo "⚠️  Работаете от root, пропускаем настройку прав"
fi
echo

echo "[7/7] Проверка работоспособности Docker..."
if docker ps &> /dev/null; then
    echo "✅ Docker работает корректно"
else
    echo "⚠️  ВНИМАНИЕ: Docker может требовать перезагрузки или повторного входа"
fi
echo

echo "========================================"
echo "✅ Установка завершена!"
echo "========================================"
echo
echo "Следующие шаги:"
echo "1. Если вы не root, выйдите и зайдите снова (exit, затем ssh)"
echo "2. Перейдите в директорию проекта: cd /opt/tg_forus_bot"
echo "3. Запустите настройку бота: python3 deploy.py"
echo "4. Запустите бота: docker compose up -d"
echo

