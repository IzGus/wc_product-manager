"""
WooCommerce Product Manager - Главный файл запуска приложения

Приложение для управления товарами WordPress + WooCommerce через REST API
Версия: 3.0 Universal

Возможности:
- Подключение к любому WooCommerce сайту
- Профили подключения с быстрым переключением
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
import time

# Добавляем текущую директорию в PATH
sys.path.insert(0, str(Path(__file__).parent))

APP_VERSION = "3.0"
APP_NAME = "WooCommerce Product Manager Universal"

try:
    from main_gui import ProductManagerGUI
except ImportError as e:
    print(f"❌ Ошибка импорта GUI: {e}")
    print("📦 Проверьте, что все зависимости установлены:")
    print("   pip install -r requirements.txt")
    input("\nНажмите Enter для выхода...")
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
    """Проверка зависимостей с кэшированием результата"""
    # Кэш файл для результатов проверки
    cache_file = Path("logs") / ".deps_check_cache"
    
    # Если кэш существует и был создан менее часа назад, используем его
    if cache_file.exists():
        try:
            cache_time = cache_file.stat().st_mtime
            if time.time() - cache_time < 3600:  # 1 час
                return True
        except OSError:
            pass
    
    required_packages = [
        ('customtkinter', 'customtkinter'),
        ('woocommerce', 'woocommerce'),
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('python-dotenv', 'dotenv'),
        ('Pillow', 'PIL')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Отсутствуют необходимые пакеты:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\n📦 Установите недостающие пакеты командой:")
        print("   pip install -r requirements.txt")
        print("\n💡 Или запустите: install_packages.bat")
        return False
    
    # Сохраняем результат успешной проверки в кэш
    try:
        cache_file.touch()
    except OSError:
        pass
    
    print("✅ Все зависимости установлены")
    return True

def print_startup_info():
    """Вывод информации о запуске"""
    print(f"🚀 {APP_NAME} v{APP_VERSION}")
    print("=" * 50)
    print("🌐 Универсальное подключение к любому WooCommerce сайту")
    print("👤 Система профилей для быстрого переключения")
    print("📊 Полное управление товарами через REST API")
    print("=" * 50)

def main():
    """Главная функция"""
    print_startup_info()
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    start_time = time.time()
    
    try:
        # Проверка зависимостей
        logger.info(f"Запуск {APP_NAME} v{APP_VERSION}")
        
        if not check_dependencies():
            logger.error("Не удалось пройти проверку зависимостей")
            input("\nНажмите Enter для выхода...")
            return
        
        # Создание и запуск приложения
        logger.info("Инициализация GUI приложения...")
        
        try:
            app = ProductManagerGUI()
            init_time = time.time() - start_time
            logger.info(f"Приложение инициализировано за {init_time:.2f} сек")
            
            print(f"✅ Приложение готово к работе! (инициализация: {init_time:.2f}с)")
            app.run()
            
        except Exception as e:
            logger.error(f"Ошибка инициализации GUI: {e}")
            print(f"\n❌ Ошибка запуска интерфейса: {e}")
            print("📋 Возможные причины:")
            print("   - Отсутствует дисплей (headless система)")
            print("   - Проблемы с CustomTkinter")
            print("   - Недостаточно прав доступа")
            raise
        
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем (Ctrl+C)")
        print("\n👋 Приложение остановлено пользователем!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        print(f"\n❌ Критическая ошибка: {e}")
        print("📝 Подробности сохранены в logs/app.log")
        print("🔧 Попробуйте перезапустить или обратитесь к документации")
        input("\nНажмите Enter для выхода...")
    
    finally:
        total_time = time.time() - start_time
        logger.info(f"Завершение работы. Общее время: {total_time:.2f} сек")

if __name__ == "__main__":
    main() 