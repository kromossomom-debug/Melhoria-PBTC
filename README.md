# 🚛 PBTC Master - Sistema de Gestão de Balança & PBTC

Sistema profissional desenvolvido em Python para conferência, cálculo e validação do **PBTC (Peso Bruto Total Combinado)** de caminhões de transporte de cargas e grãos, em conformidade com as resoluções do **CONTRAN (Resolução nº 882/2021 e Lei nº 14.229/2021)**.

---

## 📌 Principais Funcionalidades

1. **Balança Operacional Direta (Zero Impacto na Fábrica)**:
   - **Botões Rápidos (1 clique)** para os veículos mais comuns da fábrica: *Carreta LS (45t)*, *Vanderléia (53t)*, *Bitrem (57t)*, *Rodotrem (74t)*, *Carreta 4E (58,5t)* e *Bitruck (29t)*.
   - **Cálculo em Tempo Real ao Digitar**: O resultado e o banner (🟢 Liberado / 🔴 Excesso) atualizam instantaneamente conforme o operador digita os números, sem necessidade de clicar em botões.
   - **Atalhos Operacionais de Balança**:
     - `[Enter]`: Salva a pesagem no histórico.
     - `[F2]` ou `[Esc]`: Limpa a tela e foca o cursor diretamente no campo de peso para o próximo caminhão.
     - `[F3]`: Copia o ticket de conferência formatado.
   - **Inicialização Relâmpago**: O arquivo `iniciar_sistema.bat` abre o programa instantaneamente (< 0.1s) sem reprocessar dependências.
   - **Modo Expresso via Terminal (`balanca_rapida.bat`)**: Versão ultra-leve em linha de comando pelo teclado numérico, com consumo zero de memória e resposta em 0.01 segundo.

2. **Dashboard de Diagnóstico Visual**:
   - 🟢 **CONFORME / LIBERADO**: Veículo dentro do limite legal CONTRAN.
   - 🟡 **TOLERÂNCIA DE BALANÇA (5%)**: Peso acima do legal, porém dentro da margem de balança (liberado sem multa, com alerta preventivo).
   - 🔴 **EXCESSO DE PESO (BLOQUEADO)**: Ultrapassou a tolerância. Exibe o peso exato de **transbordo obrigatório** a ser descarregado.
   - Barra dinâmica com percentual de ocupação da balança.
   - Cards de métricas rápidas: PBTC Aferido, Limite Legal, Teto da Balança (+5%), Capacidade Útil Máxima, Saldo Disponível e Transbordo.

3. **Geração de Ticket de Conferência**:
   - Gera um cupom/ticket padronizado com todos os dados da pesagem (placas, romaneio, motorista, produto, valores aferidos, limites e parecer operacional).
   - Botões para **Copiar para Área de Transferência** e **Salvar em arquivo .TXT**.

4. **Balança por Eixos (Tolerância de 12,5%)**:
   - Análise por grupo de eixos (direcional, tração e semirreboque/tandem) conforme a **Lei nº 14.229/2021**.
   - Simulação e detecção de sobrecarga em eixos específicos (muito comum em transporte graneleiro/agronegócio).

5. **Histórico da Sessão e Exportação para Excel (CSV)**:
   - Registro de todas as pesagens da jornada de trabalho.
   - KPIs consolidados do turno: Total de pesagens, liberados, alertas, excessos e volume total expedido em toneladas.
   - Exportação em formato **CSV com delimitador `;` e codificação UTF-8-BOM**, pronto para abrir diretamente no Microsoft Excel ou Google Sheets.

6. **Tabela de Consulta Rápida CONTRAN**:
   - Tabela de consulta técnica com limites legais, tolerâncias e necessidade de AET para apoio da equipe de balança.

---

## 🚀 Como Instalar e Rodar

### Pré-requisito
- Ter o **Python 3.8 ou superior** instalado na máquina.

### Método 1: Inicialização em 1 Clique (Windows)
Basta dar um duplo clique no arquivo:
```
iniciar_sistema.bat
```
*O script verifica automaticamente o Python, instala as dependências caso necessário e abre o programa imediatamente.*

### Método 2: Via Linha de Comando (Terminal / PowerShell)
1. Abra o terminal na pasta `Melhoria PBTC`.
2. Instale os pacotes necessários:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```bash
   python main.py
   ```

---

## 📁 Estrutura de Arquivos

```
Melhoria PBTC/
├── requirements.txt            # Dependências necessárias (customtkinter, etc.)
├── iniciar_sistema.bat         # Inicializador rápido para Windows
├── main.py                     # Ponto de entrada do sistema
├── pbtc_core.py                # Regras de negócio, cálculos matemáticos e tolerâncias
├── vehicles_db.py              # Catálogo oficial de configurações CONTRAN
├── README.md                   # Este manual de instruções
├── tests/
│   └── test_pbtc_core.py       # Testes unitários automatizados
└── ui/
    ├── __init__.py
    ├── theme.py                # Paleta visual, fontes e formatadores numéricos
    ├── app_window.py           # Janela principal e abas de navegação
    ├── tab_calculator.py       # Aba principal de cálculo de PBTC e tickets
    ├── tab_axles.py            # Aba de análise de peso por eixos (12,5%)
    ├── tab_history.py          # Aba de histórico da sessão e exportação CSV
    └── tab_reference.py        # Aba da tabela de consulta CONTRAN
```

---

## 📊 Tabela de Referência CONTRAN (Resumo de Pesos)

| Configuração do Caminhão | Eixos | Limite Legal | Teto Balança (+5%) | AET Obrigatória |
| :--- | :---: | :---: | :---: | :---: |
| **Toco (4x2)** | 2 | 16,0 t | 16,8 t | Não |
| **Truck (6x2 / 6x4)** | 3 | 23,0 t | 24,15 t | Não |
| **Bitruck (8x2 / 8x4)** | 4 | 29,0 t | 30,45 t | Não |
| **Cavalo 4x2 + Carreta 2 Eixos** | 4 | 33,0 t | 34,65 t | Não |
| **Cavalo 4x2 + Carreta 3 Eixos** | 5 | 41,5 t | 43,57 t | Não |
| **Carreta LS (3 eixos juntos)** | 6 | 45,0 t | 47,25 t | Não |
| **Carreta Vanderléia (distanciados)** | 6 | 53,0 t | 55,65 t | Não |
| **Carreta 4 Eixos (Res. 882)** | 7 | 58,5 t | 61,42 t | Não |
| **Bitrem 7 Eixos** | 7 | 57,0 t | 59,85 t | Não |
| **Bitrenza / Bitrem 9 Eixos** | 9 | 74,0 t | 77,70 t | Sim |
| **Rodotrem 9 Eixos** | 9 | 74,0 t | 77,70 t | Sim |
| **Super Rodotrem 11 Eixos** | 11 | 91,0 t | 95,55 t | Sim |
