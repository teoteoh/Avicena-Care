@echo off
echo.
echo Iniciando Avicena Care - Sistema de Triagem...
echo.

REM Navegar para o diretório do projeto
cd /d "c:\Users\serei\OneDrive\Área de Trabalho\Avicena Care"

REM (Opcional) Desabilitar telemetria do Streamlit
set STREAMLIT_TELEMETRY_URL=

echo App rodando em: http://localhost:8501
echo Para parar o app, pressione Ctrl+C
echo.

REM Executar apenas o app principal
"C:/Users/serei/AppData/Local/Programs/Python/Python313/python.exe" -m streamlit run app_triagem.py --server.port=8501 --server.headless=true

pause
