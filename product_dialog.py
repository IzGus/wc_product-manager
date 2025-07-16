"""
Диалоговое окно для создания и редактирования товаров
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any, Optional
import json

from product_models import Product, ProductCategory, ProductImage, ProductAttribute

class ProductDialog:
    """Диалоговое окно для работы с товарами"""
    
    def __init__(self, parent, product: Optional[Product] = None, categories: List[Dict] = None, attributes: List[Dict] = None):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
            product: Товар для редактирования (None для создания нового)
            categories: Список доступных категорий
            attributes: Список доступных атрибутов
        """
        self.parent = parent
        self.product = product
        self.categories = categories or []
        self.attributes = attributes or []
        self.result = None
        
        # Создаем диалоговое окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Редактирование товара" if product else "Новый товар")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self.center_window()
        
        self.setup_ui()
        
        # Заполняем поля, если редактируем существующий товар
        if self.product:
            self.fill_fields()
    
    def center_window(self):
        """Центрирование окна относительно родительского"""
        self.window.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.window.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Создаем notebook для вкладок
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Основная информация
        self.setup_main_tab()
        
        # Категории и атрибуты
        self.setup_categories_tab()
        
        # Изображения
        self.setup_images_tab()
        
        # Дополнительно
        self.setup_advanced_tab()
        
        # Кнопки управления
        self.setup_buttons()
    
    def setup_main_tab(self):
        """Основная информация о товаре"""
        main_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(main_frame, text="Основное")
        
        # Скроллируемая область
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Название товара
        name_frame = ctk.CTkFrame(scrollable_frame)
        name_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(name_frame, text="Название товара*:", width=120).pack(side="left", padx=5)
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="Введите название товара")
        self.name_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # SKU
        sku_frame = ctk.CTkFrame(scrollable_frame)
        sku_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(sku_frame, text="SKU:", width=120).pack(side="left", padx=5)
        self.sku_entry = ctk.CTkEntry(sku_frame, placeholder_text="Уникальный артикул")
        self.sku_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Тип товара
        type_frame = ctk.CTkFrame(scrollable_frame)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(type_frame, text="Тип товара:", width=120).pack(side="left", padx=5)
        self.type_var = ctk.StringVar(value="simple")
        self.type_combo = ctk.CTkComboBox(type_frame, values=["simple", "variable", "grouped", "external"], variable=self.type_var)
        self.type_combo.pack(side="left", padx=5)
        
        # Статус
        status_frame = ctk.CTkFrame(scrollable_frame)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(status_frame, text="Статус:", width=120).pack(side="left", padx=5)
        self.status_var = ctk.StringVar(value="publish")
        self.status_combo = ctk.CTkComboBox(status_frame, values=["publish", "draft", "private"], variable=self.status_var)
        self.status_combo.pack(side="left", padx=5)
        
        # Цены
        price_frame = ctk.CTkFrame(scrollable_frame)
        price_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(price_frame, text="Обычная цена:", width=120).pack(side="left", padx=5)
        self.regular_price_entry = ctk.CTkEntry(price_frame, placeholder_text="0.00", width=100)
        self.regular_price_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(price_frame, text="Цена со скидкой:", width=120).pack(side="left", padx=5)
        self.sale_price_entry = ctk.CTkEntry(price_frame, placeholder_text="0.00", width=100)
        self.sale_price_entry.pack(side="left", padx=5)
        
        # Остатки
        stock_frame = ctk.CTkFrame(scrollable_frame)
        stock_frame.pack(fill="x", padx=10, pady=5)
        
        self.manage_stock_var = ctk.BooleanVar()
        self.manage_stock_cb = ctk.CTkCheckBox(stock_frame, text="Управлять остатками", variable=self.manage_stock_var, command=self.on_manage_stock_change)
        self.manage_stock_cb.pack(side="left", padx=5)
        
        ctk.CTkLabel(stock_frame, text="Количество:", width=120).pack(side="left", padx=5)
        self.stock_quantity_entry = ctk.CTkEntry(stock_frame, placeholder_text="0", width=100, state="disabled")
        self.stock_quantity_entry.pack(side="left", padx=5)
        
        self.stock_status_var = ctk.StringVar(value="instock")
        self.stock_status_combo = ctk.CTkComboBox(stock_frame, values=["instock", "outofstock", "onbackorder"], variable=self.stock_status_var, width=120)
        self.stock_status_combo.pack(side="left", padx=5)
        
        # Описания
        desc_frame = ctk.CTkFrame(scrollable_frame)
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(desc_frame, text="Краткое описание:").pack(anchor="w", padx=5, pady=2)
        self.short_desc_text = ctk.CTkTextbox(desc_frame, height=60)
        self.short_desc_text.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(desc_frame, text="Полное описание:").pack(anchor="w", padx=5, pady=2)
        self.description_text = ctk.CTkTextbox(desc_frame, height=120)
        self.description_text.pack(fill="x", padx=5, pady=2)
        
        # Физические характеристики
        physical_frame = ctk.CTkFrame(scrollable_frame)
        physical_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(physical_frame, text="Вес (кг):", width=120).pack(side="left", padx=5)
        self.weight_entry = ctk.CTkEntry(physical_frame, placeholder_text="0", width=100)
        self.weight_entry.pack(side="left", padx=5)
        
        # Размеры
        ctk.CTkLabel(physical_frame, text="Размеры (Д×Ш×В):").pack(side="left", padx=10)
        self.length_entry = ctk.CTkEntry(physical_frame, placeholder_text="Длина", width=80)
        self.length_entry.pack(side="left", padx=2)
        self.width_entry = ctk.CTkEntry(physical_frame, placeholder_text="Ширина", width=80)
        self.width_entry.pack(side="left", padx=2)
        self.height_entry = ctk.CTkEntry(physical_frame, placeholder_text="Высота", width=80)
        self.height_entry.pack(side="left", padx=2)
        
        # Флаги товара
        flags_frame = ctk.CTkFrame(scrollable_frame)
        flags_frame.pack(fill="x", padx=10, pady=5)
        
        self.featured_var = ctk.BooleanVar()
        self.featured_cb = ctk.CTkCheckBox(flags_frame, text="Рекомендуемый", variable=self.featured_var)
        self.featured_cb.pack(side="left", padx=5)
        
        self.virtual_var = ctk.BooleanVar()
        self.virtual_cb = ctk.CTkCheckBox(flags_frame, text="Виртуальный", variable=self.virtual_var)
        self.virtual_cb.pack(side="left", padx=5)
        
        self.downloadable_var = ctk.BooleanVar()
        self.downloadable_cb = ctk.CTkCheckBox(flags_frame, text="Загружаемый", variable=self.downloadable_var)
        self.downloadable_cb.pack(side="left", padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_categories_tab(self):
        """Вкладка категорий и атрибутов"""
        cat_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(cat_frame, text="Категории и атрибуты")
        
        # Категории
        categories_frame = ctk.CTkFrame(cat_frame)
        categories_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(categories_frame, text="Категории товара", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Список категорий с чекбоксами
        self.categories_frame = ctk.CTkScrollableFrame(categories_frame, height=150)
        self.categories_frame.pack(fill="x", padx=5, pady=5)
        
        self.category_vars = {}
        for category in self.categories:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(self.categories_frame, text=f"{category['name']} (ID: {category['id']})", variable=var)
            cb.pack(anchor="w", padx=5, pady=2)
            self.category_vars[category['id']] = var
        
        # Атрибуты
        attributes_frame = ctk.CTkFrame(cat_frame)
        attributes_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(attributes_frame, text="Атрибуты товара", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Здесь можно добавить более сложную логику для атрибутов
        ctk.CTkLabel(attributes_frame, text="Функция атрибутов будет доступна в следующей версии", 
                    text_color="gray").pack(pady=20)
    
    def setup_images_tab(self):
        """Вкладка изображений"""
        img_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(img_frame, text="Изображения")
        
        ctk.CTkLabel(img_frame, text="Изображения товара", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Поле для URL изображений
        url_frame = ctk.CTkFrame(img_frame)
        url_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(url_frame, text="URL изображения:").pack(anchor="w", padx=5, pady=2)
        self.image_url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://example.com/image.jpg")
        self.image_url_entry.pack(fill="x", padx=5, pady=2)
        
        add_img_btn = ctk.CTkButton(url_frame, text="Добавить изображение", command=self.add_image)
        add_img_btn.pack(pady=5)
        
        # Список изображений
        self.images_listbox = tk.Listbox(img_frame, height=10)
        self.images_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Кнопки управления изображениями
        img_buttons_frame = ctk.CTkFrame(img_frame)
        img_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        remove_img_btn = ctk.CTkButton(img_buttons_frame, text="Удалить", command=self.remove_image)
        remove_img_btn.pack(side="left", padx=5)
    
    def setup_advanced_tab(self):
        """Дополнительные настройки"""
        adv_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(adv_frame, text="Дополнительно")
        
        ctk.CTkLabel(adv_frame, text="Мета-данные (JSON)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.meta_data_text = ctk.CTkTextbox(adv_frame, height=200)
        self.meta_data_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Пример метаданных
        example_meta = '''[
    {
        "key": "custom_field",
        "value": "custom_value"
    },
    {
        "key": "another_field",
        "value": "another_value"
    }
]'''
        self.meta_data_text.insert("1.0", example_meta)
    
    def setup_buttons(self):
        """Кнопки управления"""
        buttons_frame = ctk.CTkFrame(self.window)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Отмена", command=self.cancel)
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ctk.CTkButton(buttons_frame, text="Сохранить", command=self.save)
        save_btn.pack(side="right", padx=5)
    
    def on_manage_stock_change(self):
        """Обработка изменения флага управления остатками"""
        if self.manage_stock_var.get():
            self.stock_quantity_entry.configure(state="normal")
        else:
            self.stock_quantity_entry.configure(state="disabled")
    
    def add_image(self):
        """Добавление изображения"""
        url = self.image_url_entry.get().strip()
        if url:
            self.images_listbox.insert("end", url)
            self.image_url_entry.delete(0, "end")
    
    def remove_image(self):
        """Удаление изображения"""
        selection = self.images_listbox.curselection()
        if selection:
            self.images_listbox.delete(selection[0])
    
    def fill_fields(self):
        """Заполнение полей данными товара"""
        if not self.product:
            return
        
        # Основные поля
        self.name_entry.insert(0, self.product.name)
        self.sku_entry.insert(0, self.product.sku)
        self.type_var.set(self.product.type)
        self.status_var.set(self.product.status)
        self.regular_price_entry.insert(0, self.product.regular_price)
        self.sale_price_entry.insert(0, self.product.sale_price)
        
        # Остатки
        self.manage_stock_var.set(self.product.manage_stock)
        if self.product.stock_quantity is not None:
            self.stock_quantity_entry.insert(0, str(self.product.stock_quantity))
        self.stock_status_var.set(self.product.stock_status)
        self.on_manage_stock_change()
        
        # Описания
        self.short_desc_text.insert("1.0", self.product.short_description)
        self.description_text.insert("1.0", self.product.description)
        
        # Физические характеристики
        self.weight_entry.insert(0, self.product.weight)
        if self.product.dimensions:
            self.length_entry.insert(0, self.product.dimensions.get("length", ""))
            self.width_entry.insert(0, self.product.dimensions.get("width", ""))
            self.height_entry.insert(0, self.product.dimensions.get("height", ""))
        
        # Флаги
        self.featured_var.set(self.product.featured)
        self.virtual_var.set(self.product.virtual)
        self.downloadable_var.set(self.product.downloadable)
        
        # Категории
        for category in self.product.categories:
            if category.id in self.category_vars:
                self.category_vars[category.id].set(True)
        
        # Изображения
        for image in self.product.images:
            self.images_listbox.insert("end", image.src)
        
        # Мета-данные
        if self.product.meta_data:
            self.meta_data_text.delete("1.0", "end")
            self.meta_data_text.insert("1.0", json.dumps(self.product.meta_data, indent=2, ensure_ascii=False))
    
    def save(self):
        """Сохранение товара"""
        try:
            # Валидация
            if not self.name_entry.get().strip():
                messagebox.showerror("Ошибка", "Введите название товара")
                return
            
            # Создаем объект товара
            product = Product(
                name=self.name_entry.get().strip(),
                type=self.type_var.get(),
                sku=self.sku_entry.get().strip(),
                regular_price=self.regular_price_entry.get().strip(),
                sale_price=self.sale_price_entry.get().strip(),
                description=self.description_text.get("1.0", "end-1c").strip(),
                short_description=self.short_desc_text.get("1.0", "end-1c").strip(),
                status=self.status_var.get(),
                manage_stock=self.manage_stock_var.get(),
                stock_status=self.stock_status_var.get(),
                weight=self.weight_entry.get().strip(),
                featured=self.featured_var.get(),
                virtual=self.virtual_var.get(),
                downloadable=self.downloadable_var.get()
            )
            
            # Копируем ID если редактируем существующий товар
            if self.product:
                product.id = self.product.id
                product.date_created = self.product.date_created
                product.date_modified = self.product.date_modified
            
            # Количество на складе
            if self.manage_stock_var.get():
                try:
                    stock_qty = self.stock_quantity_entry.get().strip()
                    if stock_qty:
                        product.stock_quantity = int(stock_qty)
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверное значение количества на складе")
                    return
            
            # Размеры
            dimensions = {}
            if self.length_entry.get().strip():
                dimensions["length"] = self.length_entry.get().strip()
            if self.width_entry.get().strip():
                dimensions["width"] = self.width_entry.get().strip()
            if self.height_entry.get().strip():
                dimensions["height"] = self.height_entry.get().strip()
            product.dimensions = dimensions
            
            # Категории
            categories = []
            for cat_id, var in self.category_vars.items():
                if var.get():
                    category = next((cat for cat in self.categories if cat['id'] == cat_id), None)
                    if category:
                        categories.append(ProductCategory(id=cat_id, name=category['name']))
            product.categories = categories
            
            # Изображения
            images = []
            for i in range(self.images_listbox.size()):
                url = self.images_listbox.get(i)
                images.append(ProductImage(src=url))
            product.images = images
            
            # Мета-данные
            try:
                meta_text = self.meta_data_text.get("1.0", "end-1c").strip()
                if meta_text:
                    product.meta_data = json.loads(meta_text)
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Неверный формат JSON в мета-данных")
                return
            
            self.result = product
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить товар:\n{e}")
    
    def cancel(self):
        """Отмена"""
        self.window.destroy() 