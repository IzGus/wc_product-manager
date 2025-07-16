"""
Диалоговое окно для управления атрибутами товаров
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any, Optional
import threading
import logging

logger = logging.getLogger(__name__)

class AttributesManagerDialog:
    """Диалоговое окно для управления атрибутами"""
    
    def __init__(self, parent, wc_manager):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
            wc_manager: Менеджер WooCommerce
        """
        self.parent = parent
        self.wc_manager = wc_manager
        self.attributes = []
        self.selected_attribute = None
        
        # Создаем диалоговое окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Управление атрибутами")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self.center_window()
        
        self.setup_ui()
        self.load_attributes()
    
    def center_window(self):
        """Центрирование окна относительно родительского"""
        self.window.update_idletasks()
        
        # Получаем размеры окон
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Вычисляем позицию
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главный контейнер
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ctk.CTkLabel(main_frame, text="Управление атрибутами товаров", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Создаем панель с двумя колонками
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Левая панель - список атрибутов
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Правая панель - редактирование
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.setup_attributes_list(left_frame)
        self.setup_attribute_editor(right_frame)
        
        # Кнопки управления
        self.setup_control_buttons(main_frame)
    
    def setup_attributes_list(self, parent_frame):
        """Настройка списка атрибутов"""
        # Заголовок
        list_title = ctk.CTkLabel(parent_frame, text="Список атрибутов", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        list_title.pack(pady=(10, 5))
        
        # Кнопки управления списком
        list_buttons_frame = ctk.CTkFrame(parent_frame)
        list_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        self.add_attr_btn = ctk.CTkButton(list_buttons_frame, text="➕ Добавить", 
                                        command=self.add_attribute, width=80)
        self.add_attr_btn.pack(side="left", padx=5)
        
        self.delete_attr_btn = ctk.CTkButton(list_buttons_frame, text="🗑 Удалить", 
                                           command=self.delete_attribute, width=80, state="disabled")
        self.delete_attr_btn.pack(side="left", padx=5)
        
        self.refresh_btn = ctk.CTkButton(list_buttons_frame, text="🔄 Обновить", 
                                       command=self.load_attributes, width=80)
        self.refresh_btn.pack(side="right", padx=5)
        
        # Создаем Treeview для списка атрибутов
        tree_frame = ctk.CTkFrame(parent_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Используем tkinter Treeview, так как customtkinter его не имеет
        style = ttk.Style()
        style.theme_use("clam")
        
        self.attributes_tree = ttk.Treeview(tree_frame, columns=("id", "name", "slug", "terms"), show="headings")
        self.attributes_tree.heading("id", text="ID")
        self.attributes_tree.heading("name", text="Название")
        self.attributes_tree.heading("slug", text="Slug")
        self.attributes_tree.heading("terms", text="Термины")
        
        self.attributes_tree.column("id", width=50)
        self.attributes_tree.column("name", width=150)
        self.attributes_tree.column("slug", width=150)
        self.attributes_tree.column("terms", width=100)
        
        # Скроллбар для дерева
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.attributes_tree.yview)
        self.attributes_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.attributes_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Привязываем события
        self.attributes_tree.bind("<<TreeviewSelect>>", self.on_attribute_select)
    
    def setup_attribute_editor(self, parent_frame):
        """Настройка панели редактирования атрибута"""
        # Заголовок
        editor_title = ctk.CTkLabel(parent_frame, text="Редактирование атрибута", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        editor_title.pack(pady=(10, 5))
        
        # Форма редактирования
        form_frame = ctk.CTkScrollableFrame(parent_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Название атрибута
        ctk.CTkLabel(form_frame, text="Название атрибута:").pack(anchor="w", pady=(5, 0))
        self.attr_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Введите название атрибута")
        self.attr_name_entry.pack(fill="x", pady=(0, 10))
        
        # Slug атрибута
        ctk.CTkLabel(form_frame, text="Slug (для URL):").pack(anchor="w", pady=(5, 0))
        self.attr_slug_entry = ctk.CTkEntry(form_frame, placeholder_text="Автоматически из названия")
        self.attr_slug_entry.pack(fill="x", pady=(0, 10))
        
        # Тип сортировки
        ctk.CTkLabel(form_frame, text="Сортировка:").pack(anchor="w", pady=(5, 0))
        self.order_by_var = ctk.StringVar(value="menu_order")
        order_by_frame = ctk.CTkFrame(form_frame)
        order_by_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkRadioButton(order_by_frame, text="По порядку меню", variable=self.order_by_var, 
                          value="menu_order").pack(side="left", padx=10)
        ctk.CTkRadioButton(order_by_frame, text="По имени", variable=self.order_by_var, 
                          value="name").pack(side="left", padx=10)
        
        # Дополнительные настройки
        settings_frame = ctk.CTkFrame(form_frame)
        settings_frame.pack(fill="x", pady=(0, 10))
        
        self.has_archives_var = ctk.BooleanVar()
        ctk.CTkCheckBox(settings_frame, text="Включить архивы", 
                       variable=self.has_archives_var).pack(anchor="w", padx=10, pady=5)
        
        # Термины (значения) атрибута
        ctk.CTkLabel(form_frame, text="Значения атрибута:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(20, 5))
        
        # Кнопки управления терминами
        terms_buttons_frame = ctk.CTkFrame(form_frame)
        terms_buttons_frame.pack(fill="x", pady=5)
        
        self.add_term_btn = ctk.CTkButton(terms_buttons_frame, text="➕ Добавить значение", 
                                        command=self.add_term, state="disabled")
        self.add_term_btn.pack(side="left", padx=5)
        
        self.delete_term_btn = ctk.CTkButton(terms_buttons_frame, text="🗑 Удалить значение", 
                                           command=self.delete_term, state="disabled")
        self.delete_term_btn.pack(side="left", padx=5)
        
        # Список терминов
        terms_frame = ctk.CTkFrame(form_frame)
        terms_frame.pack(fill="x", pady=5)
        
        self.terms_listbox = tk.Listbox(terms_frame, height=6)
        self.terms_listbox.pack(fill="x", padx=5, pady=5)
        
        # Кнопки сохранения
        save_buttons_frame = ctk.CTkFrame(form_frame)
        save_buttons_frame.pack(fill="x", pady=(20, 5))
        
        self.save_attr_btn = ctk.CTkButton(save_buttons_frame, text="💾 Сохранить атрибут", 
                                         command=self.save_attribute, state="disabled")
        self.save_attr_btn.pack(side="right", padx=5)
        
        self.cancel_edit_btn = ctk.CTkButton(save_buttons_frame, text="↶ Отменить", 
                                           command=self.cancel_edit, state="disabled")
        self.cancel_edit_btn.pack(side="right", padx=5)
    
    def setup_control_buttons(self, parent_frame):
        """Кнопки управления диалогом"""
        buttons_frame = ctk.CTkFrame(parent_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        close_btn = ctk.CTkButton(buttons_frame, text="Закрыть", command=self.close_dialog)
        close_btn.pack(side="right", padx=5)
    
    def load_attributes(self):
        """Загрузка атрибутов с сервера"""
        def load_thread():
            try:
                # Показываем индикатор загрузки
                self.window.after(0, lambda: self.refresh_btn.configure(text="⏳ Загрузка..."))
                
                # Загружаем атрибуты
                self.attributes = self.wc_manager.get_attributes()
                
                # Обновляем список в главном потоке
                self.window.after(0, self.update_attributes_list)
                
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось загрузить атрибуты:\n{e}"))
            finally:
                self.window.after(0, lambda: self.refresh_btn.configure(text="🔄 Обновить"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_attributes_list(self):
        """Обновление списка атрибутов в интерфейсе"""
        # Очищаем текущий список
        for item in self.attributes_tree.get_children():
            self.attributes_tree.delete(item)
        
        # Добавляем атрибуты
        for attr in self.attributes:
            # Получаем количество терминов для каждого атрибута
            terms_count = len(self.wc_manager.get_attribute_terms(attr['id']))
            
            self.attributes_tree.insert("", "end", values=(
                attr['id'],
                attr['name'],
                attr['slug'],
                f"{terms_count} шт."
            ))
    
    def on_attribute_select(self, event):
        """Обработка выбора атрибута из списка"""
        selection = self.attributes_tree.selection()
        if not selection:
            self.selected_attribute = None
            self.clear_editor()
            return
        
        # Получаем данные выбранного атрибута
        item = self.attributes_tree.item(selection[0])
        attr_id = int(item['values'][0])
        
        # Находим атрибут в списке
        self.selected_attribute = next((attr for attr in self.attributes if attr['id'] == attr_id), None)
        
        if self.selected_attribute:
            self.load_attribute_to_editor()
            
            # Активируем кнопки
            self.delete_attr_btn.configure(state="normal")
            self.add_term_btn.configure(state="normal")
            self.save_attr_btn.configure(state="normal")
            self.cancel_edit_btn.configure(state="normal")
    
    def load_attribute_to_editor(self):
        """Загрузка данных атрибута в редактор"""
        if not self.selected_attribute:
            return
        
        # Заполняем основные поля
        self.attr_name_entry.delete(0, "end")
        self.attr_name_entry.insert(0, self.selected_attribute.get('name', ''))
        
        self.attr_slug_entry.delete(0, "end")
        self.attr_slug_entry.insert(0, self.selected_attribute.get('slug', ''))
        
        self.order_by_var.set(self.selected_attribute.get('order_by', 'menu_order'))
        self.has_archives_var.set(self.selected_attribute.get('has_archives', False))
        
        # Загружаем термины
        self.load_terms()
    
    def load_terms(self):
        """Загрузка терминов атрибута"""
        if not self.selected_attribute:
            return
        
        def load_terms_thread():
            try:
                terms = self.wc_manager.get_attribute_terms(self.selected_attribute['id'])
                self.window.after(0, lambda: self.update_terms_list(terms))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось загрузить термины:\n{e}"))
        
        threading.Thread(target=load_terms_thread, daemon=True).start()
    
    def update_terms_list(self, terms):
        """Обновление списка терминов"""
        self.terms_listbox.delete(0, "end")
        for term in terms:
            self.terms_listbox.insert("end", f"{term['name']} (ID: {term['id']})")
    
    def clear_editor(self):
        """Очистка редактора"""
        self.attr_name_entry.delete(0, "end")
        self.attr_slug_entry.delete(0, "end")
        self.order_by_var.set("menu_order")
        self.has_archives_var.set(False)
        self.terms_listbox.delete(0, "end")
        
        # Деактивируем кнопки
        self.delete_attr_btn.configure(state="disabled")
        self.add_term_btn.configure(state="disabled")
        self.delete_term_btn.configure(state="disabled")
        self.save_attr_btn.configure(state="disabled")
        self.cancel_edit_btn.configure(state="disabled")
    
    def add_attribute(self):
        """Добавление нового атрибута"""
        # Очищаем редактор для нового атрибута
        self.selected_attribute = None
        self.clear_editor()
        
        # Активируем только кнопки сохранения
        self.save_attr_btn.configure(state="normal")
        self.cancel_edit_btn.configure(state="normal")
    
    def delete_attribute(self):
        """Удаление выбранного атрибута"""
        if not self.selected_attribute:
            return
        
        # Подтверждение удаления
        result = messagebox.askyesno("Подтверждение", 
                                   f"Вы действительно хотите удалить атрибут '{self.selected_attribute['name']}'?\n"
                                   "Это действие нельзя отменить!")
        
        if result:
            def delete_thread():
                try:
                    success = self.wc_manager.delete_attribute(self.selected_attribute['id'])
                    if success:
                        self.window.after(0, lambda: messagebox.showinfo("Успех", "Атрибут успешно удален"))
                        self.window.after(0, self.load_attributes)
                        self.window.after(0, self.clear_editor)
                    else:
                        self.window.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось удалить атрибут"))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при удалении атрибута:\n{e}"))
            
            threading.Thread(target=delete_thread, daemon=True).start()
    
    def save_attribute(self):
        """Сохранение атрибута"""
        # Валидация
        name = self.attr_name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите название атрибута")
            return
        
        # Подготавливаем данные
        slug = self.attr_slug_entry.get().strip()
        if not slug:
            # Генерируем slug из названия
            slug = name.lower().replace(' ', '-').replace('_', '-')
        
        attribute_data = {
            "name": name,
            "slug": slug,
            "order_by": self.order_by_var.get(),
            "has_archives": self.has_archives_var.get()
        }
        
        def save_thread():
            try:
                if self.selected_attribute:
                    # Обновляем существующий атрибут
                    result = self.wc_manager.update_attribute(self.selected_attribute['id'], attribute_data)
                else:
                    # Создаем новый атрибут
                    result = self.wc_manager.create_attribute(attribute_data)
                
                if result:
                    self.window.after(0, lambda: messagebox.showinfo("Успех", 
                                    "Атрибут успешно сохранен" if self.selected_attribute else "Атрибут успешно создан"))
                    self.window.after(0, self.load_attributes)
                    self.window.after(0, self.clear_editor)
                else:
                    self.window.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось сохранить атрибут"))
                    
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при сохранении атрибута:\n{e}"))
        
        threading.Thread(target=save_thread, daemon=True).start()
    
    def cancel_edit(self):
        """Отмена редактирования"""
        if self.selected_attribute:
            self.load_attribute_to_editor()
        else:
            self.clear_editor()
    
    def add_term(self):
        """Добавление нового термина к атрибуту"""
        if not self.selected_attribute:
            return
        
        # Простой диалог для ввода названия термина
        dialog = ctk.CTkInputDialog(text="Введите название нового значения атрибута:", title="Добавить значение")
        term_name = dialog.get_input()
        
        if term_name and term_name.strip():
            term_data = {
                "name": term_name.strip(),
                "slug": term_name.strip().lower().replace(' ', '-')
            }
            
            def add_term_thread():
                try:
                    result = self.wc_manager.create_attribute_term(self.selected_attribute['id'], term_data)
                    if result:
                        self.window.after(0, lambda: messagebox.showinfo("Успех", "Значение успешно добавлено"))
                        self.window.after(0, self.load_terms)
                    else:
                        self.window.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось добавить значение"))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при добавлении значения:\n{e}"))
            
            threading.Thread(target=add_term_thread, daemon=True).start()
    
    def delete_term(self):
        """Удаление выбранного термина"""
        if not self.selected_attribute:
            return
        
        selection = self.terms_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите значение для удаления")
            return
        
        # Извлекаем ID термина из текста
        term_text = self.terms_listbox.get(selection[0])
        try:
            term_id = int(term_text.split("ID: ")[1].rstrip(")"))
        except (IndexError, ValueError):
            messagebox.showerror("Ошибка", "Не удалось определить ID значения")
            return
        
        # Подтверждение удаления
        result = messagebox.askyesno("Подтверждение", f"Удалить значение '{term_text.split(' (ID:')[0]}'?")
        
        if result:
            def delete_term_thread():
                try:
                    success = self.wc_manager.delete_attribute_term(self.selected_attribute['id'], term_id)
                    if success:
                        self.window.after(0, lambda: messagebox.showinfo("Успех", "Значение успешно удалено"))
                        self.window.after(0, self.load_terms)
                    else:
                        self.window.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось удалить значение"))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при удалении значения:\n{e}"))
            
            threading.Thread(target=delete_term_thread, daemon=True).start()
    
    def close_dialog(self):
        """Закрытие диалога"""
        self.window.destroy() 