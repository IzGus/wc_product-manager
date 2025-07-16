"""
Модели данных для товаров WooCommerce
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ProductImage:
    """Модель изображения товара"""
    src: str
    name: str = ""
    alt: str = ""

@dataclass
class ProductCategory:
    """Модель категории товара"""
    id: int
    name: str = ""

@dataclass
class ProductAttribute:
    """Модель атрибута товара"""
    id: int
    name: str
    options: List[str] = field(default_factory=list)
    visible: bool = True
    variation: bool = False

@dataclass
class ProductVariation:
    """Модель вариации товара"""
    regular_price: str
    sale_price: str = ""
    sku: str = ""
    stock_quantity: Optional[int] = None
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    image: Optional[ProductImage] = None

@dataclass
class Product:
    """Основная модель товара"""
    name: str
    type: str = "simple"  # simple, variable, grouped, external
    sku: str = ""
    regular_price: str = ""
    sale_price: str = ""
    description: str = ""
    short_description: str = ""
    stock_quantity: Optional[int] = None
    manage_stock: bool = False
    stock_status: str = "instock"  # instock, outofstock, onbackorder
    weight: str = ""
    dimensions: Dict[str, str] = field(default_factory=dict)
    categories: List[ProductCategory] = field(default_factory=list)
    images: List[ProductImage] = field(default_factory=list)
    attributes: List[ProductAttribute] = field(default_factory=list)
    variations: List[ProductVariation] = field(default_factory=list)
    meta_data: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "publish"  # publish, draft, private
    featured: bool = False
    virtual: bool = False
    downloadable: bool = False
    
    # Поля для внутреннего использования
    id: Optional[int] = None
    date_created: str = ""
    date_modified: str = ""
    
    # Поля для отслеживания изменений
    _is_new: bool = field(default=False, init=False)
    _is_modified: bool = field(default=False, init=False)
    _is_deleted: bool = field(default=False, init=False)
    _original_data: Optional[Dict[str, Any]] = field(default=None, init=False)
    
    def to_woocommerce_dict(self) -> Dict[str, Any]:
        """Преобразование в формат WooCommerce API"""
        data = {
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "featured": self.featured,
            "description": self.description,
            "short_description": self.short_description,
            "sku": self.sku,
            "virtual": self.virtual,
            "downloadable": self.downloadable
        }
        
        # Добавляем цены только для простых товаров
        if self.type == "simple":
            data.update({
                "regular_price": self.regular_price,
                "sale_price": self.sale_price,
                "manage_stock": self.manage_stock,
                "stock_status": self.stock_status
            })
            
            if self.manage_stock and self.stock_quantity is not None:
                data["stock_quantity"] = self.stock_quantity
        
        # Добавляем физические характеристики
        if self.weight:
            data["weight"] = self.weight
        
        if self.dimensions:
            data["dimensions"] = self.dimensions
        
        # Добавляем категории
        if self.categories:
            data["categories"] = [{"id": cat.id} for cat in self.categories]
        
        # Добавляем изображения
        if self.images:
            data["images"] = [
                {
                    "src": img.src,
                    "name": img.name,
                    "alt": img.alt
                } for img in self.images
            ]
        
        # Добавляем атрибуты
        if self.attributes:
            data["attributes"] = [
                {
                    "id": attr.id,
                    "name": attr.name,
                    "options": attr.options,
                    "visible": attr.visible,
                    "variation": attr.variation
                } for attr in self.attributes
            ]
        
        # Добавляем мета-данные
        if self.meta_data:
            data["meta_data"] = self.meta_data
        
        return data
    
    @classmethod
    def from_woocommerce_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Создание объекта Product из данных WooCommerce API"""
        
        # Категории
        categories = []
        for cat_data in data.get("categories", []):
            categories.append(ProductCategory(
                id=cat_data.get("id", 0),
                name=cat_data.get("name", "")
            ))
        
        # Изображения
        images = []
        for img_data in data.get("images", []):
            images.append(ProductImage(
                src=img_data.get("src", ""),
                name=img_data.get("name", ""),
                alt=img_data.get("alt", "")
            ))
        
        # Атрибуты
        attributes = []
        for attr_data in data.get("attributes", []):
            attributes.append(ProductAttribute(
                id=attr_data.get("id", 0),
                name=attr_data.get("name", ""),
                options=attr_data.get("options", []),
                visible=attr_data.get("visible", True),
                variation=attr_data.get("variation", False)
            ))
        
        # Создаем объект Product
        product = cls(
            name=data.get("name", ""),
            type=data.get("type", "simple"),
            sku=data.get("sku", ""),
            regular_price=str(data.get("regular_price", "")),
            sale_price=str(data.get("sale_price", "")),
            description=data.get("description", ""),
            short_description=data.get("short_description", ""),
            stock_quantity=data.get("stock_quantity"),
            manage_stock=data.get("manage_stock", False),
            stock_status=data.get("stock_status", "instock"),
            weight=str(data.get("weight", "")),
            dimensions=data.get("dimensions", {}),
            categories=categories,
            images=images,
            attributes=attributes,
            meta_data=data.get("meta_data", []),
            status=data.get("status", "publish"),
            featured=data.get("featured", False),
            virtual=data.get("virtual", False),
            downloadable=data.get("downloadable", False),
            id=data.get("id"),
            date_created=data.get("date_created", ""),
            date_modified=data.get("date_modified", "")
        )
        
        # Сохраняем оригинальные данные для отслеживания изменений
        product.save_original_data()
        
        return product
    
    def get_display_info(self) -> Dict[str, str]:
        """Получение информации для отображения в таблице"""
        return {
            "ID": str(self.id or ""),
            "Название": self.name,
            "SKU": self.sku,
            "Тип": self.type,
            "Цена": self.regular_price,
            "Статус": self.status,
            "Остаток": str(self.stock_quantity or "∞"),
            "Категории": ", ".join([cat.name for cat in self.categories])
        }
    
    def mark_as_new(self):
        """Пометить товар как новый"""
        self._is_new = True
        self._is_modified = False
        self._is_deleted = False
    
    def mark_as_modified(self):
        """Пометить товар как измененный"""
        if not self._is_new:
            self._is_modified = True
    
    def mark_as_deleted(self):
        """Пометить товар как удаленный"""
        self._is_deleted = True
        self._is_modified = False
    
    def save_original_data(self):
        """Сохранить оригинальные данные для отслеживания изменений"""
        self._original_data = self.to_woocommerce_dict()
    
    def is_changed(self) -> bool:
        """Проверить, был ли товар изменен"""
        return self._is_new or self._is_modified or self._is_deleted
    
    def get_change_status(self) -> str:
        """Получить статус изменения товара"""
        if self._is_new:
            return "new"
        elif self._is_deleted:
            return "deleted"
        elif self._is_modified:
            return "modified"
        else:
            return "unchanged"
    
    def reset_change_flags(self):
        """Сбросить флаги изменений после успешной синхронизации"""
        self._is_new = False
        self._is_modified = False
        self._is_deleted = False
        self.save_original_data() 