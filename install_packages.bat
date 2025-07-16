@echo off
echo 📦 Установка пакетов в виртуальное окружение...
echo.

REM Проверяем наличие виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Виртуальное окружение не найдено!
    echo 📦 Сначала запустите setup_venv.bat
    pause
    exit /b 1
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Показываем текущую версию Python
echo ✅ Используется Python:
python --version
echo.

REM Обновляем pip
echo 🔄 Обновление pip...
python -m pip install --upgrade pip

REM Устанавливаем каждый пакет отдельно
echo.
echo 📦 Установка основных пакетов...

echo [1/6] Установка woocommerce...
pip install woocommerce>=3.0.0

echo [2/6] Установка customtkinter...
pip install customtkinter>=5.2.0

echo [3/6] Установка pandas...
pip install pandas>=2.0.0

echo [4/6] Установка requests...
pip install requests>=2.31.0

echo [5/6] Установка python-dotenv...
pip install python-dotenv>=1.0.0

echo [6/6] Установка Pillow...
pip install Pillow>=10.0.0

echo.
echo ✅ Все пакеты установлены!
echo.
echo 📋 Список установленных пакетов:
pip list

echo.
echo 🎉 Готово! Теперь можно запустить приложение командой:
echo    run_app.bat
echo.
pause 