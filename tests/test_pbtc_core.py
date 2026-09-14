"""
Testes unitários para as regras de negócio de cálculo de PBTC e tolerâncias CONTRAN.
"""

import unittest
import sys
from pathlib import Path

# Adiciona diretório pai ao sys.path para importação
sys.path.insert(0, str(Path(__file__).parent.parent))

from pbtc_core import calcular_pbtc, calcular_pesagem_por_eixos, gerar_ticket_pesagem_texto
from vehicles_db import VEHICLES_DATABASE


class TestPBTCCore(unittest.TestCase):

    def test_toco_conforme(self):
        """Toco limite 16.000 kg. Tara 6.000 kg + Carga 9.500 kg = 15.500 kg -> CONFORME."""
        res = calcular_pbtc(tara_kg=6000, carga_liquida_kg=9500, codigo_veiculo="TOCO_4X2")
        self.assertEqual(res.status_codigo, "OK")
        self.assertEqual(res.pbtc_aferido_kg, 15500)
        self.assertEqual(res.limite_legal_kg, 16000)
        self.assertEqual(res.tolerancia_5pct_kg, 800)
        self.assertEqual(res.limite_balanca_kg, 16800)
        self.assertEqual(res.saldo_carga_disponivel_kg, 500)
        self.assertEqual(res.excesso_sobre_legal_kg, 0)
        self.assertEqual(res.transbordo_obrigatorio_kg, 0)

    def test_carreta_ls_tolerancia(self):
        """Carreta LS limite 45.000 kg. Tolerância 5% = 2.250 kg (Teto 47.250 kg).
        Tara 15.000 kg + Carga 31.000 kg = 46.000 kg -> ALERTA (Tolerância)."""
        res = calcular_pbtc(tara_kg=15000, carga_liquida_kg=31000, codigo_veiculo="CARRETA_LS_6E")
        self.assertEqual(res.status_codigo, "ALERTA")
        self.assertEqual(res.pbtc_aferido_kg, 46000)
        self.assertEqual(res.limite_legal_kg, 45000)
        self.assertEqual(res.tolerancia_5pct_kg, 2250)
        self.assertEqual(res.limite_balanca_kg, 47250)
        self.assertEqual(res.excesso_sobre_legal_kg, 1000)
        self.assertEqual(res.transbordo_obrigatorio_kg, 0)

    def test_rodotrem_excesso_transbordo(self):
        """Rodotrem 9 eixos limite 74.000 kg. Tolerância 5% = 3.700 kg (Teto 77.700 kg).
        Tara 22.000 kg + Carga 57.000 kg = 79.000 kg -> EXCESSO.
        Transbordo obrigatório: 79.000 - 77.700 = 1.300 kg."""
        res = calcular_pbtc(tara_kg=22000, carga_liquida_kg=57000, codigo_veiculo="RODOTREM_9E")
        self.assertEqual(res.status_codigo, "EXCESSO")
        self.assertEqual(res.pbtc_aferido_kg, 79000)
        self.assertEqual(res.limite_legal_kg, 74000)
        self.assertEqual(res.tolerancia_5pct_kg, 3700)
        self.assertEqual(res.limite_balanca_kg, 77700)
        self.assertEqual(res.excesso_sobre_legal_kg, 5000)
        self.assertEqual(res.excesso_sobre_tolerancia_kg, 1300)
        self.assertEqual(res.transbordo_obrigatorio_kg, 1300)

    def test_vanderleia_capacidade_util(self):
        """Vanderléia 53.000 kg. Tara 16.000 kg. Capacidade útil = 37.000 kg."""
        res = calcular_pbtc(tara_kg=16000, carga_liquida_kg=0, codigo_veiculo="VANDERLEIA_6E")
        self.assertEqual(res.capacidade_util_maxima_kg, 37000)
        self.assertEqual(res.limite_legal_kg, 53000)

    def test_veiculo_personalizado(self):
        """Veículo personalizado com limite manual de 60.000 kg."""
        res = calcular_pbtc(tara_kg=18000, carga_liquida_kg=40000, codigo_veiculo="PERSONALIZADO", limite_manual=60000)
        self.assertEqual(res.limite_legal_kg, 60000)
        self.assertEqual(res.tolerancia_5pct_kg, 3000)
        self.assertEqual(res.status_codigo, "OK")

    def test_eixos_tolerancia_12_5(self):
        """Teste de tolerância de eixos (12,5% Lei 14.229/2021)."""
        # Truck 6x2: Eixo 1 simples 6.000 kg (+12.5% = 6.750 kg). Tandem duplo 17.000 kg (+12.5% = 19.125 kg)
        pesos = [6500.0, 19500.0]  # Eixo 1 dentro da tolerância, Eixo 2 com excesso
        res_eixos = calcular_pesagem_por_eixos("TRUCK_6X2", pesos)
        self.assertEqual(len(res_eixos), 2)
        # Eixo 1: 6500 <= 6750 -> ALERTA
        self.assertEqual(res_eixos[0].status_codigo, "ALERTA")
        # Eixo 2: 19500 > 19125 -> EXCESSO
        self.assertEqual(res_eixos[1].status_codigo, "EXCESSO")
        self.assertAlmostEqual(res_eixos[1].excesso_kg, 375.0)

    def test_gerar_ticket(self):
        """Verifica se o ticket de pesagem é gerado como string válida."""
        res = calcular_pbtc(
            tara_kg=15000,
            carga_liquida_kg=30000,
            codigo_veiculo="CARRETA_LS_6E",
            placa_cavalo="ABC-1234",
            placa_carreta="XYZ-9876",
            romaneio="ROM-2026-001",
            motorista="João da Silva",
            produto="Soja em Grãos"
        )
        ticket = gerar_ticket_pesagem_texto(res)
        self.assertIn("TICKET DE CONFERÊNCIA DE PESAGEM", ticket)
        self.assertIn("ABC-1234", ticket)
        self.assertIn("Soja em Grãos", ticket)
        self.assertIn("45.000 kg", ticket)


if __name__ == "__main__":
    unittest.main()
