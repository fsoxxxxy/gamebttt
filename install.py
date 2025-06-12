#!/usr/bin/env python3
"""
Автоустановщик для Telegram бота "Кто Крыса?"
"""

import subprocess
import sys
import os

def install_dependencies():
    """Установка зависимостей"""
    print("Устанавливаю зависимости...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==22.1"])
        print("✅ Зависимости установлены")
    except subprocess.CalledProcessError:
        print("❌ Ошибка установки зависимостей")
        return False
    return True

def check_token():
    """Проверка токена бота"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Переменная TELEGRAM_BOT_TOKEN не установлена")
        print("Получите токен у @BotFather в Telegram и добавьте в переменные окружения:")
        print("export TELEGRAM_BOT_TOKEN='ваш_токен'")
        return False
    print("✅ Токен найден")
    return True

def main():
    print("🎮 Установка Telegram бота 'Кто Крыса?'")
    print("=" * 50)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not check_token():
        print("\nНастройте токен и запустите снова")
        sys.exit(1)
    
    print("\n✅ Установка завершена!")
    print("Запустите бота командой: python main.py")

if __name__ == "__main__":
    main()