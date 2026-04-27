@echo off
REM Deploy: faz commit + push para GitHub. Streamlit Cloud reimplanta sozinho.
REM Uso: deploy.bat "mensagem do commit"

setlocal

if "%~1"=="" (
    echo Uso: deploy.bat "mensagem do commit"
    echo Exemplo: deploy.bat "ajuste tooltip da etapa de zonas"
    exit /b 1
)

echo.
echo === Status atual ===
git status --short
echo.

set /p CONFIRMA="Continuar com o commit e push? (s/N): "
if /i not "%CONFIRMA%"=="s" (
    echo Cancelado.
    exit /b 0
)

git add .
git commit -m "%~1"
git push

echo.
echo === Deploy enviado ===
echo Streamlit Cloud reimplanta automaticamente em ~1-2 minutos.
echo Acompanhe em: https://share.streamlit.io
echo.

endlocal
