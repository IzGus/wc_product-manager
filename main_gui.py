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
from config import WooCommerceConfig

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
        file_menu.add_command(label="Импорт из CSV", command=self.import_csv)
        file_menu.add_command(label="Экспорт в CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def setup_api_frame(self):
        """Панель настроек API"""
        api_frame = ctk.CTkFrame(self.root)
        api_frame.pack(fill="x", padx=10, pady=5)
        
        # Заголовок
        title_label = ctk.CTkLabel(api_frame, text="Настройки API", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=5)
        
        # Поля ввода
        input_frame = ctk.CTkFrame(api_frame)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # URL сайта
        url_frame = ctk.CTkFrame(input_frame)
        url_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(url_frame, text="URL сайта:", width=100).pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://your-site.com")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Кнопки
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(fill="x", pady=5)
        
        self.connect_btn = ctk.CTkButton(button_frame, text="Подключиться", command=self.connect_api)
        self.connect_btn.pack(side="left", padx=5)
        
        self.test_btn = ctk.CTkButton(button_frame, text="Тест соединения", command=self.test_connection, state="disabled")
        self.test_btn.pack(side="left", padx=5)
        
        # Статус подключения
        self.connection_status = ctk.CTkLabel(button_frame, text="Не подключено", text_color="red")
        self.connection_status.pack(side="right", padx=5)
    
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
            display_info = product.get_display_info()
            values = [display_info.get(col, "") for col in self.products_tree["columns"]]
            self.products_tree.insert("", "end", values=values, tags=(product.id,))
    
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
            # Удаляем товар из списка
            self.products = [p for p in self.products if p.id != product_id]
            self.update_products_table()
            self.update_status("Товар помечен для удаления. Нажмите 'Сохранить изменения' для применения.")
    
    def save_changes(self):
        """Сохранение изменений на сайт"""
        if not self.wc_manager:
            messagebox.showerror("Ошибка", "API не подключен")
            return
        
        # Здесь должна быть логика синхронизации с сайтом
        messagebox.showinfo("Информация", "Функция сохранения будет реализована в следующей версии")
    
    def import_csv(self):
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
                    imported_products = self.csv_manager.import_products_from_csv(filename)
                    self.products.extend(imported_products)
                    
                    self.root.after(0, self.update_products_table)
                    self.root.after(0, lambda: self.update_status(f"Импортировано {len(imported_products)} товаров"))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка импорта", f"Не удалось импортировать CSV:\n{e}"))
                finally:
                    self.root.after(0, lambda: self.progress_bar.stop())
            
            threading.Thread(target=import_thread, daemon=True).start()
    
    def export_csv(self):
        """Экспорт товаров в CSV"""
        if not self.products:
            messagebox.showwarning("Предупреждение", "Нет товаров для экспорта")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Сохранить как CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            def export_thread():
                self.root.after(0, lambda: self.update_status("Экспорт в CSV..."))
                self.root.after(0, lambda: self.progress_bar.start())
                
                try:
                    success = self.csv_manager.export_products_to_csv(self.products, filename)
                    if success:
                        self.root.after(0, lambda: messagebox.showinfo("Успех", "Экспорт завершен успешно"))
                        self.root.after(0, lambda: self.update_status("Экспорт завершен"))
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
WooCommerce Product Manager v1.0

Приложение для управления товарами 
WordPress + WooCommerce через REST API

Возможности:
• Загрузка товаров с сайта
• Создание и редактирование товаров
• Поддержка вариативных товаров
• Импорт/экспорт CSV
• Управление атрибутами и категориями

Разработано с использованием Python и CustomTkinter
        """
        messagebox.showinfo("О программе", about_text)
    
    def update_status(self, message: str):
        """Обновление статуса"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ProductManagerGUI()
    app.run() 