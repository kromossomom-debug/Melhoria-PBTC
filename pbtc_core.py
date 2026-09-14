"""
Módulo Central de Cálculos de PBTC e Regras de Negócio de Pesagem.
Implementa tolerâncias oficiais CONTRAN (5% PBTC / 12,5% eixos) e conferência de carregamento.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from vehicles_db import VEHICLES_DATABASE

# Constantes da Legislação Brasileira
TOLERANCIA_PBTC_PERCENTUAL = 5.0    # 5% de tolerância no PBT/PBTC
TOLERANCIA_EIXO_PERCENTUAL = 12.5   # 12,5% de tolerância por eixo (Lei 14.229/2021)

@dataclass
class ResultadoPBTC:
    timestamp: str
    veiculo_codigo: str
    veiculo_nome: str
    categoria: str
    eixos: int
    tara_kg: float
    carga_liquida_kg: float
    pbtc_aferido_kg: float
    limite_legal_kg: float
    tolerancia_5pct_kg: float
    limite_balanca_kg: float
    status: str
    status_codigo: str  # OK, ALERTA, EXCESSO
    mensagem: str
    cor_status: str
    saldo_carga_disponivel_kg: float
    excesso_sobre_legal_kg: float
    excesso_sobre_tolerancia_kg: float
    transbordo_obrigatorio_kg: float
    capacidade_util_maxima_kg: float
    capacidade_util_tolerancia_kg: float
    percentual_utilizacao_legal: float
    percentual_utilizacao_balanca: float
    placa_cavalo: str = ""
    placa_carreta: str = ""
    romaneio: str = ""
    motorista: str = ""
    produto: str = ""
    observacoes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResultadoEixo:
    nome: str
    tipo: str
    peso_aferido_kg: float
    limite_legal_kg: float
    tolerancia_kg: float
    limite_tolerancia_kg: float
    status: str
    status_codigo: str
    excesso_kg: float
    percentual: float


def obter_dados_veiculo(codigo_veiculo: str, limite_manual: Optional[float] = None) -> Dict[str, Any]:
    """Retorna os dados do veículo a partir do banco de dados ou personalização."""
    veiculo = VEHICLES_DATABASE.get(codigo_veiculo, VEHICLES_DATABASE["TOCO_4X2"]).copy()
    if codigo_veiculo == "PERSONALIZADO" and limite_manual and limite_manual > 0:
        veiculo["pbtc_legal"] = float(limite_manual)
    return veiculo


def calcular_pbtc(
    tara_kg: float,
    carga_liquida_kg: float,
    codigo_veiculo: str,
    limite_manual: Optional[float] = None,
    placa_cavalo: str = "",
    placa_carreta: str = "",
    romaneio: str = "",
    motorista: str = "",
    produto: str = "",
    observacoes: str = ""
) -> ResultadoPBTC:
    """
    Calcula o PBTC e valida a conformidade de acordo com as normas do CONTRAN.
    """
    veiculo = obter_dados_veiculo(codigo_veiculo, limite_manual)

    tara = max(0.0, float(tara_kg))
    carga = max(0.0, float(carga_liquida_kg))
    pbtc_aferido = tara + carga

    limite_legal = float(veiculo["pbtc_legal"])
    tolerancia_5pct = limite_legal * (TOLERANCIA_PBTC_PERCENTUAL / 100.0)
    limite_balanca = limite_legal + tolerancia_5pct

    capacidade_util_maxima = max(0.0, limite_legal - tara)
    capacidade_util_tolerancia = max(0.0, limite_balanca - tara)

    excesso_sobre_legal = max(0.0, pbtc_aferido - limite_legal)
    excesso_sobre_tolerancia = max(0.0, pbtc_aferido - limite_balanca)
    transbordo_obrigatorio = excesso_sobre_tolerancia

    if pbtc_aferido <= limite_legal:
        saldo_disponivel = limite_legal - pbtc_aferido
        status = "CONFORME / LIBERADO"
        status_codigo = "OK"
        mensagem = "Carregamento 100% regular. Dentro do limite legal regulamentar do CONTRAN."
        cor_status = "#10B981"  # Verde esmeralda
    elif pbtc_aferido <= limite_balanca:
        saldo_disponivel = 0.0
        status = "TOLERÂNCIA DE BALANÇA (5%)"
        status_codigo = "ALERTA"
        mensagem = (
            f"Atenção: Peso acima do limite legal (+{excesso_sobre_legal:,.0f} kg), "
            f"porém dentro da margem de 5% da balança. Liberado sem multa, mas em limite prudencial."
        ).replace(",", ".")
        cor_status = "#F59E0B"  # Âmbar / Amarelo
    else:
        saldo_disponivel = 0.0
        status = "EXCESSO DE PESO (BLOQUEADO)"
        status_codigo = "EXCESSO"
        mensagem = (
            f"REPROVADO: Excesso de {excesso_sobre_tolerancia:,.0f} kg acima do teto de tolerância da balança. "
            f"Transbordo obrigatório de carga antes da saída!"
        ).replace(",", ".")
        cor_status = "#EF4444"  # Vermelho rubi

    percentual_legal = (pbtc_aferido / limite_legal * 100.0) if limite_legal > 0 else 0.0
    percentual_balanca = (pbtc_aferido / limite_balanca * 100.0) if limite_balanca > 0 else 0.0

    return ResultadoPBTC(
        timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        veiculo_codigo=codigo_veiculo,
        veiculo_nome=veiculo["nome"],
        categoria=veiculo["categoria"],
        eixos=veiculo["eixos"],
        tara_kg=tara,
        carga_liquida_kg=carga,
        pbtc_aferido_kg=pbtc_aferido,
        limite_legal_kg=limite_legal,
        tolerancia_5pct_kg=tolerancia_5pct,
        limite_balanca_kg=limite_balanca,
        status=status,
        status_codigo=status_codigo,
        mensagem=mensagem,
        cor_status=cor_status,
        saldo_carga_disponivel_kg=saldo_disponivel,
        excesso_sobre_legal_kg=excesso_sobre_legal,
        excesso_sobre_tolerancia_kg=excesso_sobre_tolerancia,
        transbordo_obrigatorio_kg=transbordo_obrigatorio,
        capacidade_util_maxima_kg=capacidade_util_maxima,
        capacidade_util_tolerancia_kg=capacidade_util_tolerancia,
        percentual_utilizacao_legal=percentual_legal,
        percentual_utilizacao_balanca=percentual_balanca,
        placa_cavalo=placa_cavalo.strip().upper(),
        placa_carreta=placa_carreta.strip().upper(),
        romaneio=romaneio.strip(),
        motorista=motorista.strip(),
        produto=produto.strip(),
        observacoes=observacoes.strip()
    )


def calcular_pesagem_por_eixos(
    codigo_veiculo: str,
    pesos_aferidos: List[float]
) -> List[ResultadoEixo]:
    """
    Avalia individualmente os pesos por grupo de eixos aplicando a tolerância de 12,5% (Lei 14.229/2021).
    """
    veiculo = VEHICLES_DATABASE.get(codigo_veiculo, {})
    grupos = veiculo.get("grupos_eixos", [])
    resultados = []

    for i, grupo in enumerate(grupos):
        peso = pesos_aferidos[i] if i < len(pesos_aferidos) else 0.0
        limite_legal = float(grupo["limite_legal"])
        tolerancia = limite_legal * (TOLERANCIA_EIXO_PERCENTUAL / 100.0)
        limite_tolerancia = limite_legal + tolerancia

        if peso <= limite_legal:
            status = "CONFORME"
            status_codigo = "OK"
            excesso = 0.0
        elif peso <= limite_tolerancia:
            status = "TOLERÂNCIA (12,5%)"
            status_codigo = "ALERTA"
            excesso = 0.0
        else:
            status = "EXCESSO NO EIXO"
            status_codigo = "EXCESSO"
            excesso = peso - limite_tolerancia

        percentual = (peso / limite_legal * 100.0) if limite_legal > 0 else 0.0

        resultados.append(ResultadoEixo(
            nome=grupo["nome"],
            tipo=grupo["tipo"],
            peso_aferido_kg=peso,
            limite_legal_kg=limite_legal,
            tolerancia_kg=tolerancia,
            limite_tolerancia_kg=limite_tolerancia,
            status=status,
            status_codigo=status_codigo,
            excesso_kg=excesso,
            percentual=percentual
        ))

    return resultados


def gerar_ticket_pesagem_texto(resultado: ResultadoPBTC) -> str:
    """Gera um ticket de conferência de carregamento pronto para impressão/cópia."""
    sep = "=" * 54
    subsep = "-" * 54
    data_hora = resultado.timestamp

    def fmt(valor: float) -> str:
        return f"{valor:,.0f} kg".replace(",", ".")

    def fmt_t(valor: float) -> str:
        return f"{valor / 1000:,.2f} t".replace(",", "X").replace(".", ",").replace("X", ".")

    ticket = f"""{sep}
        TICKET DE CONFERÊNCIA DE PESAGEM E PBTC
                 GESTÃO DE EXPEDIÇÃO & BALANÇA
{sep}
Data e Hora: {data_hora}
Romaneio / Ticket: {resultado.romaneio or 'N/A'}
Motorista: {resultado.motorista or 'N/A'}
Placa Cavalo: {resultado.placa_cavalo or 'N/A'}  |  Placa Carreta: {resultado.placa_carreta or 'N/A'}
Produto: {resultado.produto or 'N/A'}
{subsep}
DADOS DO VEÍCULO (CONTRAN):
Veículo: {resultado.veiculo_nome}
Categoria: {resultado.categoria} ({resultado.eixos} eixos)
{subsep}
PESAGEM AFERIDA:
Tara do Veículo:           {fmt(resultado.tara_kg):>14}  ({fmt_t(resultado.tara_kg)})
Peso Líquido da Carga:     {fmt(resultado.carga_liquida_kg):>14}  ({fmt_t(resultado.carga_liquida_kg)})
PBTC TOTAL AFERIDO:        {fmt(resultado.pbtc_aferido_kg):>14}  ({fmt_t(resultado.pbtc_aferido_kg)})
{subsep}
LIMITES LEGAIS E TOLERÂNCIAS:
Limite Legal CONTRAN:      {fmt(resultado.limite_legal_kg):>14}  ({fmt_t(resultado.limite_legal_kg)})
Tolerância Balança (+5%):  {fmt(resultado.tolerancia_5pct_kg):>14}
Teto Máximo com Tolerância:{fmt(resultado.limite_balanca_kg):>14}  ({fmt_t(resultado.limite_balanca_kg)})
{subsep}
DIAGNÓSTICO E BALANÇO:
Status de Liberação:       {resultado.status}
Capacidade Útil Legal:     {fmt(resultado.capacidade_util_maxima_kg):>14}
Saldo de Carga Restante:   {fmt(resultado.saldo_carga_disponivel_kg):>14}
Excesso s/ Limite Legal:   {fmt(resultado.excesso_sobre_legal_kg):>14}
TRANSBORDO OBRIGATÓRIO:    {fmt(resultado.transbordo_obrigatorio_kg):>14}
Ocupação da Balança:       {resultado.percentual_utilizacao_balanca:.1f}%
{subsep}
PARECER OPERACIONAL:
{resultado.mensagem}
{sep}
"""
    if resultado.observacoes:
        ticket += f"OBSERVAÇÕES:\n{resultado.observacoes}\n{sep}\n"

    return ticket
