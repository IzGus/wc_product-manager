"""
Главное окно приложения WooCommerce Product Manager
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading
import logging
from typing import List, Dict, Any, Optional
import json

from woocommerce_manager import WooCommerceManager
from product_models import Product
from csv_manager import CSVManager
from config import config_manager, ConnectionProfile
from connection_settings_dialog import ConnectionSettingsDialog

# Настройка темы
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

logger = logging.getLogger(__name__)

class ProductManagerGUI:
    """Главное окно приложения"""
    
    def __init__(self):
        """Инициализация GUI"""
        self.root = ctk.CTk()
        self.root.title("WooCommerce Product Manager")
        self.root.geometry("1400x800")
        
        # Менеджеры
        self.wc_manager: Optional[WooCommerceManager] = None
        self.csv_manager = CSVManager()
        
        # Данные
        self.products: List[Product] = []
        self.categories: List[Dict] = []
        self.attributes: List[Dict] = []
        
        # Переменные состояния
        self.is_loading = False
        
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главное меню
        self.setup_menu()
        
        # Панель настроек API
        self.setup_api_frame()
        
        # Панель управления
        self.setup_control_frame()
        
        # Основная рабочая область
        self.setup_main_area()
        
        # Статус бар
        self.setup_status_bar()
    
    def setup_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Импорт
        import_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Импорт", menu=import_menu)
        import_menu.add_command(label="Авто-определение формата", command=self.import_csv)
        import_menu.add_command(label="Простой CSV", command=lambda: self.import_csv('simple'))
        import_menu.add_command(label="WooCommerce CSV", command=lambda: self.import_csv('woocommerce'))
        
        # Экспорт
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Экспорт", menu=export_menu)
        export_menu.add_command(label="Простой CSV", command=lambda: self.export_csv('simple'))
        export_menu.add_command(label="WooCommerce CSV", command=lambda: self.export_csv('woocommerce'))
        
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Настройки
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="🔗 Подключения WooCommerce", command=self.open_connection_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="📤 Экспорт профилей", command=self.export_profiles_menu)
        settings_menu.add_command(label="📥 Импорт профилей", command=self.import_profiles_menu)
        
        # Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="📋 Инструкция по настройке", command=self.show_setup_instructions)
        help_menu.add_command(label="🆕 Новые функции v3.0", command=self.show_new_features)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def setup_api_frame(self):
        """Панель настроек API с поддержкой профилей"""
        api_frame = ctk.CTkFrame(self.root)
        api_frame.pack(fill="x", padx=10, pady=5)
        
        # Заголовок
        title_label = ctk.CTkLabel(api_frame, text="🔗 Подключение к WooCommerce", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=5)
        
        # Основной контейнер
        main_container = ctk.CTkFrame(api_frame)
        main_container.pack(fill="x", padx=10, pady=5)
        
        # Информация о текущем подключении
        info_frame = ctk.CTkFrame(main_container)
        info_frame.pack(fill="x", pady=5)
        
        # Текущий профиль
        current_profile_frame = ctk.CTkFrame(info_frame)
        current_profile_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(current_profile_frame, text="Текущий профиль:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.current_profile_label = ctk.CTkLabel(current_profile_frame, text="Не выбран", text_color="gray")
        self.current_profile_label.pack(side="left", padx=10)
        
        # URL сайта
        url_frame = ctk.CTkFrame(info_frame)
        url_frame.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(url_frame, text="URL сайта:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.site_url_label = ctk.CTkLabel(url_frame, text="Не настроен", text_color="gray")
        self.site_url_label.pack(side="left", padx=10)
        
        # Кнопки управления
        buttons_frame = ctk.CTkFrame(main_container)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Основные кнопки
        self.settings_btn = ctk.CTkButton(buttons_frame, text="⚙️ Настройки подключения", 
                                         command=self.open_connection_settings, width=200)
        self.settings_btn.pack(side="left", padx=5)
        
        self.test_btn = ctk.CTkButton(buttons_frame, text="🔍 Тест соединения", 
                                     command=self.test_connection, state="disabled", width=150)
        self.test_btn.pack(side="left", padx=5)
        
        # Быстрое переключение профилей
        profiles_frame = ctk.CTkFrame(buttons_frame)
        profiles_frame.pack(side="right", padx=5)
        
        ctk.CTkLabel(profiles_frame, text="Быстрое переключение:").pack(side="left", padx=5)
        self.profile_menu = ctk.CTkOptionMenu(profiles_frame, values=["Нет профилей"], 
                                             command=self.switch_profile, width=150)
        self.profile_menu.pack(side="left", padx=5)
        self.profile_menu.set("Выберите профиль...")
        
        # Статус подключения
        status_frame = ctk.CTkFrame(main_container)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.connection_status = ctk.CTkLabel(status_frame, text="❌ Не подключено", text_color="red")
        self.connection_status.pack(side="left", padx=10, pady=5)
        
        # Загружаем текущие настройки
        self.update_connection_info()
    
    def setup_control_frame(self):
        """Панель управления товарами"""
        control_frame = ctk.CTkFrame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Заголовок
        title_label = ctk.CTkLabel(control_frame, text="Управление товарами", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=5)
        
        # Кнопки управления
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.load_btn = ctk.CTkButton(button_frame, text="Загрузить товары", command=self.load_products, state="disabled")
        self.load_btn.pack(side="left", padx=5)
        
        self.add_btn = ctk.CTkButton(button_frame, text="Добавить товар", command=self.add_product, state="disabled")
        self.add_btn.pack(side="left", padx=5)
        
        self.edit_btn = ctk.CTkButton(button_frame, text="Редактировать", command=self.edit_product, state="disabled")
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(button_frame, text="Удалить", command=self.delete_product, state="disabled")
        self.delete_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(button_frame, text="Сохранить изменения", command=self.save_changes, state="disabled")
        self.save_btn.pack(side="left", padx=5)
        
        # Поиск и фильтры
        filter_frame = ctk.CTkFrame(button_frame)
        filter_frame.pack(side="right", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Поиск:").pack(side="left", padx=2)
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Название или SKU")
        self.search_entry.pack(side="left", padx=2)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        self.filter_btn = ctk.CTkButton(filter_frame, text="Очистить", command=self.clear_search, width=70)
        self.filter_btn.pack(side="left", padx=2)
    
    def setup_main_area(self):
        """Основная рабочая область с таблицей товаров"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Заголовок
        title_label = ctk.CTkLabel(main_frame, text="Список товаров", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=5)
        
        # Создаем фрейм для таблицы
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаем Treeview для отображения товаров
        columns = ("ID", "Название", "SKU", "Тип", "Цена", "Статус", "Остаток", "Категории")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        for col in columns:
            self.products_tree.heading(col, text=col)
            if col == "ID":
                self.products_tree.column(col, width=60, minwidth=50)
            elif col == "Название":
                self.products_tree.column(col, width=250, minwidth=200)
            elif col == "SKU":
                self.products_tree.column(col, width=120, minwidth=100)
            elif col == "Тип":
                self.products_tree.column(col, width=80, minwidth=70)
            elif col == "Цена":
                self.products_tree.column(col, width=100, minwidth=80)
            elif col == "Статус":
                self.products_tree.column(col, width=100, minwidth=80)
            elif col == "Остаток":
                self.products_tree.column(col, width=80, minwidth=70)
            else:
                self.products_tree.column(col, width=150, minwidth=100)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение таблицы и скроллбаров
        self.products_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Привязка событий
        self.products_tree.bind("<Double-1>", lambda e: self.edit_product())
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)
    
    def setup_status_bar(self):
        """Статус бар"""
        status_frame = ctk.CTkFrame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Готов к работе")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Прогресс бар
        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.set(0)
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Настройка стиля для Treeview
        style.configure("Treeview", background="#FFFFFF", foreground="#000000", fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", background="#E0E0E0", foreground="#000000")
        
        # Настройка цветов для статусов изменений
        style.map("Treeview",
                  background=[('selected', '#347083')])
    
    def setup_table_colors(self):
        """Настройка цветовой индикации для статусов товаров"""
        # Настраиваем теги для разных статусов
        self.products_tree.tag_configure("status_new", background="#E8F5E8", foreground="#2E7D32")      # Зеленый для новых
        self.products_tree.tag_configure("status_modified", background="#FFF3E0", foreground="#F57C00") # Оранжевый для измененных
        self.products_tree.tag_configure("status_deleted", background="#FFEBEE", foreground="#C62828")  # Красный для удаленных
        self.products_tree.tag_configure("status_unchanged", background="#FFFFFF", foreground="#000000") # Обычный для неизмененных
    
    def connect_api(self):
        """Подключение к API"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL сайта")
            return
        
        try:
            self.wc_manager = WooCommerceManager(url)
            self.connection_status.configure(text="Подключено", text_color="green")
            self.test_btn.configure(state="normal")
            self.load_btn.configure(state="normal")
            self.add_btn.configure(state="normal")
            
            self.update_status("Подключение к API успешно установлено")
            
        except Exception as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к API:\n{e}")
            logger.error(f"Ошибка подключения к API: {e}")
    
    def test_connection(self):
        """Тестирование соединения с API"""
        if not self.wc_manager:
            return
        
        def test_thread():
            self.update_status("Тестирование соединения...")
            self.progress_bar.start()
            
            try:
                if self.wc_manager.test_connection():
                    self.root.after(0, lambda: messagebox.showinfo("Успех", "Соединение с API работает!"))
                    self.root.after(0, lambda: self.update_status("Соединение протестировано успешно"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось подключиться к API"))
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def load_products(self):
        """Загрузка товаров с сайта"""
        if not self.wc_manager:
            return
        
        def load_thread():
            self.root.after(0, lambda: self.update_status("Загрузка товаров..."))
            self.root.after(0, lambda: self.progress_bar.start())
            self.is_loading = True
            
            try:
                products_data = self.wc_manager.get_all_products()
                self.products = [Product.from_woocommerce_dict(data) for data in products_data]
                
                # Также загружаем категории и атрибуты
                self.categories = self.wc_manager.get_categories()
                self.attributes = self.wc_manager.get_attributes()
                
                self.root.after(0, self.update_products_table)
                self.root.after(0, lambda: self.update_status(f"Загружено {len(self.products)} товаров"))
                
                # Активируем кнопки управления
                self.root.after(0, lambda: self.edit_btn.configure(state="normal"))
                self.root.after(0, lambda: self.delete_btn.configure(state="normal"))
                self.root.after(0, lambda: self.save_btn.configure(state="normal"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось загрузить товары:\n{e}"))
                logger.error(f"Ошибка загрузки товаров: {e}")
            finally:
                self.is_loading = False
                self.root.after(0, lambda: self.progress_bar.stop())
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_products_table(self):
        """Обновление таблицы товаров"""
        # Очищаем таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Заполняем таблицу
        for product in self.products:
            # Пропускаем удаленные товары (но показываем помеченные к удалению)
            if product._is_deleted and not product.id:
                continue
                
            display_info = product.get_display_info()
            values = [display_info.get(col, "") for col in self.products_tree["columns"]]
            
            # Определяем тег для цветовой индикации
            change_status = product.get_change_status()
            tag_name = f"status_{change_status}"
            
            # Добавляем статус к ID для визуального отображения
            if change_status != "unchanged":
                status_indicators = {
                    "new": "[НОВЫЙ]",
                    "modified": "[ИЗМЕНЕН]", 
                    "deleted": "[УДАЛЕН]"
                }
                values[0] = f"{values[0]} {status_indicators.get(change_status, '')}"
            
            self.products_tree.insert("", "end", values=values, tags=(product.id, tag_name))
        
        # Настраиваем цветовую индикацию
        self.setup_table_colors()
    
    def on_product_select(self, event):
        """Обработка выбора товара"""
        selection = self.products_tree.selection()
        if selection:
            # Товар выбран, можно редактировать/удалять
            pass
    
    def on_search(self, event):
        """Поиск товаров"""
        search_term = self.search_entry.get().lower()
        
        # Очищаем таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Фильтруем и показываем подходящие товары
        for product in self.products:
            if (search_term in product.name.lower() or 
                search_term in product.sku.lower()):
                display_info = product.get_display_info()
                values = [display_info.get(col, "") for col in self.products_tree["columns"]]
                self.products_tree.insert("", "end", values=values, tags=(product.id,))
    
    def clear_search(self):
        """Очистка поиска"""
        self.search_entry.delete(0, "end")
        self.update_products_table()
    
    def add_product(self):
        """Добавление нового товара"""
        from product_dialog import ProductDialog
        
        dialog = ProductDialog(self.root, categories=self.categories, attributes=self.attributes)
        if dialog.result:
            # Помечаем товар как новый
            dialog.result.mark_as_new()
            self.products.append(dialog.result)
            self.update_products_table()
            self.update_status("Товар добавлен локально. Нажмите 'Сохранить изменения' для отправки на сайт.")
    
    def edit_product(self):
        """Редактирование товара"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для редактирования")
            return
        
        # Получаем ID товара из тегов
        item = self.products_tree.item(selection[0])
        product_id = item['tags'][0] if item['tags'] else None
        
        if product_id:
            # Находим товар в списке
            product = next((p for p in self.products if p.id == product_id), None)
            if product:
                from product_dialog import ProductDialog
                
                dialog = ProductDialog(self.root, product=product, categories=self.categories, attributes=self.attributes)
                if dialog.result:
                    # Помечаем товар как измененный
                    dialog.result.mark_as_modified()
                    # Обновляем товар в списке
                    index = self.products.index(product)
                    self.products[index] = dialog.result
                    self.update_products_table()
                    self.update_status("Товар изменен локально. Нажмите 'Сохранить изменения' для отправки на сайт.")
    
    def delete_product(self):
        """Удаление товара"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранный товар?"):
            return
        
        # Получаем ID товара
        item = self.products_tree.item(selection[0])
        product_id = item['tags'][0] if item['tags'] else None
        
        if product_id:
            # Находим товар и помечаем как удаленный
            product = next((p for p in self.products if p.id == product_id), None)
            if product:
                product.mark_as_deleted()
            self.update_products_table()
            self.update_status("Товар помечен для удаления. Нажмите 'Сохранить изменения' для применения.")
    
    def save_changes(self):
        """Сохранение изменений на сайт"""
        if not self.wc_manager:
            messagebox.showerror("Ошибка", "API не подключен")
            return
        
        # Собираем товары для различных операций
        products_to_create = []
        products_to_update = []
        products_to_delete = []
        
        for product in self.products:
            if product.is_changed():
                status = product.get_change_status()
                if status == "new":
                    products_to_create.append(product)
                elif status == "modified":
                    products_to_update.append(product)
                elif status == "deleted":
                    products_to_delete.append(product)
        
        total_operations = len(products_to_create) + len(products_to_update) + len(products_to_delete)
        
        if total_operations == 0:
            messagebox.showinfo("Информация", "Нет изменений для сохранения")
            return
        
        # Подтверждение операции
        confirm_message = f"""
Будут выполнены следующие операции:
• Создать: {len(products_to_create)} товаров
• Обновить: {len(products_to_update)} товаров  
• Удалить: {len(products_to_delete)} товаров

Продолжить?"""
        
        if not messagebox.askyesno("Подтверждение", confirm_message):
            return
        
        def save_thread():
            try:
                self.root.after(0, lambda: self.update_status("Сохранение изменений..."))
                self.root.after(0, lambda: self.progress_bar.start())
                
                # Результаты операций
                results = {
                    "created": [],
                    "updated": [],
                    "deleted": [],
                    "errors": []
                }
                
                # Создание новых товаров
                if products_to_create:
                    self.root.after(0, lambda: self.update_status(f"Создание {len(products_to_create)} товаров..."))
                    
                    # Пакетное создание если много товаров
                    if len(products_to_create) > 5:
                        create_data = [product.to_woocommerce_dict() for product in products_to_create]
                        batch_result = self.wc_manager.batch_create_products(create_data)
                        
                        for i, created_product in enumerate(batch_result["success"]):
                            products_to_create[i].id = created_product["id"]
                            products_to_create[i].reset_change_flags()
                            results["created"].append(created_product)
                        
                        results["errors"].extend(batch_result["errors"])
                    else:
                        # Поштучное создание для малого количества
                        for product in products_to_create:
                            created_product = self.wc_manager.create_product(product.to_woocommerce_dict())
                            if created_product:
                                product.id = created_product["id"]
                                product.reset_change_flags()
                                results["created"].append(created_product)
                            else:
                                results["errors"].append({"product": product.name, "error": "Не удалось создать"})
                
                # Обновление существующих товаров
                if products_to_update:
                    self.root.after(0, lambda: self.update_status(f"Обновление {len(products_to_update)} товаров..."))
                    
                    # Пакетное обновление если много товаров
                    if len(products_to_update) > 5:
                        update_data = []
                        for product in products_to_update:
                            product_dict = product.to_woocommerce_dict()
                            product_dict["id"] = product.id
                            update_data.append(product_dict)
                        
                        batch_result = self.wc_manager.batch_update_products(update_data)
                        
                        for i, updated_product in enumerate(batch_result["success"]):
                            products_to_update[i].reset_change_flags()
                            results["updated"].append(updated_product)
                        
                        results["errors"].extend(batch_result["errors"])
                    else:
                        # Поштучное обновление
                        for product in products_to_update:
                            updated_product = self.wc_manager.update_product(product.id, product.to_woocommerce_dict())
                            if updated_product:
                                product.reset_change_flags()
                                results["updated"].append(updated_product)
                            else:
                                results["errors"].append({"product": product.name, "error": "Не удалось обновить"})
                
                # Удаление товаров
                if products_to_delete:
                    self.root.after(0, lambda: self.update_status(f"Удаление {len(products_to_delete)} товаров..."))
                    
                    # Пакетное удаление если много товаров
                    if len(products_to_delete) > 5:
                        delete_ids = [product.id for product in products_to_delete if product.id]
                        batch_result = self.wc_manager.batch_delete_products(delete_ids)
                        
                        results["deleted"].extend(batch_result["success"])
                        results["errors"].extend(batch_result["errors"])
                        
                        # Удаляем товары из локального списка
                        self.products = [p for p in self.products if not p._is_deleted]
                    else:
                        # Поштучное удаление
                        for product in products_to_delete:
                            if product.id and self.wc_manager.delete_product(product.id):
                                results["deleted"].append({"id": product.id, "name": product.name})
                            else:
                                results["errors"].append({"product": product.name, "error": "Не удалось удалить"})
                        
                        # Удаляем товары из локального списка
                        self.products = [p for p in self.products if not p._is_deleted]
                
                # Обновляем таблицу
                self.root.after(0, self.update_products_table)
                
                # Формируем отчет
                success_count = len(results["created"]) + len(results["updated"]) + len(results["deleted"])
                error_count = len(results["errors"])
                
                if error_count == 0:
                    message = f"Синхронизация завершена успешно!\n\nВыполнено операций: {success_count}"
                    self.root.after(0, lambda: messagebox.showinfo("Успех", message))
                else:
                    message = f"Синхронизация завершена с ошибками.\n\nУспешно: {success_count}\nОшибок: {error_count}"
                    self.root.after(0, lambda: messagebox.showwarning("Частичный успех", message))
                
                self.root.after(0, lambda: self.update_status("Синхронизация завершена"))
                
            except Exception as e:
                error_message = f"Критическая ошибка при синхронизации: {e}"
                self.root.after(0, lambda: messagebox.showerror("Ошибка", error_message))
                logger.error(error_message)
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
        
        threading.Thread(target=save_thread, daemon=True).start()
    
    def import_csv(self, csv_format='auto'):
        """Импорт товаров из CSV"""
        filename = filedialog.askopenfilename(
            title="Выберите CSV файл для импорта",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            def import_thread():
                self.root.after(0, lambda: self.update_status("Импорт из CSV..."))
                self.root.after(0, lambda: self.progress_bar.start())
                
                try:
                    # Определяем формат если нужно
                    if csv_format == 'auto':
                        detected_format = self.csv_manager.detect_csv_format(filename)
                        format_message = f"Обнаружен формат: {detected_format}"
                        self.root.after(0, lambda: self.update_status(format_message))
                    
                    # Импортируем в зависимости от формата
                    if csv_format == 'simple':
                        imported_products = self.csv_manager.import_simple_csv(filename)
                    elif csv_format == 'woocommerce':
                        imported_products = self.csv_manager.import_woocommerce_csv(filename)
                    else:
                        imported_products = self.csv_manager.import_products_from_csv(filename)
                    
                    self.products.extend(imported_products)
                    
                    self.root.after(0, self.update_products_table)
                    self.root.after(0, lambda: self.update_status(f"Импортировано {len(imported_products)} товаров"))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка импорта", f"Не удалось импортировать CSV:\n{e}"))
                finally:
                    self.root.after(0, lambda: self.progress_bar.stop())
            
            threading.Thread(target=import_thread, daemon=True).start()
    
    def export_csv(self, csv_format='simple'):
        """Экспорт товаров в CSV"""
        if not self.products:
            messagebox.showwarning("Предупреждение", "Нет товаров для экспорта")
            return
        
        format_suffix = "_woocommerce" if csv_format == 'woocommerce' else "_simple"
        filename = filedialog.asksaveasfilename(
            title=f"Сохранить как {csv_format.upper()} CSV",
            defaultextension=f"{format_suffix}.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            def export_thread():
                self.root.after(0, lambda: self.update_status("Экспорт в CSV..."))
                self.root.after(0, lambda: self.progress_bar.start())
                
                try:
                    if csv_format == 'woocommerce':
                        # Экспорт в формате WooCommerce
                        try:
                            from woocommerce_csv_manager import WooCommerceCSVManager
                            wc_manager = WooCommerceCSVManager()
                            success = wc_manager.export_to_woocommerce_csv(self.products, filename)
                        except ImportError:
                            self.root.after(0, lambda: messagebox.showerror("Ошибка", "WooCommerce CSV менеджер не найден"))
                            success = False
                    else:
                        # Простой экспорт
                        success = self.csv_manager.export_products_to_csv(self.products, filename)
                    
                    if success:
                        format_name = "WooCommerce" if csv_format == 'woocommerce' else "простой"
                        self.root.after(0, lambda: messagebox.showinfo("Успех", f"Экспорт в {format_name} CSV завершен успешно"))
                        self.root.after(0, lambda: self.update_status(f"Экспорт в {format_name} CSV завершен"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось экспортировать данные"))
                
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка экспорта", f"Не удалось экспортировать CSV:\n{e}"))
                finally:
                    self.root.after(0, lambda: self.progress_bar.stop())
            
            threading.Thread(target=export_thread, daemon=True).start()
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
🛒 WooCommerce Product Manager v3.0

Универсальное приложение для управления товарами 
любых WordPress + WooCommerce сайтов через REST API

🆕 Новое в v3.0:
• Поддержка любых WooCommerce сайтов
• Система профилей подключения
• Быстрое переключение между сайтами
• Расширенные настройки API
• Экспорт/импорт профилей

Ранее реализованные возможности:
• Полная синхронизация с WooCommerce API
• Цветовая индикация изменений
• Визуальный редактор мета-полей
• Пакетные операции
• Поддержка вариативных товаров
• Импорт/экспорт WooCommerce CSV

Разработано с использованием Python и CustomTkinter
        """
        messagebox.showinfo("О программе", about_text)
    
    def show_setup_instructions(self):
        """Показать инструкцию по настройке"""
        instructions_text = """
📋 Инструкция по настройке WooCommerce API

1. Войдите в админку WordPress
2. Перейдите в WooCommerce → Настройки → Дополнительно → REST API
3. Нажмите кнопку "Добавить ключ"
4. Заполните поля:
   • Описание: "Product Manager"
   • Пользователь: выберите администратора
   • Права доступа: "Чтение/Запись"
5. Нажмите "Создать ключ API"
6. Скопируйте Consumer Key и Consumer Secret

В приложении:
1. Нажмите "⚙️ Настройки подключения"
2. Введите URL вашего сайта
3. Введите Consumer Key и Consumer Secret
4. Нажмите "🔍 Тест подключения"
5. При успехе сохраните как профиль

Готово! Теперь можете управлять товарами.
        """
        messagebox.showinfo("Инструкция по настройке", instructions_text)
    
    def show_new_features(self):
        """Показать новые функции v3.0"""
        features_text = """
🆕 Новые функции WooCommerce Product Manager v3.0

🌐 УНИВЕРСАЛЬНОСТЬ:
✅ Подключение к любому WooCommerce сайту
✅ Система профилей - сохранение нескольких подключений
✅ Быстрое переключение между сайтами
✅ Валидация подключений с диагностикой

⚙️ РАСШИРЕННЫЕ НАСТРОЙКИ:
✅ Выбор версии API (v1, v2, v3)
✅ Настройка таймаутов запросов
✅ Контроль лимитов загрузки
✅ Проверки SSL сертификатов

📁 УПРАВЛЕНИЕ ПРОФИЛЯМИ:
✅ Создание именованных профилей
✅ Редактирование существующих профилей
✅ Экспорт профилей в файл
✅ Импорт профилей с других устройств

💡 УЛУЧШЕНИЯ ИНТЕРФЕЙСА:
✅ Информация о текущем профиле
✅ Статус подключения в реальном времени
✅ Быстрое переключение в главном окне
✅ Валидация данных при вводе

Используйте "⚙️ Настройки подключения" для доступа ко всем возможностям!
        """
        messagebox.showinfo("Новые функции v3.0", features_text)
    
    def export_profiles_menu(self):
        """Экспорт профилей через меню"""
        filename = filedialog.asksaveasfilename(
            title="Экспорт профилей подключения",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if config_manager.export_profiles(filename):
                messagebox.showinfo("Успех", f"Профили экспортированы в:\n{filename}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать профили")
    
    def import_profiles_menu(self):
        """Импорт профилей через меню"""
        filename = filedialog.askopenfilename(
            title="Импорт профилей подключения",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if config_manager.import_profiles(filename):
                messagebox.showinfo("Успех", "Профили успешно импортированы")
                self.update_profile_menu()  # Обновляем меню профилей
            else:
                messagebox.showerror("Ошибка", "Не удалось импортировать профили")
    
    def update_status(self, message: str):
        """Обновление статуса"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def open_connection_settings(self):
        """Открытие диалога настроек подключения"""
        try:
            dialog = ConnectionSettingsDialog(self.root)
            self.root.wait_window(dialog.dialog)
            
            # Если пользователь выбрал профиль, обновляем интерфейс
            if dialog.result:
                self.update_connection_info()
                self.update_profile_menu()
                
                # Пытаемся подключиться к API
                self.connect_to_current_profile()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть настройки подключения:\n{e}")
            logger.error(f"Ошибка открытия настроек: {e}")
    
    def update_connection_info(self):
        """Обновление информации о текущем подключении"""
        if config_manager.current_profile and config_manager.current_profile.is_valid():
            # Обновляем отображение текущего профиля
            self.current_profile_label.configure(
                text=f"📌 {config_manager.current_profile.name}", 
                text_color="green"
            )
            
            # Обновляем отображение URL
            self.site_url_label.configure(
                text=config_manager.current_profile.site_url, 
                text_color="blue"
            )
            
            # Активируем кнопку тестирования
            self.test_btn.configure(state="normal")
            
        else:
            self.current_profile_label.configure(text="Не выбран", text_color="gray")
            self.site_url_label.configure(text="Не настроен", text_color="gray")
            self.test_btn.configure(state="disabled")
            self.connection_status.configure(text="❌ Не подключено", text_color="red")
    
    def update_profile_menu(self):
        """Обновление меню выбора профилей"""
        profile_names = config_manager.get_profile_names()
        
        if profile_names:
            self.profile_menu.configure(values=profile_names)
            
            # Устанавливаем текущий профиль в меню
            if config_manager.current_profile:
                self.profile_menu.set(config_manager.current_profile.name)
            else:
                self.profile_menu.set("Выберите профиль...")
        else:
            self.profile_menu.configure(values=["Нет профилей"])
            self.profile_menu.set("Нет профилей")
    
    def switch_profile(self, profile_name: str):
        """Переключение профиля через меню"""
        if profile_name and profile_name != "Выберите профиль..." and profile_name != "Нет профилей":
            if config_manager.set_current_profile(profile_name):
                self.update_connection_info()
                self.connect_to_current_profile()
                self.update_status(f"Переключен на профиль '{profile_name}'")
            else:
                messagebox.showerror("Ошибка", f"Не удалось переключиться на профиль '{profile_name}'")
    
    def connect_to_current_profile(self):
        """Подключение к API с текущим профилем"""
        if not config_manager.is_configured():
            self.connection_status.configure(text="❌ Профиль не настроен", text_color="red")
            return
        
        try:
            # Получаем конфигурацию текущего профиля
            config = config_manager.get_current_config()
            
            # Создаем менеджер с новыми настройками
            self.wc_manager = WooCommerceManager()
            
            # Обновляем конфигурацию менеджера
            self.wc_manager._setup_api_with_config(config)
            
            self.connection_status.configure(text="✅ Подключено", text_color="green")
            
            # Активируем кнопки управления товарами
            self.load_btn.configure(state="normal")
            self.add_btn.configure(state="normal")
            
            self.update_status(f"Успешно подключен к {config['site_url']}")
            
        except Exception as e:
            self.connection_status.configure(text="❌ Ошибка подключения", text_color="red")
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к API:\n{e}")
            logger.error(f"Ошибка подключения к API: {e}")
    
    def run(self):
        """Запуск приложения"""
        # Обновляем интерфейс при запуске
        self.update_connection_info()
        self.update_profile_menu()
        
        # Если есть настроенный профиль, пытаемся подключиться
        if config_manager.is_configured():
            self.connect_to_current_profile()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = ProductManagerGUI()
    app.run() 