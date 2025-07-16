"""
Конфигурация приложения WooCommerce Product Manager
Поддержка универсальных настроек и профилей подключения
"""
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionProfile:
    """Профиль подключения к WooCommerce API"""
    
    def __init__(self, name: str = "", site_url: str = "", consumer_key: str = "", 
                 consumer_secret: str = "", api_version: str = "wc/v3", 
                 timeout: int = 30, products_per_page: int = 100):
        self.name = name
        self.site_url = site_url.rstrip('/') if site_url else ""
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_version = api_version
        self.timeout = timeout
        self.products_per_page = products_per_page
        self.created_at = datetime.now().isoformat()
        self.last_used = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сохранения"""
        return {
            "name": self.name,
            "site_url": self.site_url,
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "products_per_page": self.products_per_page,
            "created_at": self.created_at,
            "last_used": self.last_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConnectionProfile':
        """Создание из словаря"""
        profile = cls(
            name=data.get("name", ""),
            site_url=data.get("site_url", ""),
            consumer_key=data.get("consumer_key", ""),
            consumer_secret=data.get("consumer_secret", ""),
            api_version=data.get("api_version", "wc/v3"),
            timeout=data.get("timeout", 30),
            products_per_page=data.get("products_per_page", 100)
        )
        profile.created_at = data.get("created_at", datetime.now().isoformat())
        profile.last_used = data.get("last_used")
        return profile
    
    def is_valid(self) -> bool:
        """Проверка валидности профиля"""
        return bool(self.name and self.site_url and self.consumer_key and self.consumer_secret)
    
    def update_last_used(self):
        """Обновление времени последнего использования"""
        self.last_used = datetime.now().isoformat()

class WooCommerceConfig:
    """Универсальная конфигурация для подключения к любому WooCommerce сайту"""
    
    CONFIG_FILE = "wc_connections.json"
    
    def __init__(self):
        self.profiles: Dict[str, ConnectionProfile] = {}
        self.current_profile: Optional[ConnectionProfile] = None
        self.load_profiles()
    
    def load_profiles(self):
        """Загрузка профилей подключения из файла"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for profile_data in data.get("profiles", []):
                    profile = ConnectionProfile.from_dict(profile_data)
                    self.profiles[profile.name] = profile
                
                # Загружаем текущий профиль
                current_profile_name = data.get("current_profile")
                if current_profile_name and current_profile_name in self.profiles:
                    self.current_profile = self.profiles[current_profile_name]
                    
                logger.info(f"Загружено {len(self.profiles)} профилей подключения")
                    
            except Exception as e:
                logger.error(f"Ошибка загрузки профилей: {e}")
                self.profiles = {}
                self.current_profile = None
    
    def save_profiles(self):
        """Сохранение профилей подключения в файл"""
        try:
            data = {
                "profiles": [profile.to_dict() for profile in self.profiles.values()],
                "current_profile": self.current_profile.name if self.current_profile else None,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Сохранено {len(self.profiles)} профилей подключения")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения профилей: {e}")
    
    def add_profile(self, profile: ConnectionProfile) -> bool:
        """Добавление нового профиля"""
        if not profile.is_valid():
            logger.error("Профиль не валиден")
            return False
        
        if profile.name in self.profiles:
            logger.warning(f"Профиль '{profile.name}' уже существует")
            return False
        
        self.profiles[profile.name] = profile
        self.save_profiles()
        logger.info(f"Добавлен профиль '{profile.name}'")
        return True
    
    def update_profile(self, profile: ConnectionProfile) -> bool:
        """Обновление существующего профиля"""
        if not profile.is_valid():
            logger.error("Профиль не валиден")
            return False
        
        self.profiles[profile.name] = profile
        
        # Если это текущий профиль, обновляем его
        if self.current_profile and self.current_profile.name == profile.name:
            self.current_profile = profile
        
        self.save_profiles()
        logger.info(f"Обновлен профиль '{profile.name}'")
        return True
    
    def delete_profile(self, profile_name: str) -> bool:
        """Удаление профиля"""
        if profile_name not in self.profiles:
            logger.error(f"Профиль '{profile_name}' не найден")
            return False
        
        del self.profiles[profile_name]
        
        # Если удаляем текущий профиль, сбрасываем его
        if self.current_profile and self.current_profile.name == profile_name:
            self.current_profile = None
        
        self.save_profiles()
        logger.info(f"Удален профиль '{profile_name}'")
        return True
    
    def set_current_profile(self, profile_name: str) -> bool:
        """Установка текущего профиля"""
        if profile_name not in self.profiles:
            logger.error(f"Профиль '{profile_name}' не найден")
            return False
        
        self.current_profile = self.profiles[profile_name]
        self.current_profile.update_last_used()
        self.save_profiles()
        logger.info(f"Установлен текущий профиль '{profile_name}'")
        return True
    
    def get_profile_names(self) -> List[str]:
        """Получение списка имен профилей"""
        return list(self.profiles.keys())
    
    def get_profile(self, name: str) -> Optional[ConnectionProfile]:
        """Получение профиля по имени"""
        return self.profiles.get(name)
    
    def is_configured(self) -> bool:
        """Проверка, настроен ли текущий профиль"""
        return self.current_profile is not None and self.current_profile.is_valid()
    
    def get_current_config(self) -> Dict[str, Any]:
        """Получение конфигурации текущего профиля"""
        if not self.current_profile:
            return {}
        
        return {
            "site_url": self.current_profile.site_url,
            "consumer_key": self.current_profile.consumer_key,
            "consumer_secret": self.current_profile.consumer_secret,
            "api_version": self.current_profile.api_version,
            "timeout": self.current_profile.timeout,
            "products_per_page": self.current_profile.products_per_page
        }
    
    def create_quick_profile(self, site_url: str, consumer_key: str, consumer_secret: str) -> ConnectionProfile:
        """Создание быстрого профиля без сохранения"""
        # Генерируем имя профиля из URL
        profile_name = self._generate_profile_name(site_url)
        
        return ConnectionProfile(
            name=profile_name,
            site_url=site_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret
        )
    
    def _generate_profile_name(self, site_url: str) -> str:
        """Генерация имени профиля из URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(site_url)
            domain = parsed.netloc or parsed.path
            return domain.replace('www.', '').replace('.', '_')
        except:
            return f"profile_{len(self.profiles) + 1}"
    
    def export_profiles(self, filename: str) -> bool:
        """Экспорт профилей в файл"""
        try:
            data = {
                "export_date": datetime.now().isoformat(),
                "profiles": [profile.to_dict() for profile in self.profiles.values()]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Профили экспортированы в {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экспорта: {e}")
            return False
    
    def import_profiles(self, filename: str) -> bool:
        """Импорт профилей из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for profile_data in data.get("profiles", []):
                profile = ConnectionProfile.from_dict(profile_data)
                if profile.name not in self.profiles:
                    self.profiles[profile.name] = profile
                    imported_count += 1
            
            if imported_count > 0:
                self.save_profiles()
            
            logger.info(f"Импортировано {imported_count} новых профилей")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка импорта: {e}")
            return False

# Глобальный экземпляр конфигурации
config_manager = WooCommerceConfig()

# Совместимость со старым API
class WooCommerceConfig_Legacy:
    """Класс для обратной совместимости"""
    
    @classmethod
    def is_configured(cls) -> bool:
        return config_manager.is_configured()
    
    @classmethod
    def update_site_url(cls, url: str):
        # Для обратной совместимости
        if config_manager.current_profile:
            config_manager.current_profile.site_url = url.rstrip('/')
    
    @property
    def SITE_URL(self):
        return config_manager.current_profile.site_url if config_manager.current_profile else ""
    
    @property
    def CONSUMER_KEY(self):
        return config_manager.current_profile.consumer_key if config_manager.current_profile else ""
    
    @property
    def CONSUMER_SECRET(self):
        return config_manager.current_profile.consumer_secret if config_manager.current_profile else ""
    
    @property
    def API_VERSION(self):
        return config_manager.current_profile.api_version if config_manager.current_profile else "wc/v3"
    
    @property
    def REQUEST_TIMEOUT(self):
        return config_manager.current_profile.timeout if config_manager.current_profile else 30
    
    @property
    def PRODUCTS_PER_PAGE(self):
        return config_manager.current_profile.products_per_page if config_manager.current_profile else 100

# Экземпляр для обратной совместимости
WooCommerceConfig = WooCommerceConfig_Legacy() 