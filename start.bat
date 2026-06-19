@echo off
title GourmetPOS ERP - Iniciando...
cd /d "%~dp0"

echo.
echo ================================================
echo   GourmetPOS ERP v2.0
echo   Backend FastAPI + Frontend + WhatsApp Bot
echo ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado.
    echo Instala Python desde https://python.org
    pause
    exit /b 1
)

if not exist ".env" (
    echo Creando archivo .env desde plantilla...
    copy ".env.example" ".env" >nul
)

echo Verificando dependencias...
pip install fastapi "uvicorn[standard]" sqlalchemy pydantic python-dotenv httpx aiofiles --quiet 2>nul

:: Detectar puerto libre
set PORT=8000
netstat -an | find "0.0.0.0:8000" >nul 2>&1
if not errorlevel 1 (
    set PORT=8001
    echo Puerto 8000 ocupado, usando 8001...
)

echo.
echo ------------------------------------------------
echo   Dashboard:  http://localhost:%PORT%
echo   POS:        http://localhost:%PORT%/pos.html
echo   Cocina:     http://localhost:%PORT%/cocina.html
echo   Reportes:   http://localhost:%PORT%/reportes.html
echo   WhatsApp:   http://localhost:%PORT%/whatsapp.html
echo   API Docs:   http://localhost:%PORT%/docs
echo ------------------------------------------------
echo.
echo Presiona Ctrl+C para detener
echo.

start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:%PORT%"

python -m uvicorn backend.main:app --host 0.0.0.0 --port %PORT% --reload

pause
