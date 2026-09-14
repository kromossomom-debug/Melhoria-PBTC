"""
PBTC Express - Modo Balança Rápida via Terminal (Zero Delay / Máxima Agilidade).
Ideal para conferências instantâneas pelo teclado numérico da balança sem impacto de performance.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pbtc_core import calcular_pbtc
from vehicles_db import VEHICLES_DATABASE

OPCOES = {
    "1": ("CARRETA_LS_6E", "Carreta LS 3E (45,0t)"),
    "2": ("VANDERLEIA_6E", "Vanderléia 3E Distanciados (53,0t)"),
    "3": ("BITREM_7E", "Bitrem 7 Eixos (57,0t)"),
    "4": ("RODOTREM_9E", "Rodotrem 9 Eixos (74,0t)"),
    "5": ("CARRETA_4_EIXOS", "Carreta 4 Eixos (58,5t)"),
    "6": ("BITRUCK_8X2", "Bitruck 8x2 (29,0t)"),
    "7": ("TRUCK_6X2", "Truck 6x2 (23,0t)"),
    "8": ("TOCO_4X2", "Toco 4x2 (16,0t)"),
    "9": ("PERSONALIZADO", "Personalizado (Limite Manual)")
}

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    while True:
        limpar_tela()
        print("=" * 60)
        print("       🚛 PBTC EXPRESS - BALANÇA RÁPIDA (CONTRAN)")
        print("               MODO OPERAÇÃO DIRETA")
        print("=" * 60)
        print(" [1] Carreta LS (45t)       [5] Carreta 4 Eixos (58,5t)")
        print(" [2] Vanderléia (53t)       [6] Bitruck 8x2 (29t)")
        print(" [3] Bitrem 7 Eixos (57t)   [7] Truck 6x2 (23t)")
        print(" [4] Rodotrem 9 Eixos (74t) [8] Toco 4x2 (16t)")
        print(" [9] Personalizado (AET)    [0] Sair")
        print("-" * 60)

        escolha = input("Selecione o tipo do caminhão [Padrão: 1]: ").strip()
        if escolha == "0":
            print("\nEncerrando balança expressa...")
            break
        if not escolha:
            escolha = "1"

        cod_veiculo, nome_veiculo = OPCOES.get(escolha, ("CARRETA_LS_6E", "Carreta LS 3E (45,0t)"))
        veic_info = VEHICLES_DATABASE.get(cod_veiculo, {})
        tara_ref = veic_info.get("tara_media_referencia", 15500)

        limite_manual = None
        if cod_veiculo == "PERSONALIZADO":
            try:
                limite_manual = float(input("Digite o Limite Legal PBTC em kg (Ex: 50000): ").strip())
            except ValueError:
                limite_manual = 45000.0

        print(f"\nVeículo Selecionado: {nome_veiculo}")

        # Entrada de Tara
        tara_str = input(f"Tara do caminhão em kg [Enter assume {tara_ref:,.0f} kg]: ").strip()
        try:
            tara = float(tara_str) if tara_str else float(tara_ref)
        except ValueError:
            tara = float(tara_ref)

        # Entrada de Peso Bruto
        bruto_str = input("Peso Bruto aferido na balança em kg: ").strip()
        try:
            bruto = float(bruto_str) if bruto_str else 0.0
        except ValueError:
            bruto = 0.0

        carga_liquida = max(0.0, bruto - tara)
        res = calcular_pbtc(
            tara_kg=tara,
            carga_liquida_kg=carga_liquida,
            codigo_veiculo=cod_veiculo,
            limite_manual=limite_manual
        )

        print("\n" + "=" * 60)
        print(f" RESULTADO DA PESAGEM ({res.veiculo_nome})")
        print("=" * 60)
        print(f" Tara:          {res.tara_kg:>10,.0f} kg".replace(",", "."))
        print(f" Carga Líquida: {res.carga_liquida_kg:>10,.0f} kg".replace(",", "."))
        print(f" PBTC TOTAL:    {res.pbtc_aferido_kg:>10,.0f} kg  ({res.pbtc_aferido_kg/1000:.2f} t)".replace(",", "."))
        print("-" * 60)
        print(f" Limite CONTRAN:    {res.limite_legal_kg:>10,.0f} kg".replace(",", "."))
        print(f" Teto Balança (+5%):{res.limite_balanca_kg:>10,.0f} kg".replace(",", "."))
        print("-" * 60)

        if res.status_codigo == "OK":
            print(f" >>> STATUS: [🟢 LIBERADO / CONFORME]")
            print(f" >>> Saldo disponível para carga: +{res.saldo_carga_disponivel_kg:,.0f} kg".replace(",", "."))
            print(f" >>> {res.mensagem}")
        elif res.status_codigo == "ALERTA":
            print(f" >>> STATUS: [🟡 TOLERÂNCIA DE BALANÇA (5%)]")
            print(f" >>> Liberado sem autuação, porém acima do limite legal (+{res.excesso_sobre_legal_kg:,.0f} kg)".replace(",", "."))
            print(f" >>> {res.mensagem}")
        else:
            print(f" >>> STATUS: [🔴 BLOQUEADO: EXCESSO DE PESO!]")
            print(f" >>> TRANSBORDO OBRIGATÓRIO: {res.transbordo_obrigatorio_kg:,.0f} kg".replace(",", "."))
            print(f" >>> {res.mensagem}")

        print("=" * 60)
        prox = input("\n[Enter] para próximo caminhão ou '0' para sair: ").strip()
        if prox == "0":
            break


if __name__ == "__main__":
    main()
