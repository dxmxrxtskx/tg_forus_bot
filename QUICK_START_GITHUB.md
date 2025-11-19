# Быстрый старт с GitHub

## Первый раз (настройка)

1. **Установите Git** (если еще не установлен):
   - Windows: https://git-scm.com/download/win
   - Linux: `sudo apt install git`
   - Mac: `brew install git`

2. **Создайте репозиторий на GitHub**:
   - Зайдите на https://github.com
   - Нажмите "New repository"
   - Название: `FU_bot`
   - Выберите Private (рекомендуется)
   - **НЕ** создавайте README, .gitignore или лицензию

3. **Настройте локальный репозиторий**:
   ```bash
   # Windows
   git_setup.bat
   
   # Linux/Mac
   chmod +x git_setup.sh  # если есть
   # или вручную:
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/FU_bot.git
   git push -u origin main
   ```

## Ежедневная работа

### Загрузить изменения на GitHub:

**Windows:**

**PowerShell (рекомендуется):**
```powershell
.\git_push.ps1 "Описание ваших изменений"
```

**CMD или PowerShell (альтернатива):**
```bash
.\git_push.bat "Описание ваших изменений"
```

> **Важно:** В PowerShell обязательно используйте `.\` перед именем скрипта!

**Linux/Mac:**
```bash
chmod +x git_push.sh
./git_push.sh "Описание ваших изменений"
```

**Или вручную:**
```bash
git add .
git commit -m "Описание изменений"
git push
```

### Получить обновления с GitHub:

```bash
git pull
```

---

**Подробная инструкция:** см. [GITHUB.md](GITHUB.md)

