# 🚀 Установка WooCommerce Product Manager v3.0

## 📋 Требования
- **Python 3.8+** (Windows/macOS/Linux)
- **WordPress сайт** с плагином **WooCommerce**
- **REST API ключи** WooCommerce
- **Интернет соединение**

---

## 🎯 Быстрая установка

### 1️⃣ Скачивание

```bash
# Клонируйте репозиторий
git clone https://github.com/IzGus/wc_product-manager.git
cd wc_product-manager
```

**Альтернативный способ:**
- Скачайте ZIP архив: [Download ZIP](https://github.com/IzGus/wc_product-manager/archive/refs/heads/main.zip)
- Распакуйте в любую папку

### 2️⃣ Установка зависимостей

```bash
# Установите все необходимые библиотеки
pip install -r requirements.txt
```

**Список устанавливаемых библиотек:**
- `woocommerce>=3.0.0` - WooCommerce API клиент
- `customtkinter>=5.2.0` - Современный GUI
- `pandas>=2.0.0` - Работа с данными
- `requests>=2.31.0` - HTTP запросы  
- `python-dotenv>=1.0.0` - Переменные окружения
- `Pillow>=10.0.0` - Работа с изображениями

---

## 🔑 Настройка WooCommerce API

### В админке WordPress:

1. **Перейдите в настройки API:**
   ```
   WooCommerce → Настройки → Дополнительно → REST API
   ```

2. **Создайте новый ключ:**
   - Нажмите **"Добавить ключ"**
   - **Описание:** `Product Manager App`
   - **Пользователь:** выберите администратора
   - **Разрешения:** **Read/Write** ⚠️

3. **Сохраните ключи:**
   - **Consumer Key** (начинается с `ck_`)
   - **Consumer Secret** (начинается с `cs_`)

### ⚠️ Важные настройки:

- **Убедитесь что включены "красивые ссылки"** (Permalinks)
- **Сайт должен использовать HTTPS** с действительным сертификатом
- **WooCommerce REST API должен быть активен**

---

## 🚀 Запуск приложения

```bash
# Простой запуск
python main.py
```

**При первом запуске увидите:**
```
🚀 WooCommerce Product Manager Universal v3.0
==================================================
🌐 Универсальное подключение к любому WooCommerce сайту
👤 Система профилей для быстрого переключения  
📊 Полное управление товарами через REST API
==================================================
✅ Все зависимости установлены
✅ Приложение готово к работе! (инициализация: 2.5с)
```

---

## 🌐 Первое подключение

1. **В открывшемся окне введите:**
   - **URL сайта:** `https://your-site.com`
   - **Consumer Key:** `ck_...` (из настроек API)
   - **Consumer Secret:** `cs_...` (из настроек API)

2. **Нажмите "Тест соединения"** для проверки

3. **При успешном подключении нажмите "Загрузить товары"**

---

## 📁 Структура проекта

```
wc_product-manager/
│
├── main.py                     # 🚀 Главный файл запуска
├── main_gui.py                 # 🖥️ Основной GUI интерфейс
├── connection_settings_dialog.py # ⚙️ Диалог настроек подключения
├── product_dialog.py           # 📝 Диалог редактирования товаров
├── woocommerce_manager.py      # 🔗 Менеджер WooCommerce API
├── product_models.py           # 📊 Модели данных товаров
├── csv_manager.py              # 📁 Менеджер CSV импорт/экспорт
├── meta_fields_dialog.py       # 🏷️ Диалог мета-полей
├── woocommerce_csv_manager.py  # 🔄 CSV менеджер для WooCommerce
├── config.py                   # ⚙️ Конфигурация и профили
├── requirements.txt            # 📦 Зависимости Python
├── .gitignore                  # 🚫 Исключения Git
├── README.md                   # 📖 Документация
├── QUICK_START.md              # ⚡ Быстрый старт
├── UNIVERSAL_FEATURES.md       # ✨ Новые функции v3.0
│
├── logs/                       # 📝 Папка логов (создается автоматически)
│   └── app.log                 # 🔍 Файл логов
│
└── example_products.csv        # 📄 Пример товаров для импорта
```

---

## 📝 Примеры использования

### Импорт товаров из CSV

1. Подготовьте CSV файл с колонками:
   ```csv
   name,type,sku,regular_price,description,status
   "Тестовый товар","simple","TEST123","1999.99","Описание товара","publish"
   ```

2. В приложении: **Файл → Импорт из CSV**
3. Выберите файл и дождитесь завершения

### Экспорт товаров

1. Загрузите товары с сайта
2. **Файл → Экспорт в CSV**
3. Укажите имя файла для сохранения

---

## 🛠 Устранение проблем

### ❌ Частые ошибки:

**ModuleNotFoundError:**
```bash
# Решение: Переустановите зависимости
pip install -r requirements.txt
```

**HTTP 401 - Unauthorized:**
```
Решение: Проверьте правильность Consumer Key и Secret
```

**SSL Error:**
```
Решение: Убедитесь, что сайт использует действительный SSL сертификат
```

**Connection timeout:**
```
Решение: Проверьте доступность сайта и интернет соединение
```

### 📝 Логи и диагностика:

**Все логи сохраняются в:** `logs/app.log`

**Для диагностики проблем используйте:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Информационное сообщение")
logger.error("Сообщение об ошибке")  
```

---

## 🔄 Обновление

```bash
# Получить последние изменения
git pull origin main

# Обновить зависимости
pip install -r requirements.txt --upgrade
```

---

## 💡 Полезные команды

```bash
# Запуск приложения
python main.py

# Проверка зависимостей
pip list | grep -E "customtkinter|woocommerce|pandas"

# Обновление pip
python -m pip install --upgrade pip

# Проверка версии Python
python --version
```

---

## 📞 Поддержка

- **📖 Документация:** Читайте `README.md` для подробного описания
- **⚡ Быстрый старт:** `QUICK_START.md` для начинающих
- **✨ Новые функции:** `UNIVERSAL_FEATURES.md` для v3.0
- **🐛 Сообщить об ошибке:** [GitHub Issues](https://github.com/IzGus/wc_product-manager/issues)
- **🔗 WooCommerce API:** [Официальная документация](https://woocommerce.github.io/woocommerce-rest-api-docs/)

---

**🎉 Готово! Приложение готово к работе!**

*Простая установка без виртуальных окружений и batch файлов* 