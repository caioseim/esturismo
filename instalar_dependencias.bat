@echo off
echo =======================================
echo    ES Turismo - Instalador
echo =======================================
echo.
echo Instalando dependencias necessarias...
echo.
pip install flask flask-sqlalchemy gunicorn werkzeug
echo.
echo Instalacao concluida!
echo.
echo Para iniciar o sistema, clique em "iniciar.bat"
echo.
pause