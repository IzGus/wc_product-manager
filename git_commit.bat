@echo off
chcp 65001 >nul
echo ========================================
echo  Git Operations - Safe Mode
echo ========================================
echo.

echo Текущий статус репозитория:
git status

echo.
echo Добавление всех изменений...
git add .

echo.
echo Текущие изменения для коммита:
git status

echo.
set /p commit_message="Введите сообщение коммита: "

echo.
echo Создание коммита...
git commit -m "%commit_message%"

echo.
echo Отправка изменений на GitHub...
git push origin main

echo.
echo ========================================
echo Git операции завершены!
echo ========================================
echo.
pause 