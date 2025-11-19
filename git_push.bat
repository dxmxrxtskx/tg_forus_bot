@echo off
chcp 65001 >nul 2>&1
REM Скрипт для быстрой загрузки изменений на GitHub (Windows)

if "%~1"=="" (
    echo Использование: .\git_push.bat "Описание изменений"
    echo Пример: .\git_push.bat "Добавлена поддержка новых категорий"
    exit /b 1
)

echo ========================================
echo Загрузка изменений на GitHub
echo ========================================
echo.

echo [1/4] Проверка статуса...
git status
echo.

echo [2/4] Добавление всех изменений...
git add .
if errorlevel 1 (
    echo ОШИБКА: Не удалось добавить файлы
    exit /b 1
)
echo.

echo [3/4] Создание коммита...
setlocal enabledelayedexpansion
set "commit_msg=%~1"
:loop
shift
if "%~1"=="" goto endloop
set "commit_msg=!commit_msg! %~1"
goto loop
:endloop
git commit -m "!commit_msg!"
endlocal
if errorlevel 1 (
    echo ОШИБКА: Не удалось создать коммит
    echo Возможно, нет изменений для коммита
    exit /b 1
)
echo.

echo [4/4] Отправка на GitHub...
git push
if errorlevel 1 (
    echo ОШИБКА: Не удалось отправить на GitHub
    echo Проверьте подключение к интернету и настройки Git
    exit /b 1
)
echo.

echo ========================================
echo Готово! Изменения загружены на GitHub
echo ========================================

