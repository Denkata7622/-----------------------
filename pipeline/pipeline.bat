@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Пълен път до реалния Python (не зависи от PATH)
set "PY=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"

:: Проверка, че Python съществува
if not exist "%PY%" (
    echo.
    echo [ГРЕШКА] Python не е намерен на:
    echo   %PY%
    echo.
    echo Инсталирай Python от https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Проверка, че requests е инсталиран
"%PY%" -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [setup] Инсталирам requests...
    "%PY%" -m pip install --quiet requests
)

:: Проверка, че pdfplumber е инсталиран (за gap worker-а)
"%PY%" -c "import pdfplumber" >nul 2>&1
if errorlevel 1 (
    echo [setup] Инсталирам pdfplumber за gap worker-а...
    "%PY%" -m pip install --quiet pdfplumber pypdf
)

:: Проверка, че index.html съществува
if not exist "..\index.html" (
    echo.
    echo [ГРЕШКА] Не намирам ..\index.html
    echo Очаквам index.html да е в родителската папка на pipeline\
    echo.
    pause
    exit /b 1
)

:: Проверка, че gap_worker.py съществува
if not exist "gap_worker.py" (
    echo.
    echo [ГРЕШКА] Не намирам gap_worker.py
    echo Очаквам го в същата папка като pipeline.bat
    echo.
    pause
    exit /b 1
)

:: ═══════════════════════════════════════════════
::   ЗАБРАНА НА SLEEP / HIBERNATE (временно)
:: ═══════════════════════════════════════════════
echo [power] Изключвам sleep и hibernate за времетраенето на pipeline-а...
powercfg /change standby-timeout-ac 0 >nul 2>&1
powercfg /change standby-timeout-dc 0 >nul 2>&1
powercfg /change hibernate-timeout-ac 0 >nul 2>&1
powercfg /change hibernate-timeout-dc 0 >nul 2>&1
echo [power] Готово. Ще се възстановят твоите настройки след края.
echo.

:: ═══════════════════════════════════════════════
::   PIPELINE
:: ═══════════════════════════════════════════════
echo ═══════════════════════════════════════════════
echo   OLYMPIAD PIPELINE — стартиране
echo ═══════════════════════════════════════════════
echo   Python:  %PY%
echo   HTML:    ..\index.html
echo   Спри:    Ctrl+C
echo ═══════════════════════════════════════════════
echo.

:: ─────────────────────────────────────────────
:: 1. Стартирай gap worker във фон (minimized)
:: ─────────────────────────────────────────────
echo [gap_worker] Стартирам PDF gap анализатор във фон...
start "pdf_gap_worker" /MIN "%PY%" gap_worker.py
timeout /t 3 /nobreak >nul

:: ─────────────────────────────────────────────
:: 2. Стартирай main pipeline във foreground
:: ─────────────────────────────────────────────
echo [pipeline] Работя... (Ctrl+C за спиране на всичко)
echo.
"%PY%" pipeline.py --html "..\index.html"

:: ═══════════════════════════════════════════════
::   CLEANUP
:: ═══════════════════════════════════════════════

:: Спри фоновия gap worker
echo.
echo [gap_worker] Спирам фоновия worker...
taskkill /F /FI "WINDOWTITLE eq pdf_gap_worker*" >nul 2>&1

:: ═══════════════════════════════════════════════
::   ВЪЗСТАНОВЯВАНЕ НА ТВОИТЕ НАСТРОЙКИ
:: ═══════════════════════════════════════════════
::   Sleep:     AC=0 (никога) / DC=600 (10 мин)
::   Hibernate: AC=10800 (180 мин) / DC=10800 (180 мин)
::   Display:   AC=300 (5 мин) / DC=180 (3 мин)
:: ═══════════════════════════════════════════════
echo.
echo [power] Възстановявам sleep...
powercfg /change standby-timeout-ac 0     >nul 2>&1
powercfg /change standby-timeout-dc 10    >nul 2>&1
powercfg /change hibernate-timeout-ac 180 >nul 2>&1
powercfg /change hibernate-timeout-dc 180 >nul 2>&1
echo [power] Готово
echo.

echo Pipeline спрян.
pause