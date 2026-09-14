@echo off
chcp 65001 > nul
title PBTC Master - Balança Rápida
cls

:: Inicialização instantânea: verifica se as dependências já existem
python -c "import customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Primeira execucao] Instalando dependencias necessarias...
    python -m pip install -r requirements.txt --quiet --disable-pip-version-check
)

:: Inicia o programa imediatamente em segundo plano sem travar o terminal
start "" pythonw main.py
exit
