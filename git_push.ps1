# PowerShell скрипт для быстрой загрузки изменений на GitHub
# Использование: .\git_push.ps1 "Описание изменений"

param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Загрузка изменений на GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Проверка статуса..." -ForegroundColor Yellow
git status
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Git не найден или не инициализирован" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[2/4] Добавление всех изменений..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Не удалось добавить файлы" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[3/4] Создание коммита..." -ForegroundColor Yellow
git commit -m $Message
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Не удалось создать коммит" -ForegroundColor Red
    Write-Host "Возможно, нет изменений для коммита" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

Write-Host "[4/4] Отправка на GitHub..." -ForegroundColor Yellow
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Не удалось отправить на GitHub" -ForegroundColor Red
    Write-Host "Проверьте подключение к интернету и настройки Git" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "Готово! Изменения загружены на GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

