# 🛠 Техническое задание: WooCommerce Product Manager через REST API

## 🎯 Цели проекта

- Интеграция с WordPress + WooCommerce через REST API.
- Возможность в приложении:
  - создавать новые товары (простые и вариативные);
  - выгружать товары с сайта;
  - редактировать информацию (включая атрибуты и мета-поля);
  - сохранять изменения обратно на сайт;
  - удалять товары при необходимости.

## 🔐 Настройка API

1. В админке WooCommerce: *WooCommerce → Настройки → Дополнительно → REST API* → создать ключ с правами **Read/Write**.
2. Включить «красивые ссылки» (*Permalinks*).
3. Получить **Consumer Key / Secret** для авторизации.

## 🧱 Технологии

- Язык: Python 3.x
- Библиотека API: `woocommerce`
  - Установка: `pip install woocommerce`
- REST API: версия `wc/v3`
- GUI: `customtkinter` или `PyQt`
- CSV/JSON: `pandas` (для опционального CSV-импорта/экспорта)

## 🔗 Основные компоненты

### 1. Инициализация API

```python
from woocommerce import API

wcapi = API(
    url="https://your-site.com",
    consumer_key="ck_xxx",
    consumer_secret="cs_xxx",
    version="wc/v3"
)
```

### 2. Получение товаров (экспорт)

```python
products = []
page = 1
while True:
    batch = wcapi.get("products", params={"per_page": 100, "page": page}).json()
    if not batch:
        break
    products.extend(batch)
    page += 1
```

### 3. Создание товаров

#### Простые товары

```python
data = {
  "name": "Тестовый товар",
  "type": "simple",
  "regular_price": "1999.99",
  "sku": "TEST123",
  "description": "...",
  "categories": [{"id": 15}],
  "images": [{"src": "https://...jpg"}]
}
res = wcapi.post("products", data).json()
```

#### Вариативные товары

1. Создание родителя:

```python
data = {
  "name": "Футболка",
  "type": "variable",
  "attributes": [
    {"id": 5, "variation": True, "visible": True, "options": ["S","M","L"]}
  ]
}
parent = wcapi.post("products", data).json()
```

2. Добавление вариаций:

```python
for opt in ["S","M","L"]:
    wcapi.post(f"products/{parent['id']}/variations", {
      "regular_price": "1999.99",
      "attributes": [{"id": 5, "option": opt}]
    })
```

### 4. Обновление товаров

```python
res = wcapi.get("products", params={"sku": "TEST123"}).json()
product_id = res[0]["id"]
wcapi.put(f"products/{product_id}", {"regular_price": "2499.99"})
```

### 5. Удаление товаров

```python
wcapi.delete(f"products/{product_id}", params={"force": True})
```

## 🧰 Функциональность приложения

### A. GUI

- Настройка API (URL, ключи)
- Кнопки: Загрузить товары, Создать товар, Редактировать, Удалить, Сохранить изменения
- Таблица с товарами, фильтрами и редактируемыми полями
- Формы добавления: SKU, name, type, price, stock, категории, картинки, атрибуты, мета-поля

### B. Атрибуты и мета‑поля

- Attributes: id/name, visible, variation, options
- Meta_data: JSON‑массив полей {"key": ..., "value": ...}

### C. CSV‑импорт/экспорт (опционально)

- Чтение/запись через pandas
- Привязка к API‑операциям при сохранении

## 🛡 Валидация и безопасность

- Уникальность SKU
- Проверка атрибутов (должны существовать в системе)
- Авторизация только по HTTPS
- Ключи с правами Read/Write

## 🛠 Этапы реализации

| Этап | Описание                                                                 | Срок       |
|------|--------------------------------------------------------------------------|------------|
| 1    | Авторизация, настройка API, тестовые запросы GET/POST                    | 1 день     |
| 2    | GUI загрузки и отображения товаров                                       | 2 дня      |
| 3    | Добавление, обновление, удаление товаров через API                       | 2–3 дня    |
| 4    | Поддержка вариативных товаров                                           | 2 дня      |
| 5    | Атрибуты и мета‑поля в GUI и JSON                                        | 2 дня      |
| 6    | CSV‑модуль (импорт/экспорт), интеграция с GUI                           | 1–2 дня    |
| 7    | Валидация, документация                                                 | 1 день     |

## ✅ Критерии приёмки

- Рабочее соединение с WooCommerce через REST API
- GUI: загрузка, редактирование, создание, удаление товаров
- Поддержка вариативных товаров, атрибутов, мета‑данных
- Корректное создание и обновление товаров на сайте
- (Дополнительно) CSV-импорт/экспорт

## 📚 Ресурсы

- WooCommerce REST API: https://woocommerce.github.io/woocommerce-rest-api-docs/
- Python client: https://github.com/woocommerce/wc-api-python

| 2    | GUI загрузки и отображения товаров                                       | 2 дня      |
| 3    | Добавление, обновление, удаление товаров через API                       | 2–3 дня    |
| 4    | Поддержка вариативных товаров                                           | 2 дня      |
| 5    | Атрибуты и мета‑поля в GUI и JSON                                        | 2 дня      |
| 6    | CSV‑модуль (импорт/экспорт), интеграция с GUI                           | 1–2 дня    |
| 7    | Валидация, документация                                                | 1 день     |

## ✅ Критерии приёмки

- Рабочее соединение с WooCommerce через REST API
- GUI: загрузка, редактирование, создание, удаление товаров
- Поддержка вариативных товаров, атрибутов, мета‑данных
- Корректное создание и обновление товаров на сайте
- (Дополнительно) CSV-импорт/экспорт

## 📚 Полезные ссылки

- [WooCommerce REST API v3](https://woocommerce.github.io/woocommerce-rest-api-docs/)
- [Python WooCommerce API client](https://github.com/woocommerce/wc-api-python)
- [Создание вариаций через REST API](https://florianbrinkmann.com/en/creating-a-woocommerce-product-variation-rest-api-4526/)