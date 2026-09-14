"""
Ponto de Entrada Principal do Sistema PBTC Master.
Executa a interface gráfica para cálculo e controle de PBTC de caminhões.
"""

import sys
import os

# Garante que o diretório base do projeto esteja no path de importação
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        import customtkinter
    except ImportError:
        print("[ERRO] A biblioteca 'customtkinter' não foi encontrada.")
        print("Por favor, instale as dependências executando:")
        print("    pip install -r requirements.txt")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    from ui.app_window import AppPBTC

    app = AppPBTC()
    app.run()


if __name__ == "__main__":
    main()
