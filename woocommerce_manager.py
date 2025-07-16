"""
WooCommerce Product Manager - основной класс для работы с API
"""
import logging
from typing import List, Dict, Any, Optional
from woocommerce import API
from config import WooCommerceConfig
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WooCommerceManager:
    """Класс для управления товарами через WooCommerce REST API"""
    
    def __init__(self, site_url: str = None):
        """
        Инициализация менеджера WooCommerce
        
        Args:
            site_url: URL сайта WordPress/WooCommerce
        """
        if site_url:
            WooCommerceConfig.update_site_url(site_url)
        
        self.api = None
        self._setup_api()
    
    def _setup_api(self):
        """Настройка API подключения"""
        if not WooCommerceConfig.is_configured():
            logger.warning("API не настроен. Требуется URL сайта.")
            return
        
        try:
            self.api = API(
                url=WooCommerceConfig.SITE_URL,
                consumer_key=WooCommerceConfig.CONSUMER_KEY,
                consumer_secret=WooCommerceConfig.CONSUMER_SECRET,
                version=WooCommerceConfig.API_VERSION,
                timeout=WooCommerceConfig.REQUEST_TIMEOUT
            )
            logger.info(f"API инициализирован для {WooCommerceConfig.SITE_URL}")
        except Exception as e:
            logger.error(f"Ошибка инициализации API: {e}")
            self.api = None
    
    def test_connection(self) -> bool:
        """
        Тестирование подключения к API
        
        Returns:
            bool: True если подключение успешно
        """
        if not self.api:
            return False
        
        try:
            response = self.api.get("products", params={"per_page": 1})
            if response.status_code == 200:
                logger.info("Подключение к WooCommerce API успешно!")
                return True
            else:
                logger.error(f"Ошибка подключения: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Ошибка тестирования подключения: {e}")
            return False
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Получение всех товаров с сайта
        
        Returns:
            List[Dict]: Список всех товаров
        """
        if not self.api:
            logger.error("API не инициализирован")
            return []
        
        products = []
        page = 1
        
        try:
            while True:
                logger.info(f"Загрузка страницы {page}...")
                response = self.api.get("products", params={
                    "per_page": WooCommerceConfig.PRODUCTS_PER_PAGE,
                    "page": page
                })
                
                if response.status_code != 200:
                    logger.error(f"Ошибка получения товаров: {response.status_code}")
                    break
                
                batch = response.json()
                if not batch:
                    break
                
                products.extend(batch)
                page += 1
                
                # Проверяем, есть ли еще страницы
                if len(batch) < WooCommerceConfig.PRODUCTS_PER_PAGE:
                    break
            
            logger.info(f"Загружено {len(products)} товаров")
            return products
            
        except Exception as e:
            logger.error(f"Ошибка при получении товаров: {e}")
            return []
    
    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Создание нового товара
        
        Args:
            product_data: Данные товара
            
        Returns:
            Dict: Созданный товар или None в случае ошибки
        """
        if not self.api:
            logger.error("API не инициализирован")
            return None
        
        try:
            response = self.api.post("products", product_data)
            if response.status_code == 201:
                logger.info(f"Товар создан: {product_data.get('name', 'Без названия')}")
                return response.json()
            else:
                logger.error(f"Ошибка создания товара: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при создании товара: {e}")
            return None
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Обновление существующего товара
        
        Args:
            product_id: ID товара
            product_data: Новые данные товара
            
        Returns:
            Dict: Обновленный товар или None в случае ошибки
        """
        if not self.api:
            logger.error("API не инициализирован")
            return None
        
        try:
            response = self.api.put(f"products/{product_id}", product_data)
            if response.status_code == 200:
                logger.info(f"Товар обновлен: ID {product_id}")
                return response.json()
            else:
                logger.error(f"Ошибка обновления товара: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении товара: {e}")
            return None
    
    def delete_product(self, product_id: int, force: bool = True) -> bool:
        """
        Удаление товара
        
        Args:
            product_id: ID товара
            force: Полное удаление (True) или в корзину (False)
            
        Returns:
            bool: True если удаление успешно
        """
        if not self.api:
            logger.error("API не инициализирован")
            return False
        
        try:
            response = self.api.delete(f"products/{product_id}", params={"force": force})
            if response.status_code == 200:
                logger.info(f"Товар удален: ID {product_id}")
                return True
            else:
                logger.error(f"Ошибка удаления товара: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при удалении товара: {e}")
            return False
    
    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Поиск товара по SKU
        
        Args:
            sku: Артикул товара
            
        Returns:
            Dict: Найденный товар или None
        """
        if not self.api:
            logger.error("API не инициализирован")
            return None
        
        try:
            response = self.api.get("products", params={"sku": sku})
            if response.status_code == 200:
                products = response.json()
                if products:
                    return products[0]
            return None
            
        except Exception as e:
            logger.error(f"Ошибка поиска товара по SKU: {e}")
            return None
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Получение всех категорий товаров
        
        Returns:
            List[Dict]: Список категорий
        """
        if not self.api:
            logger.error("API не инициализирован")
            return []
        
        try:
            response = self.api.get("products/categories", params={"per_page": 100})
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка получения категорий: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка при получении категорий: {e}")
            return []
    
    def get_attributes(self) -> List[Dict[str, Any]]:
        """
        Получение всех атрибутов товаров
        
        Returns:
            List[Dict]: Список атрибутов
        """
        if not self.api:
            logger.error("API не инициализирован")
            return []
        
        try:
            response = self.api.get("products/attributes", params={"per_page": 100})
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка получения атрибутов: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка при получении атрибутов: {e}")
            return []
    
    def create_variation(self, parent_id: int, variation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Создание вариации товара
        
        Args:
            parent_id: ID родительского товара
            variation_data: Данные вариации
            
        Returns:
            Dict: Созданная вариация или None в случае ошибки
        """
        if not self.api:
            logger.error("API не инициализирован")
            return None
        
        try:
            response = self.api.post(f"products/{parent_id}/variations", variation_data)
            if response.status_code == 201:
                logger.info(f"Вариация создана для товара ID {parent_id}")
                return response.json()
            else:
                logger.error(f"Ошибка создания вариации: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при создании вариации: {e}")
            return None 