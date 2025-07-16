"""
Диалог настройки подключений к WooCommerce API
Поддержка профилей и универсальных настроек
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from typing import Optional, Dict, Any
import re
from urllib.parse import urlparse

from config import config_manager, ConnectionProfile

class ConnectionSettingsDialog:
    """Диалог настройки подключений к WooCommerce API"""
    
    def __init__(self, parent):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
        """
        self.parent = parent
        self.result = None
        self.current_profile = None
        
        self.setup_dialog()
        self.load_profiles()
        
    def setup_dialog(self):
        """Настройка диалогового окна"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Настройки подключения WooCommerce")
        self.dialog.geometry("800x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Основной контейнер
        main_container = ctk.CTkFrame(self.dialog)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ctk.CTkLabel(main_container, 
                                  text="🔗 Настройки подключения к WooCommerce", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)
        
        # Создаем notebook для вкладок
        self.notebook = ctk.CTkTabview(main_container)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладки
        self.setup_quick_connect_tab()
        self.setup_profiles_tab()
        self.setup_advanced_tab()
        
        # Кнопки управления
        self.setup_action_buttons(main_container)
        
    def setup_quick_connect_tab(self):
        """Вкладка быстрого подключения"""
        quick_tab = self.notebook.add("Быстрое подключение")
        
        # Описание
        desc_frame = ctk.CTkFrame(quick_tab)
        desc_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(desc_frame, 
                    text="🚀 Быстрое подключение к WooCommerce",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        ctk.CTkLabel(desc_frame,
                    text="Введите данные для подключения к вашему WooCommerce магазину",
                    font=ctk.CTkFont(size=12)).pack(pady=5)
        
        # Форма подключения
        form_frame = ctk.CTkFrame(quick_tab)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # URL сайта
        ctk.CTkLabel(form_frame, text="URL сайта:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.quick_url_entry = ctk.CTkEntry(form_frame, placeholder_text="https://your-store.com")
        self.quick_url_entry.pack(fill="x", padx=10, pady=5)
        self.quick_url_entry.bind("<KeyRelease>", self.on_url_change)
        
        # Consumer Key
        ctk.CTkLabel(form_frame, text="Consumer Key:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.quick_key_entry = ctk.CTkEntry(form_frame, placeholder_text="ck_xxxxxxxxxxxxxxxxxxxxxxxxx")
        self.quick_key_entry.pack(fill="x", padx=10, pady=5)
        
        # Consumer Secret
        ctk.CTkLabel(form_frame, text="Consumer Secret:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.quick_secret_entry = ctk.CTkEntry(form_frame, placeholder_text="cs_xxxxxxxxxxxxxxxxxxxxxxxxx", show="*")
        self.quick_secret_entry.pack(fill="x", padx=10, pady=5)
        
        # Показать/скрыть секрет
        show_secret_var = ctk.BooleanVar()
        show_secret_cb = ctk.CTkCheckBox(form_frame, text="Показать Consumer Secret", 
                                        variable=show_secret_var, command=lambda: self.toggle_secret_visibility(show_secret_var.get()))
        show_secret_cb.pack(anchor="w", padx=10, pady=5)
        
        # Кнопки быстрых действий
        quick_buttons_frame = ctk.CTkFrame(form_frame)
        quick_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        test_btn = ctk.CTkButton(quick_buttons_frame, text="🔍 Тест подключения", 
                                command=self.test_quick_connection, width=150)
        test_btn.pack(side="left", padx=5)
        
        save_profile_btn = ctk.CTkButton(quick_buttons_frame, text="💾 Сохранить как профиль", 
                                        command=self.save_as_profile, width=180)
        save_profile_btn.pack(side="left", padx=5)
        
        connect_btn = ctk.CTkButton(quick_buttons_frame, text="✅ Подключиться", 
                                   command=self.quick_connect, width=150)
        connect_btn.pack(side="right", padx=5)
        
        # Статус подключения
        self.quick_status_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=12))
        self.quick_status_label.pack(pady=5)
        
        # Инструкция
        self.setup_instruction_section(quick_tab)
        
    def setup_profiles_tab(self):
        """Вкладка управления профилями"""
        profiles_tab = self.notebook.add("Профили")
        
        # Заголовок
        header_frame = ctk.CTkFrame(profiles_tab)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, 
                    text="📁 Управление профилями подключений",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Основной контейнер
        main_frame = ctk.CTkFrame(profiles_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Список профилей
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkLabel(list_frame, text="Сохраненные профили:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        # Создаем Treeview для списка профилей
        columns = ("Название", "URL", "Последнее использование")
        self.profiles_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.profiles_tree.heading(col, text=col)
            if col == "Название":
                self.profiles_tree.column(col, width=150, minwidth=100)
            elif col == "URL":
                self.profiles_tree.column(col, width=200, minwidth=150)
            else:
                self.profiles_tree.column(col, width=150, minwidth=100)
        
        # Скроллбар для списка
        profiles_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.profiles_tree.yview)
        self.profiles_tree.configure(yscrollcommand=profiles_scrollbar.set)
        
        self.profiles_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        profiles_scrollbar.pack(side="right", fill="y", pady=10)
        
        # Привязка событий
        self.profiles_tree.bind("<<TreeviewSelect>>", self.on_profile_select)
        self.profiles_tree.bind("<Double-1>", self.edit_profile)
        
        # Панель управления профилями
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(side="right", fill="y", padx=(5, 10), pady=10)
        
        ctk.CTkLabel(control_frame, text="Управление:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Кнопки управления
        self.use_profile_btn = ctk.CTkButton(control_frame, text="📌 Использовать", 
                                            command=self.use_selected_profile, width=140)
        self.use_profile_btn.pack(pady=5)
        
        self.edit_profile_btn = ctk.CTkButton(control_frame, text="✏️ Редактировать", 
                                             command=self.edit_profile, width=140)
        self.edit_profile_btn.pack(pady=5)
        
        self.delete_profile_btn = ctk.CTkButton(control_frame, text="🗑️ Удалить", 
                                               command=self.delete_profile, width=140)
        self.delete_profile_btn.pack(pady=5)
        
        ctk.CTkLabel(control_frame, text="").pack(pady=10)  # Разделитель
        
        self.export_btn = ctk.CTkButton(control_frame, text="📤 Экспорт", 
                                       command=self.export_profiles, width=140)
        self.export_btn.pack(pady=5)
        
        self.import_btn = ctk.CTkButton(control_frame, text="📥 Импорт", 
                                       command=self.import_profiles, width=140)
        self.import_btn.pack(pady=5)
        
        # Отключаем кнопки по умолчанию
        self.use_profile_btn.configure(state="disabled")
        self.edit_profile_btn.configure(state="disabled")
        self.delete_profile_btn.configure(state="disabled")
        
    def setup_advanced_tab(self):
        """Вкладка расширенных настроек"""
        advanced_tab = self.notebook.add("Расширенные")
        
        # Заголовок
        header_frame = ctk.CTkFrame(advanced_tab)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, 
                    text="⚙️ Расширенные настройки подключения",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Форма настроек
        settings_frame = ctk.CTkFrame(advanced_tab)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # API версия
        ctk.CTkLabel(settings_frame, text="Версия API:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.api_version_menu = ctk.CTkOptionMenu(settings_frame, values=["wc/v3", "wc/v2", "wc/v1"])
        self.api_version_menu.pack(anchor="w", padx=10, pady=5)
        self.api_version_menu.set("wc/v3")
        
        # Таймаут запросов
        ctk.CTkLabel(settings_frame, text="Таймаут запросов (секунды):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.timeout_entry = ctk.CTkEntry(settings_frame, placeholder_text="30")
        self.timeout_entry.pack(anchor="w", padx=10, pady=5, fill="x")
        self.timeout_entry.insert(0, "30")
        
        # Товаров на страницу
        ctk.CTkLabel(settings_frame, text="Товаров на страницу:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.per_page_entry = ctk.CTkEntry(settings_frame, placeholder_text="100")
        self.per_page_entry.pack(anchor="w", padx=10, pady=5, fill="x")
        self.per_page_entry.insert(0, "100")
        
        # Дополнительные опции
        options_frame = ctk.CTkFrame(settings_frame)
        options_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkLabel(options_frame, text="Дополнительные опции:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.ssl_verify_var = ctk.BooleanVar(value=True)
        ssl_cb = ctk.CTkCheckBox(options_frame, text="Проверять SSL сертификат", variable=self.ssl_verify_var)
        ssl_cb.pack(anchor="w", padx=10, pady=2)
        
        self.debug_mode_var = ctk.BooleanVar(value=False)
        debug_cb = ctk.CTkCheckBox(options_frame, text="Режим отладки", variable=self.debug_mode_var)
        debug_cb.pack(anchor="w", padx=10, pady=2)
        
    def setup_instruction_section(self, parent):
        """Секция с инструкциями"""
        instruction_frame = ctk.CTkFrame(parent)
        instruction_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(instruction_frame, 
                    text="📋 Как получить Consumer Key и Consumer Secret:",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        instructions = [
            "1. Войдите в админку WordPress",
            "2. Перейдите в WooCommerce → Настройки → Дополнительно → REST API",
            "3. Нажмите 'Добавить ключ'",
            "4. Выберите права доступа: 'Чтение/Запись'",
            "5. Скопируйте Consumer Key и Consumer Secret"
        ]
        
        for instruction in instructions:
            ctk.CTkLabel(instruction_frame, text=instruction, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
        
    def setup_action_buttons(self, parent):
        """Кнопки действий"""
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="❌ Отмена", command=self.cancel, width=100)
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(buttons_frame, text="💾 Сохранить и закрыть", command=self.save_and_close, width=180)
        save_btn.pack(side="right", padx=5)
        
    def toggle_secret_visibility(self, show: bool):
        """Переключение видимости Consumer Secret"""
        self.quick_secret_entry.configure(show="" if show else "*")
        
    def on_url_change(self, event=None):
        """Обработка изменения URL"""
        url = self.quick_url_entry.get().strip()
        if url and not url.startswith(('http://', 'https://')):
            # Автоматически добавляем https://
            self.quick_url_entry.delete(0, "end")
            self.quick_url_entry.insert(0, f"https://{url}")
    
    def validate_url(self, url: str) -> bool:
        """Валидация URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def validate_api_key(self, key: str) -> bool:
        """Валидация API ключа"""
        # Consumer Key должен начинаться с ck_ и быть определенной длины
        if key.startswith('ck_') and len(key) > 10:
            return True
        return False
    
    def validate_api_secret(self, secret: str) -> bool:
        """Валидация API секрета"""
        # Consumer Secret должен начинаться с cs_ и быть определенной длины  
        if secret.startswith('cs_') and len(secret) > 10:
            return True
        return False
    
    def test_quick_connection(self):
        """Тестирование быстрого подключения"""
        url = self.quick_url_entry.get().strip()
        key = self.quick_key_entry.get().strip()
        secret = self.quick_secret_entry.get().strip()
        
        # Валидация
        if not url:
            self.show_quick_status("❌ Введите URL сайта", "red")
            return
        
        if not self.validate_url(url):
            self.show_quick_status("❌ Некорректный URL сайта", "red")
            return
        
        if not key:
            self.show_quick_status("❌ Введите Consumer Key", "red")
            return
        
        if not self.validate_api_key(key):
            self.show_quick_status("❌ Некорректный Consumer Key", "red")
            return
        
        if not secret:
            self.show_quick_status("❌ Введите Consumer Secret", "red")
            return
        
        if not self.validate_api_secret(secret):
            self.show_quick_status("❌ Некорректный Consumer Secret", "red")
            return
        
        # Создаем временный профиль для тестирования
        test_profile = ConnectionProfile(
            name="test",
            site_url=url,
            consumer_key=key,
            consumer_secret=secret
        )
        
        # Тестируем подключение
        self.show_quick_status("🔄 Тестирование подключения...", "blue")
        
        # Здесь должен быть реальный тест API
        try:
            from woocommerce import API
            
            api = API(
                url=test_profile.site_url,
                consumer_key=test_profile.consumer_key,
                consumer_secret=test_profile.consumer_secret,
                version=test_profile.api_version,
                timeout=test_profile.timeout
            )
            
            response = api.get("products", params={"per_page": 1})
            
            if response.status_code == 200:
                self.show_quick_status("✅ Подключение успешно!", "green")
            else:
                self.show_quick_status(f"❌ Ошибка: {response.status_code}", "red")
                
        except Exception as e:
            self.show_quick_status(f"❌ Ошибка: {str(e)[:50]}...", "red")
    
    def show_quick_status(self, message: str, color: str):
        """Отображение статуса быстрого подключения"""
        self.quick_status_label.configure(text=message, text_color=color)
        
    def save_as_profile(self):
        """Сохранение как профиль"""
        url = self.quick_url_entry.get().strip()
        key = self.quick_key_entry.get().strip()
        secret = self.quick_secret_entry.get().strip()
        
        if not all([url, key, secret]):
            messagebox.showerror("Ошибка", "Заполните все поля для сохранения профиля")
            return
        
        # Генерируем имя профиля
        profile_name = config_manager._generate_profile_name(url)
        
        # Запрашиваем имя профиля у пользователя
        profile_name = ctk.CTkInputDialog(
            text=f"Введите имя профиля:",
            title="Сохранение профиля"
        ).get_input()
        
        if not profile_name:
            return
        
        # Создаем профиль
        profile = ConnectionProfile(
            name=profile_name,
            site_url=url,
            consumer_key=key,
            consumer_secret=secret,
            api_version=self.api_version_menu.get(),
            timeout=int(self.timeout_entry.get() or 30),
            products_per_page=int(self.per_page_entry.get() or 100)
        )
        
        if config_manager.add_profile(profile):
            messagebox.showinfo("Успех", f"Профиль '{profile_name}' сохранен")
            self.load_profiles()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить профиль")
    
    def quick_connect(self):
        """Быстрое подключение"""
        url = self.quick_url_entry.get().strip()
        key = self.quick_key_entry.get().strip()
        secret = self.quick_secret_entry.get().strip()
        
        if not all([url, key, secret]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        # Создаем временный профиль
        profile = config_manager.create_quick_profile(url, key, secret)
        config_manager.current_profile = profile
        
        self.result = profile
        self.dialog.destroy()
    
    def load_profiles(self):
        """Загрузка списка профилей"""
        # Очищаем список
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)
        
        # Заполняем список
        for profile in config_manager.profiles.values():
            last_used = "Никогда"
            if profile.last_used:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(profile.last_used)
                    last_used = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    last_used = "Неизвестно"
            
            # Добавляем индикатор текущего профиля
            name = profile.name
            if config_manager.current_profile and config_manager.current_profile.name == profile.name:
                name = f"📌 {name} (текущий)"
            
            self.profiles_tree.insert("", "end", values=(name, profile.site_url, last_used), tags=(profile.name,))
    
    def on_profile_select(self, event):
        """Обработка выбора профиля"""
        selection = self.profiles_tree.selection()
        if selection:
            self.use_profile_btn.configure(state="normal")
            self.edit_profile_btn.configure(state="normal")
            self.delete_profile_btn.configure(state="normal")
        else:
            self.use_profile_btn.configure(state="disabled")
            self.edit_profile_btn.configure(state="disabled")
            self.delete_profile_btn.configure(state="disabled")
    
    def use_selected_profile(self):
        """Использование выбранного профиля"""
        selection = self.profiles_tree.selection()
        if not selection:
            return
        
        item = self.profiles_tree.item(selection[0])
        profile_name = item["tags"][0] if item["tags"] else ""
        
        if config_manager.set_current_profile(profile_name):
            messagebox.showinfo("Успех", f"Профиль '{profile_name}' активирован")
            self.load_profiles()  # Обновляем список
            self.result = config_manager.current_profile
        else:
            messagebox.showerror("Ошибка", "Не удалось активировать профиль")
    
    def edit_profile(self, event=None):
        """Редактирование профиля"""
        selection = self.profiles_tree.selection()
        if not selection:
            return
        
        item = self.profiles_tree.item(selection[0])
        profile_name = item["tags"][0] if item["tags"] else ""
        profile = config_manager.get_profile(profile_name)
        
        if not profile:
            return
        
        # Открываем диалог редактирования
        edit_dialog = ProfileEditDialog(self.dialog, profile)
        self.dialog.wait_window(edit_dialog.dialog)
        
        if edit_dialog.result:
            config_manager.update_profile(edit_dialog.result)
            self.load_profiles()
    
    def delete_profile(self):
        """Удаление профиля"""
        selection = self.profiles_tree.selection()
        if not selection:
            return
        
        item = self.profiles_tree.item(selection[0])
        profile_name = item["tags"][0] if item["tags"] else ""
        
        if messagebox.askyesno("Подтверждение", f"Удалить профиль '{profile_name}'?"):
            if config_manager.delete_profile(profile_name):
                messagebox.showinfo("Успех", "Профиль удален")
                self.load_profiles()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить профиль")
    
    def export_profiles(self):
        """Экспорт профилей"""
        filename = filedialog.asksaveasfilename(
            title="Экспорт профилей",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if config_manager.export_profiles(filename):
                messagebox.showinfo("Успех", "Профили экспортированы")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать профили")
    
    def import_profiles(self):
        """Импорт профилей"""
        filename = filedialog.askopenfilename(
            title="Импорт профилей",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if config_manager.import_profiles(filename):
                messagebox.showinfo("Успех", "Профили импортированы")
                self.load_profiles()
            else:
                messagebox.showerror("Ошибка", "Не удалось импортировать профили")
    
    def save_and_close(self):
        """Сохранение и закрытие"""
        self.result = config_manager.current_profile
        self.dialog.destroy()
    
    def cancel(self):
        """Отмена"""
        self.result = None
        self.dialog.destroy()

class ProfileEditDialog:
    """Диалог редактирования профиля"""
    
    def __init__(self, parent, profile: ConnectionProfile):
        self.parent = parent
        self.profile = profile
        self.result = None
        
        self.setup_dialog()
        self.load_profile_data()
    
    def setup_dialog(self):
        """Настройка диалога"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(f"Редактирование профиля: {self.profile.name}")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Центрируем
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        ctk.CTkLabel(main_frame, text=f"Редактирование профиля", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Поля
        ctk.CTkLabel(main_frame, text="Название профиля:").pack(anchor="w", padx=10, pady=(10, 0))
        self.name_entry = ctk.CTkEntry(main_frame)
        self.name_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(main_frame, text="URL сайта:").pack(anchor="w", padx=10, pady=(10, 0))
        self.url_entry = ctk.CTkEntry(main_frame)
        self.url_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(main_frame, text="Consumer Key:").pack(anchor="w", padx=10, pady=(10, 0))
        self.key_entry = ctk.CTkEntry(main_frame)
        self.key_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(main_frame, text="Consumer Secret:").pack(anchor="w", padx=10, pady=(10, 0))
        self.secret_entry = ctk.CTkEntry(main_frame, show="*")
        self.secret_entry.pack(fill="x", padx=10, pady=5)
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", padx=10, pady=20)
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Отмена", command=self.cancel)
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(buttons_frame, text="Сохранить", command=self.save)
        save_btn.pack(side="right", padx=5)
    
    def load_profile_data(self):
        """Загрузка данных профиля"""
        self.name_entry.insert(0, self.profile.name)
        self.url_entry.insert(0, self.profile.site_url)
        self.key_entry.insert(0, self.profile.consumer_key)
        self.secret_entry.insert(0, self.profile.consumer_secret)
    
    def save(self):
        """Сохранение изменений"""
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        key = self.key_entry.get().strip()
        secret = self.secret_entry.get().strip()
        
        if not all([name, url, key, secret]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        # Обновляем профиль
        self.profile.name = name
        self.profile.site_url = url
        self.profile.consumer_key = key
        self.profile.consumer_secret = secret
        
        self.result = self.profile
        self.dialog.destroy()
    
    def cancel(self):
        """Отмена"""
        self.result = None
        self.dialog.destroy() 