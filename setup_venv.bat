@echo off
echo 🚀 Настройка виртуального окружения для WooCommerce Product Manager...
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+ и повторите.
    pause
    exit /b 1
)

echo ✅ Python найден
python --version

REM Создаем виртуальное окружение если его нет
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
) else (
    echo ✅ Виртуальное окружение уже существует
)

REM Активируем виртуальное окружение
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Обновляем pip
echo 📦 Обновление pip...
python -m pip install --upgrade pip

REM Устанавливаем зависимости
echo 📦 Установка зависимостей из requirements.txt...
pip install -r requirements.txt

echo.
echo 🎉 Настройка завершена!
echo.
echo 📝 Для запуска приложения используйте:
echo    run_app.bat
echo.
echo 🔧 Для ручной активации окружения:
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
pause 