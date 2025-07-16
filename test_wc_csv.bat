@echo off
chcp 65001 >nul
echo ========================================
echo  Тестирование WooCommerce CSV Import
echo ========================================
echo.

echo Активация виртуального окружения...
call venv\Scripts\activate.bat

echo.
echo Запуск тестирования WooCommerce CSV импорта...
python test_woocommerce_import.py

echo.
echo ========================================
echo Тестирование завершено!
echo ========================================
echo.
pause 