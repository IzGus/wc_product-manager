# 💻 Python команды WooCommerce Product Manager

## 🚀 Основные команды

### Запуск приложения
```bash
# Простой запуск
python main.py
```

### Управление зависимостями
```bash
# Установка всех зависимостей
pip install -r requirements.txt

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Проверка установленных библиотек
pip list | grep -E "customtkinter|woocommerce|pandas"

# Обновление pip
python -m pip install --upgrade pip
```

### Работа с Git
```bash
# Проверка статуса
git status

# Добавление всех изменений
git add .

# Создание коммита
git commit -m "Описание изменений"

# Отправка на GitHub
git push origin main

# Получение обновлений
git pull origin main
```

## 🔍 Диагностика и отладка

### Проверка Python окружения
```bash
# Версия Python
python --version

# Путь к Python
where python

# Установленные пакеты
pip list

# Информация о пакете
pip show customtkinter
```

### Тестирование зависимостей
```bash
# Проверка CustomTkinter
python -c "import customtkinter; print('✅ CustomTkinter работает!')"

# Проверка WooCommerce API
python -c "import woocommerce; print('✅ WooCommerce API работает!')"

# Проверка Pandas
python -c "import pandas; print('✅ Pandas работает!')"

# Проверка всех зависимостей
python -c "
import customtkinter, woocommerce, pandas, requests, PIL
print('✅ Все зависимости работают!')
"
```

## 📝 Утилиты разработки

### Работа с логами
```bash
# Просмотр логов (Windows)
type logs\app.log

# Просмотр логов (Linux/macOS)
cat logs/app.log

# Очистка логов
echo "" > logs/app.log
```

### Запуск с отладкой
```bash
# Запуск с подробными логами
python -u main.py

# Запуск с профилированием времени
python -m cProfile main.py
```

## 🧪 Тестирование функций

### Проверка подключения к API
```python
# Создайте файл test_connection.py
python -c "
from woocommerce import API

wcapi = API(
    url='https://your-site.com',
    consumer_key='ck_your_key',
    consumer_secret='cs_your_secret',
    version='wc/v3'
)

try:
    products = wcapi.get('products')
    print(f'✅ Подключение успешно! Найдено товаров: {len(products.json())}')
except Exception as e:
    print(f'❌ Ошибка подключения: {e}')
"
```

### Тестирование GUI
```python
# Тест GUI без полного запуска
python -c "
import customtkinter as ctk
app = ctk.CTk()
app.title('Тест GUI')
app.geometry('300x200')
label = ctk.CTkLabel(app, text='GUI работает!')
label.pack(pady=50)
print('✅ GUI тест готов. Закройте окно чтобы продолжить.')
app.mainloop()
"
```

## 📊 Работа с данными

### CSV операции
```bash
# Проверка CSV файла
python -c "
import pandas as pd
df = pd.read_csv('example_products.csv')
print(f'Товаров в файле: {len(df)}')
print(f'Колонки: {list(df.columns)}')
"

# Создание тестового CSV
python -c "
import pandas as pd
data = {
    'name': ['Тестовый товар 1', 'Тестовый товар 2'],
    'type': ['simple', 'simple'],
    'sku': ['TEST001', 'TEST002'],
    'regular_price': [100.00, 200.00],
    'status': ['publish', 'publish']
}
df = pd.DataFrame(data)
df.to_csv('test_products.csv', index=False)
print('✅ Создан test_products.csv')
"
```

## 🛠 Поиск и устранение неисправностей

### Очистка кэша Python
```bash
# Удаление .pyc файлов
find . -name "*.pyc" -delete     # Linux/macOS
# Или для Windows PowerShell:
Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item
```

### Переустановка зависимостей
```bash
# Полная переустановка
pip uninstall -y customtkinter woocommerce pandas requests pillow python-dotenv
pip install -r requirements.txt
```

### Создание отчета об ошибке
```bash
# Сбор информации о системе
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'Платформа: {platform.platform()}')
print(f'Архитектура: {platform.architecture()}')

import pkg_resources
for package in ['customtkinter', 'woocommerce', 'pandas']:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f'{package}: {version}')
    except:
        print(f'{package}: НЕ УСТАНОВЛЕН')
"
```

## 🚀 Продуктивные команды

### Быстрая проверка перед запуском
```bash
# Проверка всего окружения
python -c "
print('🔍 Проверка окружения...')
try:
    import customtkinter, woocommerce, pandas
    print('✅ Все зависимости на месте')
    print('🚀 Можно запускать: python main.py')
except ImportError as e:
    print(f'❌ Отсутствует: {e}')
    print('📦 Установите: pip install -r requirements.txt')
"
```

### Мониторинг ресурсов
```bash
# Использование памяти
python -c "
import psutil, os
process = psutil.Process(os.getpid())
print(f'Память: {process.memory_info().rss / 1024 / 1024:.1f} MB')
print(f'CPU: {process.cpu_percent()}%')
"
```

---

**💡 Совет:** Сохраните эти команды в файл для быстрого доступа или создайте alias в вашей оболочке.

**🔗 Больше команд:** Изучите документацию каждой библиотеки для расширенных возможностей. 