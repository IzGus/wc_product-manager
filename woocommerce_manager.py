"""
WooCommerce Product Manager - основной класс для работы с API
"""
import logging
from typing import List, Dict, Any, Optional
from woocommerce import API
from config import config_manager
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WooCommerceManager:
    """Класс для управления товарами через WooCommerce REST API"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Инициализация менеджера WooCommerce
        
        Args:
            config: Словарь с настройками подключения (опционально)
        """
        self.api = None
        self.current_config = None
        
        if config:
            self._setup_api_with_config(config)
        else:
            self._setup_api()
    
    def _setup_api(self):
        """Настройка API подключения с текущим профилем"""
        if not config_manager.is_configured():
            logger.warning("API не настроен. Требуется выбрать профиль подключения.")
            return
        
        config = config_manager.get_current_config()
        self._setup_api_with_config(config)
    
    def _setup_api_with_config(self, config: Dict[str, Any]):
        """
        Настройка API подключения с заданной конфигурацией
        
        Args:
            config: Словарь с настройками подключения
        """
        try:
            self.current_config = config
            
            self.api = API(
                url=config.get('site_url', ''),
                consumer_key=config.get('consumer_key', ''),
                consumer_secret=config.get('consumer_secret', ''),
                version=config.get('api_version', 'wc/v3'),
                timeout=config.get('timeout', 30)
            )
            logger.info(f"API инициализирован для {config.get('site_url', 'неизвестный сайт')}")
        except Exception as e:
            logger.error(f"Ошибка инициализации API: {e}")
            self.api = None
            self.current_config = None
    
    def update_config(self, config: Dict[str, Any]):
        """
        Обновление конфигурации подключения
        
        Args:
            config: Новая конфигурация
        """
        self._setup_api_with_config(config)
    
    def is_connected(self) -> bool:
        """Проверка наличия активного подключения"""
        return self.api is not None and self.current_config is not None
    
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
                    "per_page": config_manager.get_current_config().get('products_per_page', 10),
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
                if len(batch) < config_manager.get_current_config().get('products_per_page', 10):
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
    
    def get_variations(self, parent_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех вариаций товара
        
        Args:
            parent_id: ID родительского товара
            
        Returns:
            List[Dict]: Список вариаций
        """
        if not self.api:
            logger.error("API не инициализирован")
            return []
        
        try:
            response = self.api.get(f"products/{parent_id}/variations", params={"per_page": 100})
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка получения вариаций: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка при получении вариаций: {e}")
            return []
    
    def update_variation(self, parent_id: int, variation_id: int, variation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Обновление вариации товара
        
        Args:
            parent_id: ID родительского товара
            variation_id: ID вариации
            variation_data: Новые данные вариации
            
        Returns:
            Dict: Обновленная вариация или None в случае ошибки
        """
        if not self.api:
            logger.error("API не инициализирован")
            return None
        
        try:
            response = self.api.put(f"products/{parent_id}/variations/{variation_id}", variation_data)
            if response.status_code == 200:
                logger.info(f"Вариация обновлена: ID {variation_id} товара {parent_id}")
                return response.json()
            else:
                logger.error(f"Ошибка обновления вариации: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении вариации: {e}")
            return None
    
    def delete_variation(self, parent_id: int, variation_id: int, force: bool = True) -> bool:
        """
        Удаление вариации товара
        
        Args:
            parent_id: ID родительского товара
            variation_id: ID вариации
            force: Полное удаление
            
        Returns:
            bool: True если удаление успешно
        """
        if not self.api:
            logger.error("API не инициализирован")
            return False
        
        try:
            response = self.api.delete(f"products/{parent_id}/variations/{variation_id}", params={"force": force})
            if response.status_code == 200:
                logger.info(f"Вариация удалена: ID {variation_id} товара {parent_id}")
                return True
            else:
                logger.error(f"Ошибка удаления вариации: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при удалении вариации: {e}")
            return False
    
    def batch_create_products(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Пакетное создание товаров
        
        Args:
            products_data: Список данных товаров
            
        Returns:
            Dict: Результат операции с успешными и неудачными товарами
        """
        if not self.api:
            logger.error("API не инициализирован")
            return {"success": [], "errors": []}
        
        batch_data = {
            "create": products_data
        }
        
        try:
            response = self.api.post("products/batch", batch_data)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Пакетное создание: {len(result.get('create', []))} товаров")
                return {
                    "success": result.get('create', []),
                    "errors": []
                }
            else:
                logger.error(f"Ошибка пакетного создания: {response.status_code} - {response.text}")
                return {"success": [], "errors": [{"error": response.text}]}
                
        except Exception as e:
            logger.error(f"Ошибка при пакетном создании: {e}")
            return {"success": [], "errors": [{"error": str(e)}]}
    
    def batch_update_products(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Пакетное обновление товаров
        
        Args:
            products_data: Список данных товаров с ID
            
        Returns:
            Dict: Результат операции
        """
        if not self.api:
            logger.error("API не инициализирован")
            return {"success": [], "errors": []}
        
        batch_data = {
            "update": products_data
        }
        
        try:
            response = self.api.post("products/batch", batch_data)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Пакетное обновление: {len(result.get('update', []))} товаров")
                return {
                    "success": result.get('update', []),
                    "errors": []
                }
            else:
                logger.error(f"Ошибка пакетного обновления: {response.status_code} - {response.text}")
                return {"success": [], "errors": [{"error": response.text}]}
                
        except Exception as e:
            logger.error(f"Ошибка при пакетном обновлении: {e}")
            return {"success": [], "errors": [{"error": str(e)}]}
    
    def batch_delete_products(self, product_ids: List[int], force: bool = True) -> Dict[str, Any]:
        """
        Пакетное удаление товаров
        
        Args:
            product_ids: Список ID товаров для удаления
            force: Полное удаление
            
        Returns:
            Dict: Результат операции
        """
        if not self.api:
            logger.error("API не инициализирован")
            return {"success": [], "errors": []}
        
        delete_data = [{"id": pid} for pid in product_ids]
        batch_data = {
            "delete": delete_data
        }
        
        if force:
            batch_data["force"] = True
        
        try:
            response = self.api.post("products/batch", batch_data)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Пакетное удаление: {len(result.get('delete', []))} товаров")
                return {
                    "success": result.get('delete', []),
                    "errors": []
                }
            else:
                logger.error(f"Ошибка пакетного удаления: {response.status_code} - {response.text}")
                return {"success": [], "errors": [{"error": response.text}]}
                
        except Exception as e:
            logger.error(f"Ошибка при пакетном удалении: {e}")
            return {"success": [], "errors": [{"error": str(e)}]}
    
    def create_variable_product_with_variations(self, product_data: Dict[str, Any], variations_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Создание вариативного товара с вариациями
        
        Args:
            product_data: Данные родительского товара
            variations_data: Список данных вариаций
            
        Returns:
            Dict: Созданный товар с вариациями или None в случае ошибки
        """
        # Создаем родительский товар
        parent_product = self.create_product(product_data)
        if not parent_product:
            return None
        
        parent_id = parent_product["id"]
        created_variations = []
        
        # Создаем вариации
        for variation_data in variations_data:
            variation = self.create_variation(parent_id, variation_data)
            if variation:
                created_variations.append(variation)
            else:
                logger.warning(f"Не удалось создать вариацию для товара {parent_id}")
        
        # Возвращаем полную информацию
        parent_product["variations"] = created_variations
        logger.info(f"Создан вариативный товар {parent_id} с {len(created_variations)} вариациями")
        
        return parent_product 