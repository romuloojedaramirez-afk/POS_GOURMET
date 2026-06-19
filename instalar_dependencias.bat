@echo off
title GourmetPOS - Instalando Dependencias
cd /d "%~dp0"

echo.
echo ================================================
echo   GourmetPOS ERP - INSTALADOR DE LIBRERIAS
echo ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado.
    echo Instala Python desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado:
python --version
echo.

echo [1/10] FastAPI + Uvicorn (Servidor web)...
pip install fastapi "uvicorn[standard]" python-multipart --quiet
echo OK

echo [2/10] SQLAlchemy + Alembic (Base de datos)...
pip install sqlalchemy alembic --quiet
echo OK

echo [3/10] Pydantic + python-dotenv (Validacion)...
pip install pydantic pydantic-settings python-dotenv --quiet
echo OK

echo [4/10] HTTPX + Requests + Websockets (HTTP)...
pip install httpx requests websockets --quiet
echo OK

echo [5/10] Google Generative AI - Gemini (10 Prompts IA)...
pip install google-generativeai --quiet
echo OK

echo [6/10] Pandas + OpenPyXL (Reportes Excel)...
pip install pandas openpyxl xlsxwriter --quiet
echo OK

echo [7/10] Aiofiles + UJson (Utilidades)...
pip install aiofiles ujson python-dateutil pytz --quiet
echo OK

echo [8/10] Email-validator...
pip install email-validator --quiet
echo OK

echo [9/10] Passlib + Python-jose (Seguridad)...
pip install "passlib[bcrypt]" "python-jose[cryptography]" --quiet
echo OK

echo [10/10] Verificando instalacion...
python -c "import fastapi, sqlalchemy, pandas, httpx; print('Todas las librerias OK!')"

echo.
echo ================================================
echo   INSTALACION COMPLETADA
echo   Ahora ejecuta: start.bat
echo ================================================
echo.
pause
