@echo off
chcp 65001 >nul
REM Скрипт для первоначальной настройки Git репозитория (Windows)

echo ========================================
echo Настройка Git репозитория для GitHub
echo ========================================
echo.

REM Проверка и настройка Git конфигурации
echo [0/6] Проверка конфигурации Git...
git config --global user.name >nul 2>&1
if errorlevel 1 (
    echo Git не настроен. Необходимо указать имя и email.
    echo.
    set /p GIT_NAME="Введите ваше имя для Git: "
    if not "%GIT_NAME%"=="" (
        git config --global user.name "%GIT_NAME%"
    )
    set /p GIT_EMAIL="Введите ваш email для Git: "
    if not "%GIT_EMAIL%"=="" (
        git config --global user.email "%GIT_EMAIL%"
    )
    echo.
) else (
    echo Git уже настроен.
)
echo.

REM Проверка, инициализирован ли Git
if not exist ".git" (
    echo [1/6] Инициализация Git репозитория...
    git init
    if errorlevel 1 (
        echo ОШИБКА: Git не установлен или не найден в PATH
        echo Установите Git с https://git-scm.com/download/win
        exit /b 1
    )
    echo Готово!
) else (
    echo [1/6] Git репозиторий уже инициализирован
)
echo.

echo [2/6] Добавление всех файлов...
git add .
echo Готово!
echo.

echo [3/6] Создание первого коммита...
git commit -m "Initial commit: Telegram Multi-List Bot"
if errorlevel 1 (
    echo ВНИМАНИЕ: Не удалось создать коммит
    echo Возможно, нет изменений или не настроен Git
    echo.
    echo Если Git не настроен, выполните вручную:
    echo git config --global user.name "Ваше имя"
    echo git config --global user.email "your.email@example.com"
    echo git commit --amend --reset-author
)
echo.

echo [4/6] Настройка ветки main...
git branch -M main
echo Готово!
echo.

echo [5/6] Настройка удаленного репозитория
echo.
echo ВАЖНО: Сначала создайте репозиторий на GitHub!
echo 1. Зайдите на https://github.com
echo 2. Создайте новый репозиторий (НЕ добавляйте README, .gitignore, лицензию)
echo 3. Скопируйте URL репозитория
echo.
set /p REPO_URL="Введите URL репозитория (https://github.com/USERNAME/REPO.git): "

if "%REPO_URL%"=="" (
    echo Пропущено. Вы можете добавить репозиторий позже командой:
    echo git remote add origin YOUR_REPO_URL
    echo git push -u origin main
) else (
    git remote add origin %REPO_URL%
    if errorlevel 1 (
        echo ВНИМАНИЕ: Не удалось добавить удаленный репозиторий
        echo Возможно, он уже добавлен. Проверьте командой: git remote -v
    ) else (
        echo Удаленный репозиторий добавлен!
        echo.
        echo Для отправки кода выполните:
        echo git push -u origin main
    )
)
echo.

echo ========================================
echo Настройка завершена!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Убедитесь, что репозиторий создан на GitHub
echo 2. Выполните: git push -u origin main
echo 3. Для дальнейшей работы используйте: git_push.bat "Описание"
echo.

