@echo off
echo 🚀 Запуск WooCommerce Product Manager...
echo.

REM Проверяем наличие виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Виртуальное окружение не найдено!
    echo 📦 Сначала запустите setup_venv.bat для настройки
    pause
    exit /b 1
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Запускаем приложение
echo ✅ Запуск приложения в виртуальном окружении...
python main.py

echo.
echo 👋 Приложение завершено
pause 