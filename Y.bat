@echo off
:: O comando abaixo muda o foco para a pasta onde este arquivo .bat está
cd /d "%~dp0"

:: Feedback visual
echo Iniciando sua aplicacao Streamlit...
echo.

:: Roda o streamlit (substitua 'seu_script.py' pelo nome do seu arquivo)
streamlit run app.py
