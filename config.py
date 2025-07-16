"""
Конфигурация приложения WooCommerce Product Manager
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class WooCommerceConfig:
    """Конфигурация для подключения к WooCommerce API"""
    
    # API ключи (будут загружены из .env файла или заданы напрямую)
    CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY', 'ck_81441cab99b5265be3d8cce4541df681e2cb8898')
    CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET', 'cs_c1bde4c33aa6dc75d554787667d73076aa680b0b')
    
    # URL сайта (будет настроен пользователем через GUI)
    SITE_URL = os.getenv('WC_SITE_URL', '')
    
    # Версия API
    API_VERSION = 'wc/v3'
    
    # Настройки пагинации
    PRODUCTS_PER_PAGE = 100
    
    # Таймауты запросов
    REQUEST_TIMEOUT = 30
    
    @classmethod
    def is_configured(cls) -> bool:
        """Проверяет, настроены ли все необходимые параметры"""
        return bool(cls.SITE_URL and cls.CONSUMER_KEY and cls.CONSUMER_SECRET)
    
    @classmethod
    def update_site_url(cls, url: str):
        """Обновляет URL сайта"""
        cls.SITE_URL = url.rstrip('/')
        # Сохраняем в переменные окружения
        os.environ['WC_SITE_URL'] = cls.SITE_URL 