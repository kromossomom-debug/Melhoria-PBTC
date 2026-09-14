"""
Aba de Análise e Distribuição de Peso por Grupos de Eixos.
Aplica a tolerância legal de 12,5% por eixo (Lei nº 14.229/2021 e Resoluções CONTRAN).
"""

import tkinter as tk
from typing import List, Dict, Any
import customtkinter as ctk

from vehicles_db import VEHICLES_DATABASE
from pbtc_core import calcular_pesagem_por_eixos, ResultadoEixo
from ui.theme import THEME_COLORS, formatar_kg, parse_numero


class TabAxles:
    def __init__(self, parent_frame: ctk.CTkFrame, app_instance):
        self.frame = parent_frame
        self.app = app_instance
        self.inputs_eixos: List[ctk.CTkEntry] = []
        self.cards_resultados: List[Dict[str, Any]] = []

        self._criar_layout()
        self._carregar_grupos_veiculo("CARRETA_LS_6E")

    def _criar_layout(self):
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)

        # TOPO: CABEÇALHO E SELETOR
        header = ctk.CTkFrame(self.frame, corner_radius=8)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="⚖️ Análise de Balança por Eixos (Tolerância Legal de 12,5% - Lei 14.229/2021)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME_COLORS["accent_cyan"]
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 5))

        ctk.CTkLabel(header, text="Veículo para Análise:").grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        self.mapa_veiculos = {f"{v['nome']} ({v['eixos']} eixos)": k for k, v in VEHICLES_DATABASE.items() if k != "PERSONALIZADO"}
        self.combo_veiculo_eixo = ctk.CTkComboBox(
            header,
            values=list(self.mapa_veiculos.keys()),
            command=self._ao_trocar_veiculo,
            width=380
        )
        self.combo_veiculo_eixo.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 10))

        btn_simular = ctk.CTkButton(
            header,
            text="🔄 Simular Distribuição Típica",
            fg_color=THEME_COLORS["secondary"],
            command=self._simular_distribuicao_tipica
        )
        btn_simular.grid(row=1, column=2, sticky="e", padx=12, pady=(0, 10))

        # CARD INFORMATIVO DA LEI
        card_lei = ctk.CTkFrame(self.frame, corner_radius=6, fg_color="#1E293B")
        card_lei.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(
            card_lei,
            text=(
                "ℹ️ Regra CONTRAN: Se o PBTC total estiver regular (dentro dos 5%), cada grupo de eixos possui tolerância de "
                "até 12,5% sobre seu limite técnico. Caso ultrapasse, é exigido remanejamento/redistribuição física da carga "
                "entre os compartimentos ou transbordo."
            ),
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
            wraplength=950,
            justify="left"
        ).pack(fill="x", padx=12, pady=6)

        # ÁREA DE CONTEÚDO COM SCROLL (LISTA DE EIXOS)
        self.scroll_eixos = ctk.CTkScrollableFrame(self.frame, corner_radius=8)
        self.scroll_eixos.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.scroll_eixos.grid_columnconfigure(0, weight=1)

        # BARRA INFERIOR DE PARECER
        self.card_parecer = ctk.CTkFrame(self.frame, corner_radius=8, fg_color=THEME_COLORS["dark_card"])
        self.card_parecer.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.card_parecer.grid_columnconfigure(0, weight=1)

        self.lbl_parecer_titulo = ctk.CTkLabel(
            self.card_parecer,
            text="Diagnóstico da Distribuição por Eixo:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_parecer_titulo.grid(row=0, column=0, sticky="w", padx=15, pady=(8, 2))

        self.lbl_parecer_msg = ctk.CTkLabel(
            self.card_parecer,
            text="Informe os pesos aferidos nos grupos de eixos para conferência.",
            font=ctk.CTkFont(size=13),
            text_color="#CBD5E1",
            justify="left",
            wraplength=900
        )
        self.lbl_parecer_msg.grid(row=1, column=0, sticky="w", padx=15, pady=(2, 8))

    def _ao_trocar_veiculo(self, escolha):
        chave = self.mapa_veiculos.get(escolha, "CARRETA_LS_6E")
        self._carregar_grupos_veiculo(chave)

    def _carregar_grupos_veiculo(self, codigo_veiculo: str):
        # Limpa widgets anteriores
        for widget in self.scroll_eixos.winfo_children():
            widget.destroy()

        self.inputs_eixos.clear()
        self.cards_resultados.clear()

        veic = VEHICLES_DATABASE.get(codigo_veiculo, {})
        grupos = veic.get("grupos_eixos", [])

        for i, grupo in enumerate(grupos):
            card_eixo = ctk.CTkFrame(self.scroll_eixos, corner_radius=8, border_width=1, border_color="#334155")
            card_eixo.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            card_eixo.grid_columnconfigure(1, weight=1)

            # Coluna 0: Nome do grupo e limites
            f_info = ctk.CTkFrame(card_eixo, fg_color="transparent")
            f_info.grid(row=0, column=0, sticky="w", padx=12, pady=10)

            ctk.CTkLabel(
                f_info,
                text=grupo["nome"],
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w")

            limite_legal = grupo["limite_legal"]
            limite_tol = limite_legal * 1.125
            ctk.CTkLabel(
                f_info,
                text=f"Limite Legal: {formatar_kg(limite_legal)}  |  Teto Tolerância (+12,5%): {formatar_kg(limite_tol)}",
                font=ctk.CTkFont(size=12),
                text_color=THEME_COLORS["text_muted"]
            ).pack(anchor="w")

            # Coluna 1: Entrada do Peso Aferido
            f_input = ctk.CTkFrame(card_eixo, fg_color="transparent")
            f_input.grid(row=0, column=1, sticky="e", padx=10, pady=10)

            ctk.CTkLabel(f_input, text="Peso Aferido no Grupo:").pack(side="left", padx=6)

            entry_peso = ctk.CTkEntry(f_input, width=130, height=32, placeholder_text="kg")
            entry_peso.pack(side="left", padx=4)
            entry_peso.bind("<KeyRelease>", lambda event: self._calcular_eixos())
            self.inputs_eixos.append(entry_peso)

            # Coluna 2: Badge de Status do Eixo
            badge_status = ctk.CTkLabel(
                card_eixo,
                text="Aguardando",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=160,
                height=30,
                corner_radius=6,
                fg_color="#334155",
                text_color="#FFFFFF"
            )
            badge_status.grid(row=0, column=2, padx=12, pady=10)

            self.cards_resultados.append({
                "badge": badge_status,
                "grupo": grupo
            })

        self._calcular_eixos()

    def _simular_distribuicao_tipica(self):
        """Preenche valores típicos de peso distribuído com base no PBTC legal do veículo."""
        escolha = self.combo_veiculo_eixo.get()
        chave = self.mapa_veiculos.get(escolha, "CARRETA_LS_6E")
        veic = VEHICLES_DATABASE.get(chave, {})
        grupos = veic.get("grupos_eixos", [])

        # Distribui perto de 92% do limite de cada eixo (situação ideal carregado)
        for i, grupo in enumerate(grupos):
            if i < len(self.inputs_eixos):
                peso_sugerido = int(grupo["limite_legal"] * 0.94)
                self.inputs_eixos[i].delete(0, tk.END)
                self.inputs_eixos[i].insert(0, str(peso_sugerido))

        self._calcular_eixos()

    def _calcular_eixos(self):
        escolha = self.combo_veiculo_eixo.get()
        chave = self.mapa_veiculos.get(escolha, "CARRETA_LS_6E")

        pesos = [parse_numero(entry.get()) for entry in self.inputs_eixos]
        resultados = calcular_pesagem_por_eixos(chave, pesos)

        tem_excesso = False
        tem_alerta = False
        mensagens_alerta = []
        peso_total_eixos = sum(pesos)

        for i, res_eixo in enumerate(resultados):
            if i < len(self.cards_resultados):
                badge = self.cards_resultados[i]["badge"]
                if res_eixo.peso_aferido_kg == 0:
                    badge.configure(text="Pendente", fg_color="#334155", text_color="#FFFFFF")
                elif res_eixo.status_codigo == "OK":
                    badge.configure(text=f"🟢 OK ({res_eixo.percentual:.0f}%)", fg_color=THEME_COLORS["success_bg"], text_color="#34D399")
                elif res_eixo.status_codigo == "ALERTA":
                    tem_alerta = True
                    badge.configure(text=f"🟡 Tolerância ({res_eixo.percentual:.0f}%)", fg_color=THEME_COLORS["warning_bg"], text_color="#FBBF24")
                else:
                    tem_excesso = True
                    badge.configure(text=f"🔴 Excesso +{formatar_kg(res_eixo.excesso_kg)}", fg_color=THEME_COLORS["danger_bg"], text_color="#F87171")
                    mensagens_alerta.append(f"{res_eixo.nome}: Excesso de {formatar_kg(res_eixo.excesso_kg)}.")

        # Atualiza o parecer geral
        if peso_total_eixos == 0:
            self.lbl_parecer_titulo.configure(text="Diagnóstico de Balança por Eixos: Pendente", text_color="#FFFFFF")
            self.lbl_parecer_msg.configure(text="Preencha os pesos aferidos em cada balança de eixos.")
            self.card_parecer.configure(fg_color=THEME_COLORS["dark_card"])
        elif tem_excesso:
            self.lbl_parecer_titulo.configure(text="🔴 REPROVADO: EXCESSO DETECTADO EM GRUPO DE EIXOS!", text_color="#F87171")
            msg = " ".join(mensagens_alerta) + " Ação recomendada: Fazer o remanejamento/redistribuição da carga ou transbordo imediato antes da liberação do caminhão."
            self.lbl_parecer_msg.configure(text=msg)
            self.card_parecer.configure(fg_color=THEME_COLORS["danger_bg"])
        elif tem_alerta:
            self.lbl_parecer_titulo.configure(text="🟡 ALERTA: EIXO NA FAIXA DE TOLERÂNCIA (12,5%)", text_color="#FBBF24")
            self.lbl_parecer_msg.configure(
                text=(
                    f"Soma total aferida nos eixos: {formatar_kg(peso_total_eixos)}. "
                    "Todos os eixos estão dentro da tolerância de balança, porém próximos ao limite regulamentar. Liberado com advertência."
                )
            )
            self.card_parecer.configure(fg_color=THEME_COLORS["warning_bg"])
        else:
            self.lbl_parecer_titulo.configure(text="🟢 APROVADO: TODOS OS EIXOS EM CONFORMIDADE", text_color="#34D399")
            self.lbl_parecer_msg.configure(
                text=(
                    f"Soma total aferida nos eixos: {formatar_kg(peso_total_eixos)}. "
                    "Excelente distribuição de carga entre o cavalo mecânico e o semirreboque. Carregamento liberado sem restrições."
                )
            )
            self.card_parecer.configure(fg_color=THEME_COLORS["success_bg"])
