"""
WooCommerce Product Manager - Главный файл запуска приложения

Приложение для управления товарами WordPress + WooCommerce через REST API

Возможности:
- Загрузка товаров с сайта
- Создание и редактирование товаров  
- Поддержка вариативных товаров
- Импорт/экспорт CSV
- Управление атрибутами и категориями
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем текущую директорию в PATH
sys.path.insert(0, str(Path(__file__).parent))

try:
    from main_gui import ProductManagerGUI
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Проверьте, что все зависимости установлены:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """Настройка логирования"""
    # Создаем папку для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Проверка зависимостей"""
    required_packages = [
        'customtkinter',
        'woocommerce',
        'pandas',
        'requests',
        'python-dotenv',
        'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Отсутствуют необходимые пакеты:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Установите недостающие пакеты командой:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def main():
    """Главная функция"""
    print("🚀 Запуск WooCommerce Product Manager...")
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Проверка зависимостей
        if not check_dependencies():
            input("\nНажмите Enter для выхода...")
            return
        
        # Создание и запуск приложения
        logger.info("Запуск GUI приложения")
        app = ProductManagerGUI()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
        print("\n👋 До свидания!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
        print("Подробности в файле logs/app.log")
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main() 