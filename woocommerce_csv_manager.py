"""
Менеджер для работы с форматом CSV выгрузки WooCommerce
Поддерживает оригинальный формат экспорта WooCommerce с русскими заголовками
"""
import pandas as pd
import logging
from typing import List, Dict, Any, Optional, Tuple
from product_models import Product, ProductCategory, ProductImage, ProductAttribute, ProductVariation
import json
import re

logger = logging.getLogger(__name__)

class WooCommerceCSVManager:
    """Класс для работы с CSV файлами в формате WooCommerce"""
    
    def __init__(self):
        """Инициализация менеджера WooCommerce CSV"""
        
        # Маппинг полей: наш формат -> WooCommerce формат
        self.field_mapping = {
            'id': 'ID',
            'type': 'Тип',
            'sku': 'Артикул',
            'name': 'Имя',
            'regular_price': 'Базовая цена',
            'sale_price': 'Акционная цена',
            'description': 'Описание',
            'short_description': 'Краткое описание',
            'status': 'Опубликован',
            'featured': 'Рекомендуемый?',
            'stock_status': 'Наличие',
            'stock_quantity': 'Запасы',
            'manage_stock': None,  # Будет вычисляться
            'weight': 'Вес (г)',
            'categories': 'Категории',
            'images': 'Изображения',
            'visibility': 'Видимость в каталоге',
            'virtual': None,  # В WC формате нет прямого поля
            'downloadable': None,  # В WC формате нет прямого поля
        }
        
        # Обратный маппинг: WooCommerce формат -> наш формат
        self.reverse_mapping = {v: k for k, v in self.field_mapping.items() if v}
        
        # Дополнительные поля WooCommerce
        self.wc_extra_fields = [
            'GTIN, UPC, EAN или ISBN',
            'Дата начала действия скидки',
            'Дата окончания действия скидки',
            'Статус налога',
            'Налоговый класс',
            'Величина малых запасов',
            'Возможен ли предзаказ?',
            'Продано индивидуально?',
            'Длина (мм)',
            'Ширина (мм)',
            'Высота (мм)',
            'Разрешить отзывы от клиентов?',
            'Примечание к покупке',
            'Метки',
            'Класс доставки',
            'Лимит скачивания',
            'Дней срока скачивания',
            'Родительский',
            'Сгруппированные товары',
            'Апсэлы',
            'Кросселы',
            'Внешний URL',
            'Текст кнопки',
            'Позиция',
            'Бренды',
            'Бренд'
        ]
        
        # Атрибуты (до 21 атрибута в WooCommerce)
        self.attribute_fields = []
        for i in range(1, 22):
            self.attribute_fields.extend([
                f'Название атрибута {i}',
                f'Значения атрибутов {i}',
                f'Видимость атрибута {i}',
                f'Глобальный атрибут {i}'
            ])
        
        # Мета-поля (Yoast SEO и другие)
        self.meta_fields = [
            'Мета: _yoast_wpseo_title',
            'Мета: _yoast_wpseo_metadesc',
            'Мета: _yfym_cargo_types',
            'Мета: _yfym_individual_vat',
            'Мета: _yfym_condition',
            'Мета: _yfym_quality',
            'Мета: _yoast_wpseo_primary_pwb-brand',
            'Мета: _yoast_wpseo_primary_product_brand',
            'Мета: _yoast_wpseo_primary_product_cat',
            'Мета: _yoast_wpseo_primary_yfym_collection',
            'Мета: _yoast_wpseo_focuskw',
            'Мета: _yoast_wpseo_linkdex',
            'Мета: _yoast_wpseo_content_score',
            'Мета: _yoast_wpseo_estimated-reading-time-minutes',
            'Мета: _yoast_wpseo_bctitle',
            'Мета: _yfym_barcode'
        ]
    
    def detect_csv_format(self, filename: str) -> str:
        """
        Определение формата CSV файла
        
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
    
    def import_woocommerce_csv(self, filename: str) -> List[Product]:
        """
        Импорт товаров из CSV файла WooCommerce формата
        
        Args:
            filename: Имя CSV файла
            
        Returns:
            List[Product]: Список импортированных товаров
        """
        try:
            # Читаем CSV файл
            df = pd.read_csv(filename, encoding='utf-8-sig')
            
            logger.info(f"Загружен CSV файл: {len(df)} строк, {len(df.columns)} колонок")
            
            products = []
            variations_data = {}  # Для хранения вариаций
            
            for index, row in df.iterrows():
                try:
                    product_type = row.get('Тип', 'simple')
                    
                    if product_type == 'variable':
                        # Основной вариативный товар
                        product = self._parse_wc_product_row(row)
                        if product:
                            products.append(product)
                            variations_data[product.id] = []
                    
                    elif product_type == 'variation':
                        # Вариация товара
                        variation = self._parse_wc_variation_row(row)
                        if variation:
                            parent_id = row.get('Родительский')
                            if parent_id and parent_id in variations_data:
                                variations_data[parent_id].append(variation)
                    
                    else:
                        # Простой товар
                        product = self._parse_wc_product_row(row)
                        if product:
                            products.append(product)
                            
                except Exception as e:
                    logger.error(f"Ошибка обработки строки {index + 1}: {e}")
                    continue
            
            # Добавляем вариации к родительским товарам
            for product in products:
                if product.id in variations_data:
                    product.variations = variations_data[product.id]
            
            logger.info(f"Импортировано {len(products)} товаров из WooCommerce CSV")
            return products
            
        except Exception as e:
            logger.error(f"Ошибка импорта WooCommerce CSV: {e}")
            return []
    
    def _parse_wc_product_row(self, row: pd.Series) -> Optional[Product]:
        """Парсинг строки основного товара из WooCommerce CSV"""
        try:
            # Основные поля
            product = Product(
                name=str(row.get('Имя', '')),
                type=str(row.get('Тип', 'simple')),
                sku=str(row.get('Артикул', '')),
                regular_price=str(row.get('Базовая цена', '')),
                sale_price=str(row.get('Акционная цена', '')),
                description=self._clean_text(str(row.get('Описание', ''))),
                short_description=self._clean_text(str(row.get('Краткое описание', ''))),
                status='publish' if row.get('Опубликован', 0) == 1 else 'draft',
                featured=bool(row.get('Рекомендуемый?', 0)),
                stock_status=str(row.get('Наличие', 'instock')),
                weight=str(row.get('Вес (г)', '')),
                id=int(row.get('ID', 0)) if pd.notna(row.get('ID')) else None
            )
            
            # Остатки
            if pd.notna(row.get('Запасы')):
                try:
                    product.stock_quantity = int(row['Запасы'])
                    product.manage_stock = True
                except (ValueError, TypeError):
                    product.manage_stock = False
            
            # Размеры
            dimensions = {}
            if pd.notna(row.get('Длина (мм)')):
                dimensions['length'] = str(row['Длина (мм)'])
            if pd.notna(row.get('Ширина (мм)')):
                dimensions['width'] = str(row['Ширина (мм)'])
            if pd.notna(row.get('Высота (мм)')):
                dimensions['height'] = str(row['Высота (мм)'])
            product.dimensions = dimensions
            
            # Категории
            categories_str = row.get('Категории', '')
            if pd.notna(categories_str) and categories_str:
                categories = self._parse_categories(str(categories_str))
                product.categories = categories
            
            # Изображения
            images_str = row.get('Изображения', '')
            if pd.notna(images_str) and images_str:
                images = self._parse_images(str(images_str))
                product.images = images
            
            # Атрибуты
            attributes = self._parse_attributes(row)
            product.attributes = attributes
            
            # Мета-данные
            meta_data = self._parse_meta_data(row)
            product.meta_data = meta_data
            
            return product
            
        except Exception as e:
            logger.error(f"Ошибка парсинга товара: {e}")
            return None
    
    def _parse_wc_variation_row(self, row: pd.Series) -> Optional[ProductVariation]:
        """Парсинг строки вариации из WooCommerce CSV"""
        try:
            variation = ProductVariation(
                regular_price=str(row.get('Базовая цена', '')),
                sale_price=str(row.get('Акционная цена', '')),
                sku=str(row.get('Артикул', ''))
            )
            
            # Остатки
            if pd.notna(row.get('Запасы')):
                try:
                    variation.stock_quantity = int(row['Запасы'])
                except (ValueError, TypeError):
                    pass
            
            # Атрибуты вариации (упрощенно)
            attributes = []
            for i in range(1, 22):
                attr_name = row.get(f'Название атрибута {i}')
                attr_value = row.get(f'Значения атрибутов {i}')
                if pd.notna(attr_name) and pd.notna(attr_value):
                    attributes.append({
                        'name': str(attr_name),
                        'option': str(attr_value)
                    })
            
            variation.attributes = attributes
            
            # Изображение вариации
            images_str = row.get('Изображения', '')
            if pd.notna(images_str) and images_str:
                images = self._parse_images(str(images_str))
                if images:
                    variation.image = images[0]
            
            return variation
            
        except Exception as e:
            logger.error(f"Ошибка парсинга вариации: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов"""
        if not text or text == 'nan':
            return ''
        
        # Убираем \n и лишние пробелы
        text = re.sub(r'\\n', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _parse_categories(self, categories_str: str) -> List[ProductCategory]:
        """Парсинг категорий из строки"""
        categories = []
        try:
            # Категории разделены запятыми или | 
            category_names = re.split(r'[,|]', categories_str)
            for i, name in enumerate(category_names):
                name = name.strip()
                if name:
                    categories.append(ProductCategory(
                        id=i + 1000,  # Примерный ID
                        name=name
                    ))
        except Exception as e:
            logger.warning(f"Ошибка парсинга категорий: {e}")
        
        return categories
    
    def _parse_images(self, images_str: str) -> List[ProductImage]:
        """Парсинг изображений из строки"""
        images = []
        try:
            # Изображения разделены запятыми
            image_urls = images_str.split(',')
            for url in image_urls:
                url = url.strip()
                if url and url.startswith('http'):
                    images.append(ProductImage(
                        src=url,
                        name='',
                        alt=''
                    ))
        except Exception as e:
            logger.warning(f"Ошибка парсинга изображений: {e}")
        
        return images
    
    def _parse_attributes(self, row: pd.Series) -> List[ProductAttribute]:
        """Парсинг атрибутов из строки WooCommerce"""
        attributes = []
        try:
            for i in range(1, 22):
                attr_name = row.get(f'Название атрибута {i}')
                attr_values = row.get(f'Значения атрибутов {i}')
                attr_visible = row.get(f'Видимость атрибута {i}', 1)
                attr_global = row.get(f'Глобальный атрибут {i}', 0)
                
                if pd.notna(attr_name) and pd.notna(attr_values):
                    # Значения могут быть разделены | или ,
                    values = re.split(r'[|,]', str(attr_values))
                    values = [v.strip() for v in values if v.strip()]
                    
                    if values:
                        attributes.append(ProductAttribute(
                            id=i,
                            name=str(attr_name),
                            options=values,
                            visible=bool(attr_visible),
                            variation=False  # Определяется отдельно
                        ))
        except Exception as e:
            logger.warning(f"Ошибка парсинга атрибутов: {e}")
        
        return attributes
    
    def _parse_meta_data(self, row: pd.Series) -> List[Dict[str, Any]]:
        """Парсинг мета-данных из строки WooCommerce"""
        meta_data = []
        try:
            for field in self.meta_fields:
                value = row.get(field)
                if pd.notna(value) and value:
                    # Убираем префикс "Мета: "
                    key = field.replace('Мета: ', '')
                    meta_data.append({
                        'key': key,
                        'value': str(value)
                    })
        except Exception as e:
            logger.warning(f"Ошибка парсинга мета-данных: {e}")
        
        return meta_data
    
    def export_to_woocommerce_csv(self, products: List[Product], filename: str) -> bool:
        """
        Экспорт товаров в формат WooCommerce CSV
        
        Args:
            products: Список товаров
            filename: Имя файла для сохранения
            
        Returns:
            bool: True если экспорт успешен
        """
        try:
            # Создаем заголовки WooCommerce
            headers = self._get_woocommerce_headers()
            
            # Подготавливаем данные
            rows = []
            for product in products:
                # Основной товар
                row = self._product_to_wc_row(product)
                rows.append(row)
                
                # Вариации товара
                if product.variations:
                    for variation in product.variations:
                        var_row = self._variation_to_wc_row(variation, product)
                        rows.append(var_row)
            
            # Создаем DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Сохраняем в CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            logger.info(f"Экспорт в WooCommerce CSV завершен: {len(rows)} строк в файл {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экспорта в WooCommerce CSV: {e}")
            return False
    
    def _get_woocommerce_headers(self) -> List[str]:
        """Получение заголовков WooCommerce CSV"""
        headers = [
            'ID', 'Тип', 'Артикул', 'GTIN, UPC, EAN или ISBN', 'Имя',
            'Опубликован', 'Рекомендуемый?', 'Видимость в каталоге',
            'Краткое описание', 'Описание',
            'Дата начала действия скидки', 'Дата окончания действия скидки',
            'Статус налога', 'Налоговый класс', 'Наличие', 'Запасы',
            'Величина малых запасов', 'Возможен ли предзаказ?',
            'Продано индивидуально?', 'Вес (г)', 'Длина (мм)',
            'Ширина (мм)', 'Высота (мм)', 'Разрешить отзывы от клиентов?',
            'Примечание к покупке', 'Акционная цена', 'Базовая цена',
            'Категории', 'Метки', 'Класс доставки', 'Изображения',
            'Лимит скачивания', 'Дней срока скачивания', 'Родительский',
            'Сгруппированные товары', 'Апсэлы', 'Кросселы',
            'Внешний URL', 'Текст кнопки', 'Позиция', 'Бренды', 'Бренд'
        ]
        
        # Добавляем атрибуты
        headers.extend(self.attribute_fields)
        
        # Добавляем мета-поля
        headers.extend(self.meta_fields)
        
        return headers
    
    def _product_to_wc_row(self, product: Product) -> Dict[str, Any]:
        """Преобразование Product в строку WooCommerce CSV"""
        row = {}
        
        # Основные поля
        row['ID'] = product.id or ''
        row['Тип'] = product.type
        row['Артикул'] = product.sku
        row['Имя'] = product.name
        row['Опубликован'] = 1 if product.status == 'publish' else 0
        row['Рекомендуемый?'] = 1 if product.featured else 0
        row['Видимость в каталоге'] = 'visible'
        row['Краткое описание'] = product.short_description
        row['Описание'] = product.description
        row['Базовая цена'] = product.regular_price
        row['Акционная цена'] = product.sale_price
        row['Наличие'] = product.stock_status
        row['Запасы'] = product.stock_quantity if product.manage_stock else ''
        row['Вес (г)'] = product.weight
        
        # Размеры
        if product.dimensions:
            row['Длина (мм)'] = product.dimensions.get('length', '')
            row['Ширина (мм)'] = product.dimensions.get('width', '')
            row['Высота (мм)'] = product.dimensions.get('height', '')
        
        # Категории
        if product.categories:
            categories_str = ', '.join([cat.name for cat in product.categories])
            row['Категории'] = categories_str
        
        # Изображения
        if product.images:
            images_str = ', '.join([img.src for img in product.images])
            row['Изображения'] = images_str
        
        # Атрибуты
        for i, attr in enumerate(product.attributes[:21], 1):
            row[f'Название атрибута {i}'] = attr.name
            row[f'Значения атрибутов {i}'] = ' | '.join(attr.options)
            row[f'Видимость атрибута {i}'] = 1 if attr.visible else 0
            row[f'Глобальный атрибут {i}'] = 1
        
        # Мета-данные
        for meta in product.meta_data:
            meta_field = f"Мета: {meta['key']}"
            if meta_field in self.meta_fields:
                row[meta_field] = meta['value']
        
        # Заполняем пустые поля
        for header in self._get_woocommerce_headers():
            if header not in row:
                row[header] = ''
        
        return row
    
    def _variation_to_wc_row(self, variation: ProductVariation, parent: Product) -> Dict[str, Any]:
        """Преобразование ProductVariation в строку WooCommerce CSV"""
        row = {}
        
        # Основные поля вариации
        row['ID'] = ''  # WooCommerce присвоит автоматически
        row['Тип'] = 'variation'
        row['Артикул'] = variation.sku
        row['Имя'] = parent.name
        row['Опубликован'] = 1
        row['Рекомендуемый?'] = 0
        row['Видимость в каталоге'] = 'visible'
        row['Базовая цена'] = variation.regular_price
        row['Акционная цена'] = variation.sale_price
        row['Наличие'] = 'instock'
        row['Запасы'] = variation.stock_quantity or ''
        row['Родительский'] = parent.id
        
        # Атрибуты вариации
        for i, attr in enumerate(variation.attributes[:21], 1):
            row[f'Название атрибута {i}'] = attr.get('name', '')
            row[f'Значения атрибутов {i}'] = attr.get('option', '')
            row[f'Видимость атрибута {i}'] = 1
            row[f'Глобальный атрибут {i}'] = 1
        
        # Изображение вариации
        if variation.image:
            row['Изображения'] = variation.image.src
        
        # Заполняем пустые поля
        for header in self._get_woocommerce_headers():
            if header not in row:
                row[header] = ''
        
        return row 