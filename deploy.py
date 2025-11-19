"""Deployment script for the bot."""
import os
import json
from pathlib import Path

def main():
    """Main deployment function."""
    print("=" * 50)
    print("Развертывание Telegram-бота")
    print("=" * 50)
    print()
    
    # Get bot token
    print("1. Введите токен бота (получите у @BotFather):")
    bot_token = input("BOT_TOKEN: ").strip()
    if not bot_token:
        print("❌ Токен не может быть пустым!")
        return
    
    # Get users
    print("\n2. Настройка пользователей:")
    print("   Введите Telegram ID и отображаемые псевдонимы для каждого пользователя.")
    print("   (Минимум 2 пользователя)")
    print("   Чтобы узнать свой Telegram ID, напишите боту @userinfobot")
    print()
    
    users = []
    user_count = 1
    
    while True:
        print(f"Пользователь {user_count}:")
        telegram_id = input("  Telegram ID: ").strip()
        
        if not telegram_id:
            if user_count < 3:
                print("  ❌ Нужно минимум 2 пользователя!")
                continue
            else:
                break
        
        try:
            telegram_id = int(telegram_id)
        except ValueError:
            print("  ❌ Telegram ID должен быть числом!")
            continue
        
        display_name = input("  Отображаемое имя: ").strip()
        if not display_name:
            display_name = f"Пользователь {user_count}"
        
        users.append({
            "telegram_id": telegram_id,
            "display_name": display_name
        })
        
        user_count += 1
        
        if user_count > 2:
            add_more = input("\n  Добавить еще пользователя? (y/n): ").strip().lower()
            if add_more != 'y':
                break
    
    if len(users) < 2:
        print("❌ Нужно минимум 2 пользователя!")
        return
    
    # Create .env file
    print("\n3. Создание файла .env...")
    env_content = f"BOT_TOKEN={bot_token}\n"
    
    env_path = Path(".env")
    # Удалить .env если это директория или файл
    if env_path.exists():
        if env_path.is_dir():
            import shutil
            shutil.rmtree(env_path)
            print("   ⚠️  Удалена директория .env (была создана по ошибке)")
        elif env_path.is_file():
            env_path.unlink()
            print("   ⚠️  Удален существующий файл .env")
    
    # Убедиться, что путь свободен
    if env_path.exists():
        raise Exception(f"Не удалось удалить {env_path}. Проверьте права доступа.")
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("   ✅ Файл .env создан")
    
    # Create config.json
    print("\n4. Создание файла config.json...")
    config = {
        "users": users
    }
    
    config_path = Path("config.json")
    # Удалить config.json если это директория
    if config_path.exists() and config_path.is_dir():
        import shutil
        shutil.rmtree(config_path)
        print("   ⚠️  Удалена директория config.json (была создана по ошибке)")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("   ✅ Файл config.json создан")
    
    # Create data directory
    print("\n5. Создание директории data...")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("   ✅ Директория data создана")
    
    # Docker instructions
    print("\n" + "=" * 50)
    print("✅ Конфигурация завершена!")
    print("=" * 50)
    print("\nДля запуска бота выполните:")
    print("  docker-compose up -d")
    print("\nДля просмотра логов:")
    print("  docker-compose logs -f")
    print("\nДля остановки бота:")
    print("  docker-compose down")
    print()

if __name__ == '__main__':
    main()

