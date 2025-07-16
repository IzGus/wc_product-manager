# 🛒 WooCommerce Product Manager

**Приложение для управления товарами WordPress + WooCommerce через REST API**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![WooCommerce](https://img.shields.io/badge/WooCommerce-REST%20API%20v3-purple.svg)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)

## 📋 Описание

WooCommerce Product Manager - это настольное приложение на Python, которое позволяет управлять товарами вашего интернет-магазина на WordPress + WooCommerce через REST API. Приложение предоставляет удобный графический интерфейс для создания, редактирования, удаления товаров и работы с их атрибутами.

## ✨ Возможности

### 🔗 Интеграция с WooCommerce
- ✅ Подключение к WordPress/WooCommerce через REST API v3
- ✅ Тестирование соединения с API
- ✅ Безопасная авторизация с Consumer Key/Secret

### 📦 Управление товарами
- ✅ Загрузка всех товаров с сайта
- ✅ Создание новых товаров (простые и вариативные)
- ✅ Редактирование существующих товаров
- ✅ Удаление товаров
- ✅ Поиск и фильтрация товаров

### 📊 Работа с данными
- ✅ **Авто-определение формата CSV** (WooCommerce/простой)
- ✅ **Импорт WooCommerce CSV** с поддержкой вариаций
- ✅ **Экспорт в WooCommerce формат** (128 колонок)
- ✅ Импорт/экспорт простого CSV формата
- ✅ Валидация данных при импорте
- ✅ Управление атрибутами и категориями

### 🎨 Удобный интерфейс
- ✅ Современный GUI на CustomTkinter
- ✅ Табличное отображение товаров
- ✅ Диалоговые окна для редактирования
- ✅ Прогресс-бары и статус-бар

## 🚀 Быстрый старт

### 1. Установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/wc_product-manager.git
cd wc_product-manager

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка WooCommerce API

В админке WordPress:
1. Перейдите в **WooCommerce → Настройки → Дополнительно → REST API**
2. Создайте новый ключ с правами **Read/Write**
3. Скопируйте **Consumer Key** и **Consumer Secret**
4. Убедитесь, что включены "красивые ссылки" (Permalinks)

### 3. Запуск приложения

```bash
python main.py
```

### 4. Подключение к API

1. В поле "URL сайта" введите адрес вашего сайта (например: `https://your-site.com`)
2. Нажмите **"Подключиться"**
3. Нажмите **"Тест соединения"** для проверки
4. При успешном подключении нажмите **"Загрузить товары"**

## 📁 Структура проекта

```
wc_product-manager/
│
├── main.py                     # Главный файл запуска
├── main_gui.py                 # Основной GUI интерфейс
├── product_dialog.py           # Диалог редактирования товаров
├── woocommerce_manager.py      # Менеджер WooCommerce API
├── product_models.py           # Модели данных товаров
├── csv_manager.py              # Менеджер CSV импорт/экспорт
├── config.py                   # Конфигурация приложения
├── requirements.txt            # Зависимости Python
├── .gitignore                  # Исключения Git
├── README.md                   # Документация
│
├── logs/                       # Папка логов (создается автоматически)
│   └── app.log
│
└── keys.txt                    # API ключи (исключен из Git)
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
WC_SITE_URL=https://your-site.com
WC_CONSUMER_KEY=ck_your_consumer_key_here
WC_CONSUMER_SECRET=cs_your_consumer_secret_here
```

### Основные настройки в `config.py`

```python
# API настройки
API_VERSION = 'wc/v3'
PRODUCTS_PER_PAGE = 100
REQUEST_TIMEOUT = 30
```

## 📝 Использование

### Работа с товарами

#### Создание товара
1. Нажмите **"Добавить товар"**
2. Заполните обязательные поля:
   - Название товара
   - SKU (опционально)
   - Тип товара (simple/variable)
   - Цена
3. Добавьте описание, категории, изображения
4. Нажмите **"Сохранить"**

#### Редактирование товара
1. Выберите товар в таблице
2. Нажмите **"Редактировать"** или дважды щелкните по товару
3. Внесите изменения
4. Нажмите **"Сохранить"**

#### Импорт из CSV

**Авто-определение формата:**
1. Выберите **Файл → Импорт → Авто-определение формата**
2. Выберите CSV файл (WooCommerce или простой)
3. Приложение автоматически определит и обработает формат

**WooCommerce CSV:**
- Поддержка **128 колонок** WooCommerce
- **Вариативные товары** с атрибутами
- **Мета-данные** и SEO поля
- **Полная совместимость** с экспортом WooCommerce

**Простой CSV:**
```csv
name,type,sku,regular_price,description,status
"Тестовый товар","simple","TEST123","1999.99","Описание товара","publish"
```

#### Экспорт в CSV

**WooCommerce формат:**
1. Выберите **Файл → Экспорт → WooCommerce CSV**
2. Получите файл совместимый с WooCommerce импортом

**Простой формат:**
1. Выберите **Файл → Экспорт → Простой CSV**
2. Получите упрощенный файл для других систем

### Форматы CSV файлов

#### 🛒 WooCommerce CSV (полный формат)
**128 колонок включая:**
- `ID`, `Тип`, `Артикул`, `Имя`, `Базовая цена`
- `Описание`, `Краткое описание`, `Категории`
- `Изображения`, `Вес (г)`, `Размеры`
- `Название атрибута 1-21`, `Значения атрибутов 1-21`
- `Мета: _yoast_wpseo_*` (SEO поля)
- `Вариации товаров` и многое другое

#### 📄 Простой CSV (базовый формат)
**Обязательные колонки:**
- `name` - название товара
- `type` - тип товара (simple, variable, grouped, external)
- `sku` - артикул
- `regular_price` - обычная цена
- `description` - описание
- `status` - статус (publish, draft, private)

**Дополнительные колонки:**
- `sale_price` - цена со скидкой
- `short_description` - краткое описание
- `stock_quantity` - количество на складе
- `weight` - вес товара
- `categories` - категории (JSON формат)
- `images` - изображения (JSON формат)
- `attributes` - атрибуты (JSON формат)
- `meta_data` - мета-данные (JSON формат)

## 🛠 Разработка

### Требования к системе
- Python 3.8+
- Windows/macOS/Linux
- Интернет соединение для работы с API

### Зависимости
```txt
woocommerce>=3.0.0    # WooCommerce API клиент
customtkinter>=5.2.0  # Современный GUI
pandas>=2.0.0         # Работа с данными
requests>=2.31.0      # HTTP запросы
python-dotenv>=1.0.0  # Переменные окружения
Pillow>=10.0.0        # Работа с изображениями
```

### Архитектура

#### Основные компоненты:

1. **WooCommerceManager** - Управление API запросами
2. **ProductManagerGUI** - Главное окно приложения
3. **ProductDialog** - Диалог редактирования товаров
4. **Product, ProductCategory, ProductImage** - Модели данных
5. **CSVManager** - Импорт/экспорт CSV

#### Паттерны:
- **MVC** - Разделение логики и представления
- **Observer** - Обновление GUI при изменениях
- **Factory** - Создание объектов Product из API данных

### Добавление новых функций

#### Пример добавления нового поля товара:

1. Обновите модель `Product` в `product_models.py`:
```python
@dataclass
class Product:
    # ... существующие поля ...
    new_field: str = ""
```

2. Добавьте поле в GUI (`product_dialog.py`):
```python
def setup_main_tab(self):
    # ... существующие поля ...
    self.new_field_entry = ctk.CTkEntry(frame, placeholder_text="Новое поле")
```

3. Обновите методы сохранения и загрузки данных

## 🔍 Устранение проблем

### Частые ошибки

#### Ошибка подключения к API
```
Ошибка: HTTP 401 - Unauthorized
```
**Решение:** Проверьте правильность Consumer Key и Secret

#### Ошибка SSL сертификата
```
SSL Error: certificate verify failed
```
**Решение:** Убедитесь, что сайт использует действительный SSL сертификат

#### Ошибка импорта зависимостей
```
ModuleNotFoundError: No module named 'customtkinter'
```
**Решение:** Переустановите зависимости:
```bash
pip install -r requirements.txt
```

### Логи

Все логи сохраняются в файл `logs/app.log`. Используйте их для диагностики проблем:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Информационное сообщение")
logger.error("Сообщение об ошибке")
```

## 📞 Поддержка

- **Документация WooCommerce API:** https://woocommerce.github.io/woocommerce-rest-api-docs/
- **CustomTkinter документация:** https://customtkinter.tomschimansky.com/
- **Создание Issues:** [GitHub Issues](https://github.com/your-username/wc_product-manager/issues)

## 📈 Планы развития

- [ ] Поддержка вариативных товаров с атрибутами
- [ ] Массовые операции с товарами
- [ ] Работа с заказами и клиентами
- [ ] Синхронизация с внешними системами
- [ ] Планировщик задач
- [ ] Уведомления о низких остатках
- [ ] Аналитика и отчеты
- [ ] Мобильная версия

## 🤝 Участие в разработке

1. Сделайте Fork репозитория
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте ветку (`git push origin feature/AmazingFeature`)
5. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле `LICENSE`.

## 👨‍💻 Автор

**Ваше имя**
- GitHub: [@your-username](https://github.com/your-username)
- Email: your.email@example.com

---

**Дата последнего обновления:** Январь 2024

*Приложение разработано для управления интернет-магазинами на WordPress + WooCommerce* 