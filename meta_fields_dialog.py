"""
Диалог для работы с мета-полями товаров WooCommerce
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any, Optional

class MetaFieldsDialog:
    """Диалог для редактирования мета-полей товара"""
    
    def __init__(self, parent, meta_data: List[Dict[str, Any]] = None):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
            meta_data: Существующие мета-поля
        """
        self.parent = parent
        self.meta_data = meta_data or []
        self.result = None
        
        self.setup_dialog()
        self.populate_fields()
        
    def setup_dialog(self):
        """Настройка диалогового окна"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Мета-поля товара")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Заголовок
        title_label = ctk.CTkLabel(self.dialog, text="Управление мета-полями", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=10)
        
        # Описание
        desc_label = ctk.CTkLabel(self.dialog, 
                                 text="Мета-поля позволяют добавить дополнительную информацию к товару",
                                 font=ctk.CTkFont(size=12))
        desc_label.pack(pady=5)
        
        # Область для списка мета-полей
        self.setup_meta_fields_area()
        
        # Кнопки управления
        self.setup_control_buttons()
        
        # Кнопки действий
        self.setup_action_buttons()
        
    def setup_meta_fields_area(self):
        """Настройка области мета-полей"""
        # Фрейм для таблицы
        table_frame = ctk.CTkFrame(self.dialog)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Заголовок
        ctk.CTkLabel(table_frame, text="Список мета-полей", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Создаем Treeview для отображения мета-полей
        columns = ("Ключ", "Значение", "Тип")
        self.meta_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Настройка заголовков
        self.meta_tree.heading("Ключ", text="Ключ")
        self.meta_tree.heading("Значение", text="Значение")
        self.meta_tree.heading("Тип", text="Тип")
        
        self.meta_tree.column("Ключ", width=150, minwidth=100)
        self.meta_tree.column("Значение", width=250, minwidth=200)
        self.meta_tree.column("Тип", width=100, minwidth=80)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.meta_tree.yview)
        self.meta_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Размещение
        self.meta_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        v_scrollbar.pack(side="right", fill="y", pady=10)
        
    def setup_control_buttons(self):
        """Настройка кнопок управления"""
        control_frame = ctk.CTkFrame(self.dialog)
        control_frame.pack(fill="x", padx=20, pady=5)
        
        # Кнопки
        add_btn = ctk.CTkButton(control_frame, text="Добавить поле", command=self.add_meta_field)
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(control_frame, text="Редактировать", command=self.edit_meta_field)
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(control_frame, text="Удалить", command=self.delete_meta_field)
        delete_btn.pack(side="left", padx=5)
        
        # Предустановленные поля
        preset_frame = ctk.CTkFrame(control_frame)
        preset_frame.pack(side="right", padx=5)
        
        ctk.CTkLabel(preset_frame, text="Быстрое добавление:").pack(side="left", padx=5)
        
        preset_menu = ctk.CTkOptionMenu(preset_frame, 
                                       values=["SEO Title", "SEO Description", "Brand", "Model", "Color", "Size"],
                                       command=self.add_preset_field)
        preset_menu.pack(side="left", padx=5)
        preset_menu.set("Выберите...")
        
    def setup_action_buttons(self):
        """Настройка кнопок действий"""
        action_frame = ctk.CTkFrame(self.dialog)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        cancel_btn = ctk.CTkButton(action_frame, text="Отмена", command=self.cancel)
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(action_frame, text="Сохранить", command=self.save)
        save_btn.pack(side="right", padx=5)
        
    def populate_fields(self):
        """Заполнение списка мета-полей"""
        for item in self.meta_tree.get_children():
            self.meta_tree.delete(item)
            
        for meta_field in self.meta_data:
            key = meta_field.get("key", "")
            value = str(meta_field.get("value", ""))
            
            # Определяем тип значения
            value_type = "string"
            if isinstance(meta_field.get("value"), bool):
                value_type = "boolean"
            elif isinstance(meta_field.get("value"), (int, float)):
                value_type = "number"
            elif isinstance(meta_field.get("value"), list):
                value_type = "array"
            elif isinstance(meta_field.get("value"), dict):
                value_type = "object"
                
            # Ограничиваем длину отображения
            display_value = value[:50] + "..." if len(value) > 50 else value
            
            self.meta_tree.insert("", "end", values=(key, display_value, value_type), 
                                 tags=(key,))
    
    def add_meta_field(self):
        """Добавление нового мета-поля"""
        self.edit_field_dialog()
        
    def add_preset_field(self, preset_name: str):
        """Добавление предустановленного поля"""
        preset_fields = {
            "SEO Title": {"key": "_yoast_wpseo_title", "value": "", "type": "string"},
            "SEO Description": {"key": "_yoast_wpseo_metadesc", "value": "", "type": "string"},
            "Brand": {"key": "_product_brand", "value": "", "type": "string"},
            "Model": {"key": "_product_model", "value": "", "type": "string"},
            "Color": {"key": "_product_color", "value": "", "type": "string"},
            "Size": {"key": "_product_size", "value": "", "type": "string"}
        }
        
        if preset_name in preset_fields:
            field_data = preset_fields[preset_name]
            self.edit_field_dialog(field_data["key"], field_data["value"])
    
    def edit_meta_field(self):
        """Редактирование выбранного мета-поля"""
        selection = self.meta_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите поле для редактирования")
            return
        
        item = self.meta_tree.item(selection[0])
        key = item["tags"][0] if item["tags"] else ""
        
        # Находим полное значение
        meta_field = next((m for m in self.meta_data if m.get("key") == key), None)
        if meta_field:
            value = meta_field.get("value", "")
            self.edit_field_dialog(key, value)
    
    def delete_meta_field(self):
        """Удаление выбранного мета-поля"""
        selection = self.meta_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите поле для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранное мета-поле?"):
            item = self.meta_tree.item(selection[0])
            key = item["tags"][0] if item["tags"] else ""
            
            # Удаляем из данных
            self.meta_data = [m for m in self.meta_data if m.get("key") != key]
            self.populate_fields()
    
    def edit_field_dialog(self, key: str = "", value: Any = ""):
        """Диалог редактирования отдельного поля"""
        field_dialog = ctk.CTkToplevel(self.dialog)
        field_dialog.title("Редактирование мета-поля")
        field_dialog.geometry("400x300")
        field_dialog.transient(self.dialog)
        field_dialog.grab_set()
        
        # Центрирование
        field_dialog.update_idletasks()
        x = (field_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (field_dialog.winfo_screenheight() // 2) - (300 // 2)
        field_dialog.geometry(f"400x300+{x}+{y}")
        
        # Поля ввода
        ctk.CTkLabel(field_dialog, text="Ключ (key):", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        key_entry = ctk.CTkEntry(field_dialog, width=350)
        key_entry.pack(pady=5)
        key_entry.insert(0, key)
        
        ctk.CTkLabel(field_dialog, text="Значение (value):", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        value_textbox = ctk.CTkTextbox(field_dialog, width=350, height=100)
        value_textbox.pack(pady=5)
        value_textbox.insert("1.0", str(value))
        
        # Тип значения
        ctk.CTkLabel(field_dialog, text="Тип значения:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        type_menu = ctk.CTkOptionMenu(field_dialog, values=["string", "number", "boolean", "array", "object"])
        type_menu.pack(pady=5)
        type_menu.set("string")
        
        # Кнопки
        def save_field():
            new_key = key_entry.get().strip()
            new_value = value_textbox.get("1.0", "end-1c").strip()
            value_type = type_menu.get()
            
            if not new_key:
                messagebox.showerror("Ошибка", "Ключ не может быть пустым")
                return
            
            # Преобразуем значение согласно типу
            try:
                if value_type == "number":
                    new_value = float(new_value) if '.' in new_value else int(new_value)
                elif value_type == "boolean":
                    new_value = new_value.lower() in ("true", "1", "yes", "on")
                elif value_type == "array":
                    new_value = [item.strip() for item in new_value.split(",") if item.strip()]
                elif value_type == "object":
                    import json
                    new_value = json.loads(new_value)
            except (ValueError, json.JSONDecodeError) as e:
                messagebox.showerror("Ошибка", f"Неверный формат значения для типа {value_type}: {e}")
                return
            
            # Обновляем или добавляем поле
            existing_field = next((m for m in self.meta_data if m.get("key") == key), None)
            if existing_field:
                existing_field["key"] = new_key
                existing_field["value"] = new_value
            else:
                self.meta_data.append({"key": new_key, "value": new_value})
            
            self.populate_fields()
            field_dialog.destroy()
        
        button_frame = ctk.CTkFrame(field_dialog)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(button_frame, text="Отмена", command=field_dialog.destroy).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Сохранить", command=save_field).pack(side="right", padx=5)
        
    def save(self):
        """Сохранение изменений"""
        self.result = self.meta_data.copy()
        self.dialog.destroy()
        
    def cancel(self):
        """Отмена изменений"""
        self.result = None
        self.dialog.destroy() 