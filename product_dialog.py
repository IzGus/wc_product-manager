"""
Диалоговое окно для создания и редактирования товаров
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any, Optional
import json
import threading

from product_models import Product, ProductCategory, ProductImage, ProductAttribute
from meta_fields_dialog import MetaFieldsDialog


class AttributeSelectionDialog:
    """Диалог выбора атрибута для добавления к товару"""
    
    def __init__(self, parent, attributes: List[Dict]):
        self.parent = parent
        self.attributes = attributes
        self.result = None
        
        # Создаем диалоговое окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Выбор атрибута")
        self.window.geometry("400x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        """Центрирование окна"""
        self.window.update_idletasks()
        
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        ctk.CTkLabel(main_frame, text="Выберите атрибут для добавления", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        
        # Список атрибутов
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.attributes_listbox = tk.Listbox(list_frame)
        self.attributes_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заполняем список
        for attr in self.attributes:
            self.attributes_listbox.insert("end", f"{attr['name']} (ID: {attr['id']})")
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Отмена", command=self.cancel)
        cancel_btn.pack(side="right", padx=5)
        
        select_btn = ctk.CTkButton(buttons_frame, text="Выбрать", command=self.select_attribute)
        select_btn.pack(side="right", padx=5)
    
    def select_attribute(self):
        """Выбор атрибута"""
        selection = self.attributes_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите атрибут из списка")
            return
        
        attr_index = selection[0]
        selected_attr = self.attributes[attr_index]
        self.result = (selected_attr['id'], selected_attr['name'])
        self.window.destroy()
    
    def cancel(self):
        """Отмена"""
        self.window.destroy()

class ProductDialog:
    """Диалоговое окно для работы с товарами"""
    
    def __init__(self, parent, product: Optional[Product] = None, categories: List[Dict] = None, attributes: List[Dict] = None, wc_manager=None):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
            product: Товар для редактирования (None для создания нового)
            categories: Список доступных категорий
            attributes: Список доступных атрибутов
            wc_manager: Менеджер WooCommerce для загрузки терминов атрибутов
        """
        self.parent = parent
        self.product = product
        self.categories = categories or []
        self.attributes = attributes or []
        self.wc_manager = wc_manager
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
        
        # Управление атрибутами
        attr_control_frame = ctk.CTkFrame(attributes_frame)
        attr_control_frame.pack(fill="x", padx=5, pady=5)
        
        self.add_attribute_btn = ctk.CTkButton(attr_control_frame, text="➕ Добавить атрибут", 
                                             command=self.add_product_attribute, width=120)
        self.add_attribute_btn.pack(side="left", padx=5)
        
        self.remove_attribute_btn = ctk.CTkButton(attr_control_frame, text="➖ Удалить", 
                                                command=self.remove_product_attribute, width=80, state="disabled")
        self.remove_attribute_btn.pack(side="left", padx=5)
        
        # Список атрибутов товара
        self.product_attributes_frame = ctk.CTkScrollableFrame(attributes_frame, height=200)
        self.product_attributes_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Словарь для хранения виджетов атрибутов
        self.attribute_widgets = {}
    
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
        
        # Заголовок и кнопка для мета-данных
        meta_header_frame = ctk.CTkFrame(adv_frame)
        meta_header_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(meta_header_frame, text="Мета-данные", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", pady=5)
        
        # Кнопка для визуального редактора
        meta_edit_btn = ctk.CTkButton(meta_header_frame, text="Визуальный редактор", 
                                     command=self.open_meta_fields_dialog, width=150)
        meta_edit_btn.pack(side="right", padx=5, pady=5)
        
        # Текстовое поле для JSON (для продвинутых пользователей)
        ctk.CTkLabel(adv_frame, text="JSON формат (для продвинутых пользователей):", 
                    font=ctk.CTkFont(size=12)).pack(pady=(10, 0))
        
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
        
        # Атрибуты
        self.load_product_attributes()
    
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
            
            # Атрибуты
            product.attributes = self.get_product_attributes()
            
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
    
    def open_meta_fields_dialog(self):
        """Открытие визуального диалога для редактирования мета-полей"""
        try:
            # Получаем текущие мета-данные из JSON поля
            meta_text = self.meta_data_text.get("1.0", "end-1c").strip()
            current_meta_data = []
            
            if meta_text:
                try:
                    current_meta_data = json.loads(meta_text)
                    if not isinstance(current_meta_data, list):
                        current_meta_data = []
                except json.JSONDecodeError:
                    messagebox.showwarning("Предупреждение", 
                                         "Некорректный JSON в поле мета-данных. Будет создан новый список.")
                    current_meta_data = []
            
            # Открываем диалог мета-полей
            dialog = MetaFieldsDialog(self.window, current_meta_data)
            self.window.wait_window(dialog.dialog)
            
            # Если пользователь сохранил изменения, обновляем JSON поле
            if dialog.result is not None:
                updated_json = json.dumps(dialog.result, indent=2, ensure_ascii=False)
                self.meta_data_text.delete("1.0", "end")
                self.meta_data_text.insert("1.0", updated_json)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть диалог мета-полей:\n{e}")
    
    def add_product_attribute(self):
        """Добавление атрибута к товару"""
        if not self.attributes:
            messagebox.showwarning("Предупреждение", "Сначала нужно загрузить атрибуты с сервера")
            return
        
        # Создаем диалог выбора атрибута
        dialog = AttributeSelectionDialog(self.window, self.attributes)
        self.window.wait_window(dialog.window)
        
        if dialog.result:
            attr_id, attr_name = dialog.result
            
            # Проверяем, не добавлен ли уже этот атрибут
            if attr_id in self.attribute_widgets:
                messagebox.showwarning("Предупреждение", f"Атрибут '{attr_name}' уже добавлен к товару")
                return
            
            # Добавляем виджет атрибута
            self.create_attribute_widget(attr_id, attr_name)
    
    def remove_product_attribute(self):
        """Удаление выбранного атрибута"""
        # Найдем выбранный атрибут (можно улучшить логику выбора)
        if not self.attribute_widgets:
            return
        
        # Простая реализация - удаляем последний добавленный атрибут
        # В более сложной версии можно добавить выбор
        last_attr_id = list(self.attribute_widgets.keys())[-1]
        self.remove_attribute_widget(last_attr_id)
    
    def create_attribute_widget(self, attr_id: int, attr_name: str):
        """Создание виджета для атрибута товара"""
        # Основной контейнер атрибута
        attr_frame = ctk.CTkFrame(self.product_attributes_frame)
        attr_frame.pack(fill="x", padx=5, pady=5)
        
        # Заголовок атрибута
        header_frame = ctk.CTkFrame(attr_frame)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(header_frame, text=f"Атрибут: {attr_name}", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        # Кнопка удаления конкретного атрибута
        remove_btn = ctk.CTkButton(header_frame, text="✖", width=30, height=25,
                                 command=lambda: self.remove_attribute_widget(attr_id))
        remove_btn.pack(side="right", padx=5)
        
        # Настройки атрибута
        settings_frame = ctk.CTkFrame(attr_frame)
        settings_frame.pack(fill="x", padx=5, pady=5)
        
        # Видимость атрибута
        visible_var = ctk.BooleanVar(value=True)
        visible_cb = ctk.CTkCheckBox(settings_frame, text="Видимый на странице товара", variable=visible_var)
        visible_cb.pack(anchor="w", padx=5, pady=2)
        
        # Используется для вариаций
        variation_var = ctk.BooleanVar(value=False)
        variation_cb = ctk.CTkCheckBox(settings_frame, text="Используется для вариаций", variable=variation_var)
        variation_cb.pack(anchor="w", padx=5, pady=2)
        
        # Значения атрибута
        values_frame = ctk.CTkFrame(attr_frame)
        values_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(values_frame, text="Значения атрибута:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5)
        
        # Контейнер для существующих значений
        existing_values_frame = ctk.CTkFrame(values_frame)
        existing_values_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(existing_values_frame, text="Выберите из существующих:").pack(anchor="w", padx=5)
        
        # Скроллируемый фрейм для чекбоксов значений
        values_scroll_frame = ctk.CTkScrollableFrame(existing_values_frame, height=100)
        values_scroll_frame.pack(fill="x", padx=5, pady=2)
        
        # Словарь для хранения переменных чекбоксов
        value_vars = {}
        
        # Добавление нового значения
        new_value_frame = ctk.CTkFrame(values_frame)
        new_value_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(new_value_frame, text="Добавить новое значение:").pack(anchor="w", padx=5)
        
        new_value_container = ctk.CTkFrame(new_value_frame)
        new_value_container.pack(fill="x", padx=5, pady=2)
        
        new_value_entry = ctk.CTkEntry(new_value_container, placeholder_text="Введите новое значение")
        new_value_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        add_value_btn = ctk.CTkButton(new_value_container, text="➕ Добавить", width=80,
                                    command=lambda: self.add_new_attribute_value(attr_id, new_value_entry, values_scroll_frame, value_vars))
        add_value_btn.pack(side="right")
        
        # Сохраняем ссылки на виджеты
        self.attribute_widgets[attr_id] = {
            'frame': attr_frame,
            'name': attr_name,
            'visible_var': visible_var,
            'variation_var': variation_var,
            'values_scroll_frame': values_scroll_frame,
            'value_vars': value_vars,
            'new_value_entry': new_value_entry
        }
        
        # Загружаем существующие значения атрибута
        self.load_attribute_terms(attr_id)
        
        # Активируем кнопку удаления
        self.remove_attribute_btn.configure(state="normal")
    
    def load_attribute_terms(self, attr_id: int):
        """Загрузка существующих значений атрибута"""
        if attr_id not in self.attribute_widgets:
            return
        
        # Показываем индикатор загрузки
        widgets = self.attribute_widgets[attr_id]
        values_frame = widgets['values_scroll_frame']
        
        # Очищаем фрейм и показываем индикатор загрузки
        for widget in values_frame.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(values_frame, text="⏳ Загрузка значений...", text_color="blue")
        loading_label.pack(anchor="w", padx=5, pady=5)
        
        def load_terms_thread():
            try:
                # Используем переданный WooCommerce менеджер
                if self.wc_manager:
                    terms = self.wc_manager.get_attribute_terms(attr_id)
                else:
                    # Если нет доступа к wc_manager, используем пустой список
                    terms = []
                
                # Обновляем интерфейс в главном потоке
                self.window.after(0, lambda: self.update_attribute_terms_ui(attr_id, terms))
                
            except Exception as e:
                print(f"Ошибка загрузки терминов атрибута {attr_id}: {e}")
                # В случае ошибки показываем пустой список
                self.window.after(0, lambda: self.update_attribute_terms_ui(attr_id, []))
        
        threading.Thread(target=load_terms_thread, daemon=True).start()
    
    def update_attribute_terms_ui(self, attr_id: int, terms: List[Dict]):
        """Обновление интерфейса с терминами атрибута"""
        if attr_id not in self.attribute_widgets:
            return
        
        widgets = self.attribute_widgets[attr_id]
        values_frame = widgets['values_scroll_frame']
        value_vars = widgets['value_vars']
        
        # Очищаем существующие чекбоксы
        for widget in values_frame.winfo_children():
            widget.destroy()
        value_vars.clear()
        
        # Добавляем чекбоксы для каждого термина
        for term in terms:
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(values_frame, text=term['name'], variable=var)
            checkbox.pack(anchor="w", padx=5, pady=2)
            value_vars[term['name']] = var
        
        # Если нет терминов, показываем сообщение
        if not terms:
            ctk.CTkLabel(values_frame, text="Нет доступных значений", 
                        text_color="gray").pack(anchor="w", padx=5, pady=5)
    
    def add_new_attribute_value(self, attr_id: int, entry_widget, values_frame, value_vars):
        """Добавление нового значения атрибута"""
        new_value = entry_widget.get().strip()
        if not new_value:
            messagebox.showwarning("Предупреждение", "Введите название нового значения")
            return
        
        # Проверяем, не существует ли уже такое значение
        if new_value in value_vars:
            messagebox.showwarning("Предупреждение", f"Значение '{new_value}' уже существует")
            return
        
        # Удаляем сообщение "Нет доступных значений" если оно есть
        for widget in values_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and "Нет доступных" in widget.cget("text"):
                widget.destroy()
        
        # Добавляем новый чекбокс
        var = ctk.BooleanVar(value=True)  # Автоматически выбираем новое значение
        checkbox = ctk.CTkCheckBox(values_frame, text=new_value, variable=var)
        checkbox.pack(anchor="w", padx=5, pady=2)
        value_vars[new_value] = var
        
        # Очищаем поле ввода
        entry_widget.delete(0, "end")
        
        messagebox.showinfo("Успех", f"Значение '{new_value}' добавлено")
    
    def remove_attribute_widget(self, attr_id: int):
        """Удаление виджета атрибута"""
        if attr_id in self.attribute_widgets:
            # Удаляем виджет
            self.attribute_widgets[attr_id]['frame'].destroy()
            del self.attribute_widgets[attr_id]
            
            # Если атрибутов не осталось, деактивируем кнопку удаления
            if not self.attribute_widgets:
                self.remove_attribute_btn.configure(state="disabled")
    
    def get_product_attributes(self) -> List[ProductAttribute]:
        """Получение списка атрибутов товара из интерфейса"""
        attributes = []
        
        for attr_id, widgets in self.attribute_widgets.items():
            # Получаем выбранные значения из чекбоксов
            selected_values = []
            value_vars = widgets['value_vars']
            
            for value_name, var in value_vars.items():
                if var.get():  # Если чекбокс выбран
                    selected_values.append(value_name)
            
            if selected_values:  # Добавляем только если есть выбранные значения
                attr = ProductAttribute(
                    id=attr_id,
                    name=widgets['name'],
                    options=selected_values,
                    visible=widgets['visible_var'].get(),
                    variation=widgets['variation_var'].get()
                )
                attributes.append(attr)
        
        return attributes
    
    def load_product_attributes(self):
        """Загрузка атрибутов товара в интерфейс (при редактировании)"""
        if not self.product or not self.product.attributes:
            return
        
        for attr in self.product.attributes:
            # Создаем виджет для атрибута
            self.create_attribute_widget(attr.id, attr.name)
            
            # Заполняем значения после загрузки терминов
            def set_attribute_values(attr_obj=attr):
                if attr_obj.id in self.attribute_widgets:
                    widgets = self.attribute_widgets[attr_obj.id]
                    widgets['visible_var'].set(attr_obj.visible)
                    widgets['variation_var'].set(attr_obj.variation)
                    
                    # Устанавливаем выбранные значения в чекбоксах
                    self.set_selected_attribute_values(attr_obj.id, attr_obj.options)
            
            # Устанавливаем значения с небольшой задержкой, чтобы термины успели загрузиться
            self.window.after(1000, set_attribute_values)
    
    def set_selected_attribute_values(self, attr_id: int, selected_options: List[str]):
        """Установка выбранных значений атрибута"""
        if attr_id not in self.attribute_widgets:
            return
        
        widgets = self.attribute_widgets[attr_id]
        value_vars = widgets['value_vars']
        values_frame = widgets['values_scroll_frame']
        
        # Сначала устанавливаем существующие значения
        for option in selected_options:
            if option in value_vars:
                value_vars[option].set(True)
            else:
                # Если значение не найдено в существующих, добавляем его как новое
                var = ctk.BooleanVar(value=True)
                checkbox = ctk.CTkCheckBox(values_frame, text=option, variable=var)
                checkbox.pack(anchor="w", padx=5, pady=2)
                value_vars[option] = var
                
                # Удаляем сообщение "Нет доступных значений" если оно есть
                for widget in values_frame.winfo_children():
                    if isinstance(widget, ctk.CTkLabel) and "Нет доступных" in widget.cget("text"):
                        widget.destroy()
    
    def cancel(self):
        """Отмена"""
        self.window.destroy() 