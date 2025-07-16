"""
Модуль для работы с CSV файлами - импорт и экспорт товаров
Поддерживает как простой формат, так и формат WooCommerce
"""
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from product_models import Product, ProductCategory, ProductImage, ProductAttribute
import json

logger = logging.getLogger(__name__)

class CSVManager:
    """Класс для работы с CSV файлами"""
    
    def __init__(self):
        """Инициализация менеджера CSV"""
        self.required_columns = [
            'name', 'type', 'sku', 'regular_price', 'description', 'status'
        ]
        
        self.optional_columns = [
            'sale_price', 'short_description', 'stock_quantity', 
            'manage_stock', 'stock_status', 'weight', 'categories',
            'images', 'attributes', 'meta_data', 'featured',
            'virtual', 'downloadable'
        ]
    
    def export_products_to_csv(self, products: List[Product], filename: str) -> bool:
        """
        Экспорт товаров в CSV файл
        
        Args:
            products: Список товаров
            filename: Имя файла для сохранения
            
        Returns:
            bool: True если экспорт успешен
        """
        try:
            # Преобразуем товары в DataFrame
            data = []
            for product in products:
                row = {
                    'id': product.id,
                    'name': product.name,
                    'type': product.type,
                    'sku': product.sku,
                    'regular_price': product.regular_price,
                    'sale_price': product.sale_price,
                    'description': product.description,
                    'short_description': product.short_description,
                    'stock_quantity': product.stock_quantity,
                    'manage_stock': product.manage_stock,
                    'stock_status': product.stock_status,
                    'weight': product.weight,
                    'status': product.status,
                    'featured': product.featured,
                    'virtual': product.virtual,
                    'downloadable': product.downloadable,
                    'date_created': product.date_created,
                    'date_modified': product.date_modified
                }
                
                # Преобразуем сложные поля в JSON строки
                row['categories'] = json.dumps([
                    {'id': cat.id, 'name': cat.name} for cat in product.categories
                ], ensure_ascii=False)
                
                row['images'] = json.dumps([
                    {'src': img.src, 'name': img.name, 'alt': img.alt} 
                    for img in product.images
                ], ensure_ascii=False)
                
                row['attributes'] = json.dumps([
                    {
                        'id': attr.id,
                        'name': attr.name,
                        'options': attr.options,
                        'visible': attr.visible,
                        'variation': attr.variation
                    } for attr in product.attributes
                ], ensure_ascii=False)
                
                row['meta_data'] = json.dumps(product.meta_data, ensure_ascii=False)
                row['dimensions'] = json.dumps(product.dimensions, ensure_ascii=False)
                
                data.append(row)
            
            # Создаем DataFrame и сохраняем в CSV
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            logger.info(f"Экспорт завершен: {len(products)} товаров в файл {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экспорта в CSV: {e}")
            return False
    
    def detect_csv_format(self, filename: str) -> str:
        """
        Определение формата CSV файла
        
        Args:
            filename: Имя CSV файла
            
        Returns:
            str: 'woocommerce' или 'simple'
        """
        try:
            # Читаем только заголовки
            df = pd.read_csv(filename, nrows=0, encoding='utf-8-sig')
            columns = list(df.columns)
            
            # Проверяем наличие характерных полей WooCommerce
            wc_indicators = ['ID', 'Тип', 'Артикул', 'Имя', 'Базовая цена']
            found_indicators = sum(1 for indicator in wc_indicators if indicator in columns)
            
            if found_indicators >= 3:
                logger.info("Обнаружен формат WooCommerce CSV")
                return 'woocommerce'
            else:
                logger.info("Обнаружен простой формат CSV")
                return 'simple'
                
        except Exception as e:
            logger.error(f"Ошибка определения формата CSV: {e}")
            return 'simple'

    def import_products_from_csv(self, filename: str) -> List[Product]:
        """
        Импорт товаров из CSV файла с автоматическим определением формата
        
        Args:
            filename: Имя CSV файла
            
        Returns:
            List[Product]: Список импортированных товаров
        """
        # Определяем формат файла
        csv_format = self.detect_csv_format(filename)
        
        if csv_format == 'woocommerce':
            return self.import_woocommerce_csv(filename)
        else:
            return self.import_simple_csv(filename)

    def import_simple_csv(self, filename: str) -> List[Product]:
        """
        Импорт товаров из простого CSV файла
        
        Args:
            filename: Имя CSV файла
            
        Returns:
            List[Product]: Список импортированных товаров
        """
        try:
            # Читаем CSV файл
            df = pd.read_csv(filename, encoding='utf-8-sig')
            
            # Проверяем наличие обязательных колонок
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Отсутствуют обязательные колонки: {missing_columns}")
                return []
            
            products = []
            
            for index, row in df.iterrows():
                try:
                    # Создаем базовый товар
                    product = Product(
                        name=str(row['name']),
                        type=str(row.get('type', 'simple')),
                        sku=str(row.get('sku', '')),
                        regular_price=str(row.get('regular_price', '')),
                        sale_price=str(row.get('sale_price', '')),
                        description=str(row.get('description', '')),
                        short_description=str(row.get('short_description', '')),
                        status=str(row.get('status', 'publish')),
                        featured=bool(row.get('featured', False)),
                        virtual=bool(row.get('virtual', False)),
                        downloadable=bool(row.get('downloadable', False)),
                        weight=str(row.get('weight', '')),
                        manage_stock=bool(row.get('manage_stock', False)),
                        stock_status=str(row.get('stock_status', 'instock'))
                    )
                    
                    # Добавляем количество на складе
                    if pd.notna(row.get('stock_quantity')):
                        product.stock_quantity = int(row['stock_quantity'])
                    
                    # Парсим JSON поля
                    if pd.notna(row.get('categories')):
                        try:
                            cats_data = json.loads(row['categories'])
                            product.categories = [
                                ProductCategory(id=cat.get('id', 0), name=cat.get('name', ''))
                                for cat in cats_data
                            ]
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Ошибка парсинга категорий в строке {index + 1}")
                    
                    if pd.notna(row.get('images')):
                        try:
                            imgs_data = json.loads(row['images'])
                            product.images = [
                                ProductImage(
                                    src=img.get('src', ''),
                                    name=img.get('name', ''),
                                    alt=img.get('alt', '')
                                ) for img in imgs_data
                            ]
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Ошибка парсинга изображений в строке {index + 1}")
                    
                    if pd.notna(row.get('attributes')):
                        try:
                            attrs_data = json.loads(row['attributes'])
                            product.attributes = [
                                ProductAttribute(
                                    id=attr.get('id', 0),
                                    name=attr.get('name', ''),
                                    options=attr.get('options', []),
                                    visible=attr.get('visible', True),
                                    variation=attr.get('variation', False)
                                ) for attr in attrs_data
                            ]
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Ошибка парсинга атрибутов в строке {index + 1}")
                    
                    if pd.notna(row.get('meta_data')):
                        try:
                            product.meta_data = json.loads(row['meta_data'])
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Ошибка парсинга мета-данных в строке {index + 1}")
                    
                    if pd.notna(row.get('dimensions')):
                        try:
                            product.dimensions = json.loads(row['dimensions'])
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Ошибка парсинга размеров в строке {index + 1}")
                    
                    products.append(product)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки строки {index + 1}: {e}")
                    continue
            
            logger.info(f"Импорт простого CSV завершен: {len(products)} товаров из файла {filename}")
            return products
            
        except Exception as e:
            logger.error(f"Ошибка импорта простого CSV: {e}")
            return []

    def import_woocommerce_csv(self, filename: str) -> List[Product]:
        """
        Импорт товаров из CSV файла WooCommerce формата
        
        Args:
            filename: Имя CSV файла
            
        Returns:
            List[Product]: Список импортированных товаров
        """
        try:
            from woocommerce_csv_manager import WooCommerceCSVManager
            wc_manager = WooCommerceCSVManager()
            products = wc_manager.import_woocommerce_csv(filename)
            logger.info(f"Импорт WooCommerce CSV завершен: {len(products)} товаров")
            return products
        except ImportError:
            logger.error("WooCommerceCSVManager не найден, используется простой импорт")
            return self.import_simple_csv(filename)
        except Exception as e:
            logger.error(f"Ошибка импорта WooCommerce CSV: {e}")
            return []
    
    def validate_csv_structure(self, filename: str) -> Dict[str, Any]:
        """
        Валидация структуры CSV файла
        
        Args:
            filename: Имя CSV файла
            
        Returns:
            Dict: Результат валидации
        """
        try:
            df = pd.read_csv(filename, encoding='utf-8-sig')
            
            result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'total_rows': len(df),
                'columns': list(df.columns)
            }
            
            # Проверяем обязательные колонки
            missing_required = [col for col in self.required_columns if col not in df.columns]
            if missing_required:
                result['valid'] = False
                result['errors'].append(f"Отсутствуют обязательные колонки: {missing_required}")
            
            # Проверяем наличие данных
            if len(df) == 0:
                result['valid'] = False
                result['errors'].append("CSV файл пуст")
            
            # Проверяем уникальность SKU
            if 'sku' in df.columns:
                duplicate_skus = df[df['sku'].duplicated() & df['sku'].notna()]
                if not duplicate_skus.empty:
                    result['warnings'].append(f"Найдены дубликаты SKU: {list(duplicate_skus['sku'])}")
            
            # Проверяем обязательные поля
            for col in self.required_columns:
                if col in df.columns:
                    empty_values = df[df[col].isna() | (df[col] == '')].index.tolist()
                    if empty_values:
                        result['warnings'].append(f"Пустые значения в колонке '{col}' в строках: {empty_values}")
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Ошибка чтения файла: {e}"],
                'warnings': [],
                'total_rows': 0,
                'columns': []
            } 