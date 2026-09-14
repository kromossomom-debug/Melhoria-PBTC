"""
Definições de Tema, Cores, Estilos e Formatadores para a Interface Gráfica.
"""

# Paleta de Cores Moderna e Corporativa
THEME_COLORS = {
    "primary": "#1E40AF",        # Azul Royal / LDC Blue
    "primary_hover": "#1D4ED8",
    "secondary": "#475569",      # Slate
    "success": "#10B981",        # Esmeralda / Conforme
    "success_bg": "#064E3B",
    "warning": "#F59E0B",        # Âmbar / Tolerância
    "warning_bg": "#78350F",
    "danger": "#EF4444",         # Vermelho / Excesso
    "danger_bg": "#7F1D1D",
    "dark_card": "#1E293B",      # Slate 800
    "light_card": "#F1F5F9",     # Slate 100
    "dark_card_border": "#334155",
    "light_card_border": "#CBD5E1",
    "text_muted": "#94A3B8",
    "accent_cyan": "#06B6D4"
}

def formatar_kg(valor: float) -> str:
    """Formata valor numérico para padrão brasileiro em kg."""
    try:
        return f"{float(valor):,.0f} kg".replace(",", ".")
    except (ValueError, TypeError):
        return "0 kg"

def formatar_toneladas(valor: float) -> str:
    """Formata valor em kg para toneladas com 2 casas decimais."""
    try:
        t = float(valor) / 1000.0
        return f"{t:,.2f} t".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0,00 t"

def parse_numero(texto: str) -> float:
    """Converte strings digitadas (com pontos ou vírgulas) em float limpo."""
    if not texto:
        return 0.0
    limpo = str(texto).strip().replace("kg", "").replace("KG", "").replace("t", "").replace("T", "")
    # Se contém ponto e vírgula, e.g. 15.000,50
    if "." in limpo and "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    elif "." in limpo:
        # Se tiver mais de um ponto ou ponto no milhar (ex: 15.000)
        partes = limpo.split(".")
        if len(partes) > 1 and len(partes[-1]) == 3 and len(partes) == 2 and float(partes[0]) > 0:
            # Caso comum: 15.000 (15 mil kg)
            limpo = limpo.replace(".", "")
        elif len(partes) > 2:
            limpo = limpo.replace(".", "")
    try:
        return float(limpo)
    except ValueError:
        return 0.0
