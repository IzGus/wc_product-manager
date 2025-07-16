"""
Тестовый скрипт для проверки импорта WooCommerce CSV
"""
import logging
from woocommerce_csv_manager import WooCommerceCSVManager
from csv_manager import CSVManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_woocommerce_import():
    """Тестирование импорта WooCommerce CSV"""
    
    # Файл с реальными данными WooCommerce
    test_file = "wc-product-export-16-7-2025-1752664811537 - Тестовый.csv"
    
    print("🧪 Тестирование импорта WooCommerce CSV...")
    print("=" * 50)
    
    # Создаем менеджеры
    csv_manager = CSVManager()
    wc_manager = WooCommerceCSVManager()
    
    try:
        # 1. Тест автоматического определения формата
        print("📋 1. Определение формата CSV...")
        detected_format = csv_manager.detect_csv_format(test_file)
        print(f"   ✅ Обнаружен формат: {detected_format}")
        
        # 2. Тест импорта через WooCommerce менеджер
        print("\n📦 2. Импорт через WooCommerce менеджер...")
        products_wc = wc_manager.import_woocommerce_csv(test_file)
        print(f"   ✅ Импортировано WooCommerce: {len(products_wc)} товаров")
        
        # 3. Тест автоматического импорта
        print("\n🔄 3. Автоматический импорт...")
        products_auto = csv_manager.import_products_from_csv(test_file)
        print(f"   ✅ Импортировано автоматически: {len(products_auto)} товаров")
        
        # 4. Анализ первого товара
        if products_wc:
            product = products_wc[0]
            print(f"\n📊 4. Анализ первого товара:")
            print(f"   🏷️  ID: {product.id}")
            print(f"   📝  Название: {product.name[:50]}...")
            print(f"   🔖  Тип: {product.type}")
            print(f"   📋  SKU: {product.sku}")
            print(f"   💰  Цена: {product.regular_price}")
            print(f"   📷  Изображений: {len(product.images)}")
            print(f"   🏪  Категорий: {len(product.categories)}")
            print(f"   🔧  Атрибутов: {len(product.attributes)}")
            print(f"   📄  Мета-данных: {len(product.meta_data)}")
            print(f"   🔀  Вариаций: {len(product.variations)}")
        
        # 5. Статистика по типам товаров
        if products_wc:
            print(f"\n📈 5. Статистика по типам:")
            type_stats = {}
            for product in products_wc:
                type_stats[product.type] = type_stats.get(product.type, 0) + 1
            
            for ptype, count in type_stats.items():
                print(f"   📦 {ptype}: {count} товаров")
        
        # 6. Тест экспорта обратно в WooCommerce формат
        print(f"\n💾 6. Тест экспорта в WooCommerce формат...")
        export_filename = "test_export_woocommerce.csv"
        success = wc_manager.export_to_woocommerce_csv(products_wc[:5], export_filename)
        if success:
            print(f"   ✅ Экспорт успешен: {export_filename}")
        else:
            print(f"   ❌ Ошибка экспорта")
        
        print("\n🎉 Все тесты завершены!")
        
    except Exception as e:
        print(f"\n❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

def test_comparison():
    """Сравнение простого и WooCommerce импорта"""
    
    print("\n" + "=" * 50)
    print("🔍 Сравнение форматов импорта")
    print("=" * 50)
    
    test_file = "wc-product-export-16-7-2025-1752664811537 - Тестовый.csv"
    
    try:
        csv_manager = CSVManager()
        
        # Простой импорт
        simple_products = csv_manager.import_simple_csv(test_file)
        print(f"📄 Простой импорт: {len(simple_products)} товаров")
        
        # WooCommerce импорт
        wc_products = csv_manager.import_woocommerce_csv(test_file)
        print(f"🛒 WooCommerce импорт: {len(wc_products)} товаров")
        
        print(f"\n📊 Разница: {len(wc_products) - len(simple_products)} товаров")
        
        if wc_products and simple_products:
            print(f"\n🔍 Сравнение первого товара:")
            print(f"Простой формат:")
            print(f"  Название: {simple_products[0].name[:30]}...")
            print(f"  Атрибутов: {len(simple_products[0].attributes)}")
            print(f"  Изображений: {len(simple_products[0].images)}")
            
            print(f"WooCommerce формат:")
            print(f"  Название: {wc_products[0].name[:30]}...")
            print(f"  Атрибутов: {len(wc_products[0].attributes)}")
            print(f"  Изображений: {len(wc_products[0].images)}")
            
    except Exception as e:
        print(f"❌ Ошибка сравнения: {e}")

if __name__ == "__main__":
    # Запуск основного теста
    test_woocommerce_import()
    
    # Запуск сравнения форматов
    test_comparison()
    
    print("\n" + "🎯" * 25)
    print("Тестирование завершено!")
    print("🎯" * 25) 