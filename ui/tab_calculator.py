"""
Aba Principal de Cálculo de PBTC - Modo Balança Operacional Direta.
Projetada para alta velocidade de pesagem, cálculo em tempo real e atalhos de teclado.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from vehicles_db import VEHICLES_DATABASE, PRODUTOS_PADRAO
from pbtc_core import calcular_pbtc, gerar_ticket_pesagem_texto, ResultadoPBTC
from ui.theme import THEME_COLORS, formatar_kg, formatar_toneladas, parse_numero


class TabCalculator:
    def __init__(self, parent_frame: ctk.CTkFrame, app_instance):
        self.frame = parent_frame
        self.app = app_instance
        self.resultado_atual: ResultadoPBTC = None

        self._criar_layout()
        self._selecionar_veiculo_inicial()
        self._calcular()  # Executa primeiro cálculo com dados padrão

    def _criar_layout(self):
        # Grid da aba (duas colunas: esquerda formulário direto, direita diagnóstico)
        self.frame.grid_columnconfigure(0, weight=4, minsize=410)
        self.frame.grid_columnconfigure(1, weight=5, minsize=460)
        self.frame.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # COLUNA ESQUERDA: FORMULÁRIO OPERACIONAL DIRETO
        # ---------------------------------------------------------------------
        self.scroll_left = ctk.CTkScrollableFrame(self.frame, corner_radius=10)
        self.scroll_left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.scroll_left.grid_columnconfigure(0, weight=1)

        # TÍTULO E ATALHOS RÁPIDOS
        lbl_form_title = ctk.CTkLabel(
            self.scroll_left,
            text="⚡ Balança Direta & Expedição",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        lbl_form_title.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 4))

        # CARD 1: SELEÇÃO RÁPIDA DE VEÍCULOS (1 CLIQUE)
        card_quick = ctk.CTkFrame(self.scroll_left, corner_radius=8, fg_color="#1E293B")
        card_quick.grid(row=1, column=0, sticky="ew", padx=5, pady=4)
        card_quick.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            card_quick,
            text="ACESSO RÁPIDO AO TIPO DE CAMINHÃO (1 CLIQUE):",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["accent_cyan"]
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(6, 4))

        # Botões rápidos para os veículos mais comuns da fábrica
        self._criar_btn_rapido(card_quick, 1, 0, "Carreta LS 45t", "CARRETA_LS_6E")
        self._criar_btn_rapido(card_quick, 1, 1, "Vanderléia 53t", "VANDERLEIA_6E")
        self._criar_btn_rapido(card_quick, 1, 2, "Bitrem 57t", "BITREM_7E")
        self._criar_btn_rapido(card_quick, 2, 0, "Rodotrem 74t", "RODOTREM_9E")
        self._criar_btn_rapido(card_quick, 2, 1, "Carreta 4E 58,5t", "CARRETA_4_EIXOS")
        self._criar_btn_rapido(card_quick, 2, 2, "Bitruck 29t", "BITRUCK_8X2")

        # CARD 2: CONFIGURAÇÃO DO VEÍCULO (DROPDOWN COMPLETO)
        card_veic = ctk.CTkFrame(self.scroll_left, corner_radius=8)
        card_veic.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        card_veic.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_veic,
            text="Veículo Selecionado (CONTRAN)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(6, 2))

        self.mapa_nomes_veiculos = {f"{v['nome']} [{v['pbtc_legal']/1000:.1f}t]": k for k, v in VEHICLES_DATABASE.items()}
        lista_opcoes = list(self.mapa_nomes_veiculos.keys())

        self.combo_veiculo = ctk.CTkComboBox(
            card_veic,
            values=lista_opcoes,
            command=self._ao_trocar_veiculo,
            height=32
        )
        self.combo_veiculo.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 4))

        self.lbl_info_veiculo = ctk.CTkLabel(
            card_veic,
            text="...",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_muted"],
            justify="left",
            wraplength=380
        )
        self.lbl_info_veiculo.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 6))

        # Limite Manual (visível apenas para personalizado)
        self.frame_limite_manual = ctk.CTkFrame(card_veic, fg_color="transparent")
        self.frame_limite_manual.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.frame_limite_manual.grid_remove()

        ctk.CTkLabel(self.frame_limite_manual, text="Limite Manual PBTC (kg):").pack(side="left", padx=(0, 10))
        self.entry_limite_manual = ctk.CTkEntry(self.frame_limite_manual, width=130, placeholder_text="Ex: 50000")
        self.entry_limite_manual.insert(0, "45000")
        self.entry_limite_manual.pack(side="left")
        self.entry_limite_manual.bind("<KeyRelease>", lambda e: self._calcular())

        # CARD 3: ENTRADA DE PESAGEM (EM DESTAQUE OPERACIONAL)
        card_peso = ctk.CTkFrame(self.scroll_left, corner_radius=8, border_width=1, border_color="#3B82F6")
        card_peso.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        card_peso.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card_peso,
            text="⚖️ Pesagem da Balança (Cálculo Instantâneo ao Digitar)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#60A5FA"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 4))

        # Seletor de Modo de Entrada (Bruto vs Líquido)
        self.var_modo_peso = ctk.StringVar(value="BRUTO")
        seg_modo = ctk.CTkSegmentedButton(
            card_peso,
            values=["Tara + Peso Bruto Balança", "Tara + Peso Líquido"],
            command=self._ao_trocar_modo_peso
        )
        seg_modo.set("Tara + Peso Bruto Balança")
        seg_modo.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 6))

        # Campo Tara
        ctk.CTkLabel(card_peso, text="1. Tara do Veículo (kg):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", padx=10, pady=(2, 2))
        self.entry_tara = ctk.CTkEntry(card_peso, placeholder_text="Ex: 15500", height=34, font=ctk.CTkFont(size=14, weight="bold"))
        self.entry_tara.insert(0, "15500")
        self.entry_tara.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 6))
        self.entry_tara.bind("<KeyRelease>", lambda e: self._calcular())

        btn_tara_ref = ctk.CTkButton(
            card_peso,
            text="Restaurar Tara Ref.",
            height=34,
            fg_color=THEME_COLORS["secondary"],
            command=self._aplicar_tara_referencia
        )
        btn_tara_ref.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=(0, 6))

        # Campo Peso Bruto ou Líquido
        self.lbl_campo_peso2 = ctk.CTkLabel(card_peso, text="2. Peso Bruto da Balança (kg):", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_campo_peso2.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(2, 2))

        self.entry_peso2 = ctk.CTkEntry(
            card_peso,
            placeholder_text="Ex: 44500",
            height=38,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#38BDF8"
        )
        self.entry_peso2.insert(0, "44500")
        self.entry_peso2.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        self.entry_peso2.bind("<KeyRelease>", lambda e: self._calcular())

        # CARD 4: DADOS COMPLEMENTARES / ROMANEIO (OPCIONAL E COMPACTO)
        card_id = ctk.CTkFrame(self.scroll_left, corner_radius=8)
        card_id.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        card_id.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card_id,
            text="📋 Identificação / Romaneio (Opcional)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["text_muted"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(6, 4))

        ctk.CTkLabel(card_id, text="Nº Romaneio:").grid(row=1, column=0, sticky="w", padx=10, pady=1)
        self.entry_romaneio = ctk.CTkEntry(card_id, placeholder_text="Ex: ROM-88421", height=28)
        self.entry_romaneio.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 4))

        ctk.CTkLabel(card_id, text="Placa Cavalo:").grid(row=1, column=1, sticky="w", padx=10, pady=1)
        self.entry_placa_cavalo = ctk.CTkEntry(card_id, placeholder_text="Ex: BRA2E19", height=28)
        self.entry_placa_cavalo.grid(row=2, column=1, sticky="ew", padx=10, pady=(0, 4))

        ctk.CTkLabel(card_id, text="Motorista:").grid(row=3, column=0, sticky="w", padx=10, pady=1)
        self.entry_motorista = ctk.CTkEntry(card_id, placeholder_text="Motorista", height=28)
        self.entry_motorista.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 4))

        ctk.CTkLabel(card_id, text="Produto:").grid(row=3, column=1, sticky="w", padx=10, pady=1)
        self.combo_produto = ctk.CTkComboBox(card_id, values=PRODUTOS_PADRAO, height=28)
        self.combo_produto.set(PRODUTOS_PADRAO[0])
        self.combo_produto.grid(row=4, column=1, sticky="ew", padx=10, pady=(0, 6))

        # Campos extras que mantemos para compatibilidade
        self.entry_placa_carreta = ctk.CTkEntry(card_id)  # Oculto / compatibilidade
        self.entry_obs = ctk.CTkEntry(card_id)            # Oculto / compatibilidade

        # BARRA DE ATALHOS E BOTÕES RÁPIDOS
        card_botoes = ctk.CTkFrame(self.scroll_left, fg_color="transparent")
        card_botoes.grid(row=5, column=0, sticky="ew", padx=5, pady=8)
        card_botoes.grid_columnconfigure((0, 1), weight=1)

        btn_salvar = ctk.CTkButton(
            card_botoes,
            text="💾 Salvar Pesagem (Enter)",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            command=self._salvar_historico
        )
        btn_salvar.grid(row=0, column=0, sticky="ew", padx=4, pady=3)

        btn_limpar = ctk.CTkButton(
            card_botoes,
            text="🧹 Próximo Caminhão (F2)",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME_COLORS["secondary"],
            command=self._limpar_campos
        )
        btn_limpar.grid(row=0, column=1, sticky="ew", padx=4, pady=3)

        # Rótulo explicativo dos atalhos
        ctk.CTkLabel(
            card_botoes,
            text="⌨️ Teclas: [Enter] Grava Histórico  •  [F2 / Esc] Próximo Caminhão  •  [F3] Copiar Ticket",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_muted"]
        ).grid(row=1, column=0, columnspan=2, pady=(4, 0))

        # ---------------------------------------------------------------------
        # COLUNA DIREITA: DASHBOARD DE DIAGNÓSTICO IMEDIATO
        # ---------------------------------------------------------------------
        self.frame_right = ctk.CTkFrame(self.frame, corner_radius=10)
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_rowconfigure(3, weight=1)

        # BANNER DE STATUS GIGANTE (DIAGNÓSTICO IMEDIATO)
        self.card_status = ctk.CTkFrame(self.frame_right, corner_radius=8, fg_color=THEME_COLORS["success_bg"])
        self.card_status.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.card_status.grid_columnconfigure(0, weight=1)

        self.lbl_status_icon = ctk.CTkLabel(
            self.card_status,
            text="🟢 LIBERADO / CONFORME",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        self.lbl_status_icon.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))

        self.lbl_status_msg = ctk.CTkLabel(
            self.card_status,
            text="Carregamento regular dentro do limite regulamentar.",
            font=ctk.CTkFont(size=13),
            text_color="#E2E8F0",
            justify="left",
            wraplength=480
        )
        self.lbl_status_msg.grid(row=1, column=0, sticky="w", padx=15, pady=(2, 10))

        # BARRA DE UTILIZAÇÃO DA BALANÇA
        frame_progresso = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        frame_progresso.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        frame_progresso.grid_columnconfigure(0, weight=1)

        self.lbl_progresso_texto = ctk.CTkLabel(
            frame_progresso,
            text="Ocupação da Balança: 0,0%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_progresso_texto.grid(row=0, column=0, sticky="w")

        self.progresso_barra = ctk.CTkProgressBar(frame_progresso, height=14)
        self.progresso_barra.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.progresso_barra.set(0)

        # GRID DE CARDS KPI (2x3)
        grid_kpis = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        grid_kpis.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        grid_kpis.grid_columnconfigure((0, 1, 2), weight=1)

        self.kpi_pbtc = self._criar_card_kpi(grid_kpis, 0, 0, "PBTC Aferido", "0 kg", THEME_COLORS["accent_cyan"])
        self.kpi_limite_legal = self._criar_card_kpi(grid_kpis, 0, 1, "Limite CONTRAN", "0 kg", "#FFFFFF")
        self.kpi_limite_balanca = self._criar_card_kpi(grid_kpis, 0, 2, "Teto (+5%)", "0 kg", THEME_COLORS["warning"])

        self.kpi_cap_util = self._criar_card_kpi(grid_kpis, 1, 0, "Carga Líquida", "0 kg", THEME_COLORS["success"])
        self.kpi_saldo = self._criar_card_kpi(grid_kpis, 1, 1, "Saldo Disponível", "0 kg", "#FFFFFF")
        self.kpi_transbordo = self._criar_card_kpi(grid_kpis, 1, 2, "Transbordo Obrigatório", "0 kg", THEME_COLORS["danger"])

        # TICKET DE CONFERÊNCIA
        frame_ticket = ctk.CTkFrame(self.frame_right, corner_radius=8)
        frame_ticket.grid(row=3, column=0, sticky="nsew", padx=10, pady=(8, 10))
        frame_ticket.grid_columnconfigure(0, weight=1)
        frame_ticket.grid_rowconfigure(1, weight=1)

        header_ticket = ctk.CTkFrame(frame_ticket, fg_color="transparent")
        header_ticket.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        header_ticket.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_ticket,
            text="📄 Ticket de Conferência (Pronto para Copiar)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        btn_copiar = ctk.CTkButton(
            header_ticket,
            text="📋 Copiar (F3)",
            width=95,
            height=26,
            command=self._copiar_ticket
        )
        btn_copiar.grid(row=0, column=1, padx=4)

        btn_exportar_txt = ctk.CTkButton(
            header_ticket,
            text="💾 Salvar .TXT",
            width=90,
            height=26,
            fg_color=THEME_COLORS["secondary"],
            command=self._salvar_ticket_txt
        )
        btn_exportar_txt.grid(row=0, column=2, padx=4)

        self.txt_ticket = ctk.CTkTextbox(
            frame_ticket,
            font=ctk.CTkFont(family="Consolas", size=11),
            activate_scrollbars=True
        )
        self.txt_ticket.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # Vincula atalhos de teclado globais da janela
        self.app.root.bind("<Return>", lambda e: self._salvar_historico())
        self.app.root.bind("<F2>", lambda e: self._limpar_campos())
        self.app.root.bind("<Escape>", lambda e: self._limpar_campos())
        self.app.root.bind("<F3>", lambda e: self._copiar_ticket())

    def _criar_btn_rapido(self, parent, row, col, texto, codigo_veiculo):
        """Cria botão de seleção rápida em 1 clique."""
        btn = ctk.CTkButton(
            parent,
            text=texto,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#334155",
            hover_color="#1D4ED8",
            command=lambda: self._selecionar_veiculo_por_codigo(codigo_veiculo)
        )
        btn.grid(row=row, column=col, sticky="ew", padx=3, pady=2)

    def _criar_card_kpi(self, parent, row, col, titulo, valor_inicial, cor_destaque):
        card = ctk.CTkFrame(parent, corner_radius=6, border_width=1, border_color="#334155")
        card.grid(row=row, column=col, sticky="ew", padx=4, pady=4)

        lbl_tit = ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"])
        lbl_tit.pack(anchor="w", padx=8, pady=(5, 0))

        lbl_val = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=15, weight="bold"), text_color=cor_destaque)
        lbl_val.pack(anchor="w", padx=8, pady=(0, 5))
        return lbl_val

    def _selecionar_veiculo_inicial(self):
        self._selecionar_veiculo_por_codigo("CARRETA_LS_6E")

    def _selecionar_veiculo_por_codigo(self, codigo: str):
        for texto, chave in self.mapa_nomes_veiculos.items():
            if chave == codigo:
                self.combo_veiculo.set(texto)
                self._atualizar_info_veiculo(chave)
                self._aplicar_tara_referencia()
                break

    def _ao_trocar_veiculo(self, escolha):
        chave = self.mapa_nomes_veiculos.get(escolha)
        if chave:
            self._atualizar_info_veiculo(chave)
            self._aplicar_tara_referencia()

    def _atualizar_info_veiculo(self, chave: str):
        veic = VEHICLES_DATABASE.get(chave, {})
        if chave == "PERSONALIZADO":
            self.frame_limite_manual.grid()
        else:
            self.frame_limite_manual.grid_remove()

        info = (
            f"• {veic.get('categoria', '')} ({veic.get('eixos', 0)} eixos)  |  "
            f"Limite Legal: {formatar_toneladas(veic.get('pbtc_legal', 0))}  |  "
            f"Teto Balança: {formatar_toneladas(veic.get('pbtc_legal', 0) * 1.05)}"
        )
        self.lbl_info_veiculo.configure(text=info)

    def _ao_trocar_modo_peso(self, valor):
        if valor == "Tara + Peso Líquido":
            self.var_modo_peso.set("LIQUIDO")
            self.lbl_campo_peso2.configure(text="2. Peso Líquido da Carga (kg):")
            self.entry_peso2.configure(placeholder_text="Ex: 29000")
        else:
            self.var_modo_peso.set("BRUTO")
            self.lbl_campo_peso2.configure(text="2. Peso Bruto da Balança (kg):")
            self.entry_peso2.configure(placeholder_text="Ex: 44500")
        self._calcular()

    def _aplicar_tara_referencia(self):
        chave = self.obter_codigo_veiculo_selecionado()
        veic = VEHICLES_DATABASE.get(chave, {})
        tara_ref = veic.get("tara_media_referencia", 15500)
        self.entry_tara.delete(0, tk.END)
        self.entry_tara.insert(0, str(int(tara_ref)))
        self._calcular()

    def obter_codigo_veiculo_selecionado(self) -> str:
        escolha = self.combo_veiculo.get()
        return self.mapa_nomes_veiculos.get(escolha, "CARRETA_LS_6E")

    def _calcular(self):
        """Cálculo instantâneo em tempo real de PBTC."""
        cod_veiculo = self.obter_codigo_veiculo_selecionado()
        tara = parse_numero(self.entry_tara.get())
        segundo_peso = parse_numero(self.entry_peso2.get())

        if self.var_modo_peso.get() == "BRUTO":
            peso_bruto = segundo_peso
            carga_liquida = max(0.0, peso_bruto - tara)
        else:
            carga_liquida = segundo_peso

        limite_manual = None
        if cod_veiculo == "PERSONALIZADO":
            limite_manual = parse_numero(self.entry_limite_manual.get())

        resultado = calcular_pbtc(
            tara_kg=tara,
            carga_liquida_kg=carga_liquida,
            codigo_veiculo=cod_veiculo,
            limite_manual=limite_manual,
            placa_cavalo=self.entry_placa_cavalo.get(),
            placa_carreta="",
            romaneio=self.entry_romaneio.get(),
            motorista=self.entry_motorista.get(),
            produto=self.combo_produto.get(),
            observacoes=""
        )
        self.resultado_atual = resultado
        self._atualizar_dashboard(resultado)

    def _atualizar_dashboard(self, res: ResultadoPBTC):
        # Banner de Status
        if res.status_codigo == "OK":
            self.card_status.configure(fg_color=THEME_COLORS["success_bg"])
            self.lbl_status_icon.configure(text="🟢 LIBERADO / CONFORME")
            self.lbl_status_icon.configure(text_color="#34D399")
        elif res.status_codigo == "ALERTA":
            self.card_status.configure(fg_color=THEME_COLORS["warning_bg"])
            self.lbl_status_icon.configure(text="🟡 TOLERÂNCIA DE BALANÇA (5%)")
            self.lbl_status_icon.configure(text_color="#FBBF24")
        else:
            self.card_status.configure(fg_color=THEME_COLORS["danger_bg"])
            self.lbl_status_icon.configure(text="🔴 EXCESSO DE PESO (BLOQUEADO)")
            self.lbl_status_icon.configure(text_color="#F87171")

        self.lbl_status_msg.configure(text=res.mensagem)

        # Barra de Progresso
        fracao = min(1.0, res.percentual_utilizacao_balanca / 100.0) if res.limite_balanca_kg > 0 else 0
        self.progresso_barra.set(fracao)
        if res.status_codigo == "OK":
            self.progresso_barra.configure(progress_color=THEME_COLORS["success"])
        elif res.status_codigo == "ALERTA":
            self.progresso_barra.configure(progress_color=THEME_COLORS["warning"])
        else:
            self.progresso_barra.configure(progress_color=THEME_COLORS["danger"])

        self.lbl_progresso_texto.configure(
            text=f"Ocupação da Balança: {res.percentual_utilizacao_balanca:.1f}%  |  "
                 f"Limite CONTRAN: {formatar_kg(res.limite_legal_kg)}"
        )

        # KPIs Rápidos
        self.kpi_pbtc.configure(text=formatar_kg(res.pbtc_aferido_kg))
        self.kpi_limite_legal.configure(text=formatar_kg(res.limite_legal_kg))
        self.kpi_limite_balanca.configure(text=formatar_kg(res.limite_balanca_kg))
        self.kpi_cap_util.configure(text=formatar_kg(res.carga_liquida_kg))

        if res.saldo_carga_disponivel_kg > 0:
            self.kpi_saldo.configure(text=f"+{formatar_kg(res.saldo_carga_disponivel_kg)}", text_color=THEME_COLORS["success"])
        else:
            self.kpi_saldo.configure(text=f"-{formatar_kg(res.excesso_sobre_legal_kg)} (Acima)", text_color=THEME_COLORS["warning"])

        if res.transbordo_obrigatorio_kg > 0:
            self.kpi_transbordo.configure(
                text=f"⚠️ {formatar_kg(res.transbordo_obrigatorio_kg)}",
                text_color=THEME_COLORS["danger"]
            )
        else:
            self.kpi_transbordo.configure(text="0 kg (Liberado)", text_color="#10B981")

        # Ticket em texto
        ticket_str = gerar_ticket_pesagem_texto(res)
        self.txt_ticket.delete("0.0", tk.END)
        self.txt_ticket.insert("0.0", ticket_str)

    def _salvar_historico(self):
        if not self.resultado_atual:
            self._calcular()
        if self.resultado_atual:
            self.app.adicionar_ao_historico(self.resultado_atual)

    def _copiar_ticket(self):
        texto = self.txt_ticket.get("0.0", tk.END).strip()
        if texto:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(texto)
            messagebox.showinfo("Copiado", "Ticket copiado! Pronto para colar.")

    def _salvar_ticket_txt(self):
        texto = self.txt_ticket.get("0.0", tk.END).strip()
        if not texto:
            return
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt")],
            initialfile=f"Ticket_PBTC_{self.entry_placa_cavalo.get() or 'Carregamento'}.txt"
        )
        if arquivo:
            try:
                with open(arquivo, "w", encoding="utf-8") as f:
                    f.write(texto)
                messagebox.showinfo("Sucesso", f"Ticket salvo com sucesso em:\n{arquivo}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def _limpar_campos(self):
        """Limpa campos e já foca o cursor diretamente no campo de peso para o próximo caminhão."""
        self.entry_romaneio.delete(0, tk.END)
        self.entry_motorista.delete(0, tk.END)
        self.entry_placa_cavalo.delete(0, tk.END)
        self.entry_peso2.delete(0, tk.END)
        self.entry_peso2.insert(0, "44500")
        self._calcular()
        self.entry_peso2.focus_set()
        self.entry_peso2.select_range(0, tk.END)
