"""
Base de Dados Técnica de Veículos de Carga (CONTRAN / Legislação Brasileira).
Resolução CONTRAN nº 882/2021, Lei nº 14.229/2021 e normas correlatas.
"""

from typing import Dict, List, Any

# Catálogo completo de configurações de veículos e seus limites legais em kg
VEHICLES_DATABASE: Dict[str, Dict[str, Any]] = {
    "TOCO_4X2": {
        "codigo": "TOCO_4X2",
        "nome": "Caminhão Toco (4x2)",
        "categoria": "Veículo Rígido",
        "eixos": 2,
        "pbtc_legal": 16000,  # 16,0 toneladas
        "requer_aet": False,
        "tara_media_referencia": 6000,
        "descricao": "Caminhão rígido de 2 eixos (1 dianteiro simples + 1 traseiro simples de tração).",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Dianteiro Direcional Simples)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixo 2 (Traseiro Tração Simples)", "limite_legal": 10000, "tipo": "simples_tracao"},
        ]
    },
    "TRUCK_6X2": {
        "codigo": "TRUCK_6X2",
        "nome": "Caminhão Truck (6x2 / 6x4)",
        "categoria": "Veículo Rígido",
        "eixos": 3,
        "pbtc_legal": 23000,  # 23,0 toneladas
        "requer_aet": False,
        "tara_media_referencia": 8500,
        "descricao": "Caminhão rígido de 3 eixos (1 dianteiro simples + tandem duplo traseiro).",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Dianteiro Direcional Simples)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Tandem Duplo Traseiro)", "limite_legal": 17000, "tipo": "tandem_duplo"},
        ]
    },
    "BITRUCK_8X2": {
        "codigo": "BITRUCK_8X2",
        "nome": "Caminhão Bitruck (8x2 / 8x4)",
        "categoria": "Veículo Rígido",
        "eixos": 4,
        "pbtc_legal": 29000,  # 29,0 toneladas
        "requer_aet": False,
        "tara_media_referencia": 11000,
        "descricao": "Caminhão rígido de 4 eixos (2 eixos direcionais dianteiros + tandem duplo traseiro).",
        "grupos_eixos": [
            {"nome": "Eixos 1 e 2 (Duplo Direcional Dianteiro)", "limite_legal": 12000, "tipo": "duplo_direcional"},
            {"nome": "Eixos 3 e 4 (Tandem Duplo Traseiro)", "limite_legal": 17000, "tipo": "tandem_duplo"},
        ]
    },
    "CARRETA_2E": {
        "codigo": "CARRETA_2E",
        "nome": "Cavalo 4x2 + Carreta 2 Eixos (4 eixos total)",
        "categoria": "Veículo Articulado",
        "eixos": 4,
        "pbtc_legal": 33000,  # 33,0 toneladas
        "requer_aet": False,
        "tara_media_referencia": 12500,
        "descricao": "Cavalo mecânico 4x2 (toco) acoplado a semirreboque de 2 eixos tandem.",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixo 2 (Cavalo - Tração Simples)", "limite_legal": 10000, "tipo": "simples_tracao"},
            {"nome": "Eixos 3 e 4 (Carreta - Tandem Duplo)", "limite_legal": 17000, "tipo": "tandem_duplo"},
        ]
    },
    "CARRETA_3E_5E": {
        "codigo": "CARRETA_3E_5E",
        "nome": "Cavalo 4x2 + Carreta 3 Eixos (5 eixos total)",
        "categoria": "Veículo Articulado",
        "eixos": 5,
        "pbtc_legal": 41500,  # 41,5 toneladas
        "requer_aet": False,
        "tara_media_referencia": 14000,
        "descricao": "Cavalo mecânico 4x2 acoplado a semirreboque de 3 eixos tandem juntos.",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixo 2 (Cavalo - Tração Simples)", "limite_legal": 10000, "tipo": "simples_tracao"},
            {"nome": "Eixos 3, 4 e 5 (Carreta - Tandem Triplo)", "limite_legal": 25500, "tipo": "tandem_triplo"},
        ]
    },
    "CARRETA_LS_6E": {
        "codigo": "CARRETA_LS_6E",
        "nome": "Carreta LS 3 Eixos Juntos (6 eixos total - 6x2/6x4)",
        "categoria": "Veículo Articulado",
        "eixos": 6,
        "pbtc_legal": 45000,  # 45,0 toneladas (41,5t se cavalo 4x2; 45t com cavalo 6x2)
        "requer_aet": False,
        "tara_media_referencia": 15500,
        "descricao": "Cavalo mecânico 6x2/6x4 + semirreboque de 3 eixos tandem juntos (tradicional LS).",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Cavalo - Tração Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 4, 5 e 6 (Carreta - Tandem Triplo)", "limite_legal": 25500, "tipo": "tandem_triplo"},
        ]
    },
    "VANDERLEIA_6E": {
        "codigo": "VANDERLEIA_6E",
        "nome": "Carreta Vanderléia 3 Eixos Distanciados (6 eixos total)",
        "categoria": "Veículo Articulado",
        "eixos": 6,
        "pbtc_legal": 53000,  # 53,0 toneladas
        "requer_aet": False,
        "tara_media_referencia": 16000,
        "descricao": "Cavalo 6x2/6x4 + semirreboque com 3 eixos distanciados (10t por eixo isolado no semirreboque).",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Cavalo - Tração Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixo 4 (Carreta - 1º Eixo Distanciado)", "limite_legal": 10000, "tipo": "simples_isolado"},
            {"nome": "Eixo 5 (Carreta - 2º Eixo Distanciado)", "limite_legal": 10000, "tipo": "simples_isolado"},
            {"nome": "Eixo 6 (Carreta - 3º Eixo Distanciado)", "limite_legal": 10000, "tipo": "simples_isolado"},
        ]
    },
    "CARRETA_4_EIXOS": {
        "codigo": "CARRETA_4_EIXOS",
        "nome": "Carreta 4 Eixos (7 eixos total - Res. CONTRAN 882)",
        "categoria": "Veículo Articulado",
        "eixos": 7,
        "pbtc_legal": 58500,  # 58,5 toneladas
        "requer_aet": False,
        "tara_media_referencia": 17500,
        "descricao": "Cavalo 6x4 + semirreboque de 4 eixos (1 autodirecional distanciado + tandem triplo).",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Cavalo - Tração Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixo 4 (Carreta - Direcional Isolado)", "limite_legal": 10000, "tipo": "simples_isolado"},
            {"nome": "Eixos 5, 6 e 7 (Carreta - Tandem Triplo)", "limite_legal": 25500, "tipo": "tandem_triplo"},
        ]
    },
    "BITREM_7E": {
        "codigo": "BITREM_7E",
        "nome": "Bitrem 7 Eixos (CVC Articulado)",
        "categoria": "Combinação de Carga (CVC)",
        "eixos": 7,
        "pbtc_legal": 57000,  # 57,0 toneladas
        "requer_aet": False,
        "tara_media_referencia": 18500,
        "descricao": "Cavalo trator 6x4 + dois semirreboques acoplados por quinta-roda (2 eixos em cada semirreboque).",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Cavalo - Tração Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 4 e 5 (1º Semirreboque - Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 6 e 7 (2º Semirreboque - Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
        ]
    },
    "BITRENZA_9E": {
        "codigo": "BITRENZA_9E",
        "nome": "Bitrem 9 Eixos / Bitrenza (CVC 9 eixos)",
        "categoria": "Combinação de Carga (CVC)",
        "eixos": 9,
        "pbtc_legal": 74000,  # 74,0 toneladas
        "requer_aet": True,
        "tara_media_referencia": 21500,
        "descricao": "Cavalo trator 6x4 + semirreboque dianteiro com tandem triplo + semirreboque traseiro com tandem triplo.",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Cavalo - Tração Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 4, 5 e 6 (1º Semirreboque - Triplo)", "limite_legal": 25500, "tipo": "tandem_triplo"},
            {"nome": "Eixos 7, 8 e 9 (2º Semirreboque - Triplo)", "limite_legal": 25500, "tipo": "tandem_triplo"},
        ]
    },
    "RODOTREM_9E": {
        "codigo": "RODOTREM_9E",
        "nome": "Rodotrem / Treminhão 9 Eixos (com Dolly)",
        "categoria": "Combinação de Carga (CVC)",
        "eixos": 9,
        "pbtc_legal": 74000,  # 74,0 toneladas
        "requer_aet": True,
        "tara_media_referencia": 22500,
        "descricao": "Cavalo 6x4 + 1º Semirreboque (2 eixos) + Dolly intermediário (2 eixos) + 2º Semirreboque (2 eixos).",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Cavalo - Tração Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 4 e 5 (1º Semirreboque - Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 6 e 7 (Dolly de Acoplamento - Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 8 e 9 (2º Semirreboque - Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
        ]
    },
    "SUPER_RODOTREM_11E": {
        "codigo": "SUPER_RODOTREM_11E",
        "nome": "Super Rodotrem 11 Eixos (CVC Canavieiro / Especial)",
        "categoria": "Combinação Especial (AET)",
        "eixos": 11,
        "pbtc_legal": 91000,  # 91,0 toneladas
        "requer_aet": True,
        "tara_media_referencia": 26000,
        "descricao": "Cavalo 6x4 + composições especiais de até 11 eixos autorizadas com AET específica.",
        "grupos_eixos": [
            {"nome": "Eixo 1 (Cavalo - Dianteiro)", "limite_legal": 6000, "tipo": "simples_direcional"},
            {"nome": "Eixos 2 e 3 (Cavalo - Tração Tandem)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 4, 5 e 6 (1º Semirreboque)", "limite_legal": 25500, "tipo": "tandem_triplo"},
            {"nome": "Eixos 7 e 8 (Dolly)", "limite_legal": 17000, "tipo": "tandem_duplo"},
            {"nome": "Eixos 9, 10 e 11 (2º Semirreboque)", "limite_legal": 25500, "tipo": "tandem_triplo"},
        ]
    },
    "PERSONALIZADO": {
        "codigo": "PERSONALIZADO",
        "nome": "Personalizado / Especial (AET sob medida)",
        "categoria": "Especial",
        "eixos": 0,
        "pbtc_legal": 45000,
        "requer_aet": True,
        "tara_media_referencia": 15000,
        "descricao": "Configuração personalizada com limite de PBTC definido manualmente pelo operador.",
        "grupos_eixos": []
    }
}

# Lista ordenada de opções para caixas de seleção
VEHICLE_OPTIONS: List[tuple] = [
    (k, v["nome"], f"{v['pbtc_legal'] / 1000:.1f}t")
    for k, v in VEHICLES_DATABASE.items()
]

# Produtos típicos de granéis e agronegócio (LDC)
PRODUTOS_PADRAO = [
    "Soja em Grãos",
    "Milho em Grãos",
    "Farelo de Soja",
    "Açúcar a Granel / Sacaria",
    "Adubo / Fertilizante",
    "Trigo",
    "Algodão em Pluma / Caroço",
    "Café",
    "Óleo Vegetal (Líquido)",
    "Carga Geral / Outros"
]
