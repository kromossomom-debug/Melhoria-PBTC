"""
Aba de Tabela de Consulta Rápida CONTRAN e Legislação de Pesos e Dimensões.
"""

from tkinter import ttk
import customtkinter as ctk

from vehicles_db import VEHICLES_DATABASE
from ui.theme import THEME_COLORS, formatar_kg, formatar_toneladas


class TabReference:
    def __init__(self, parent_frame: ctk.CTkFrame, app_instance):
        self.frame = parent_frame
        self.app = app_instance

        self._criar_layout()

    def _criar_layout(self):
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        # TOPO: CARDS DE LEGISLAÇÃO E REGRAS
        top_frame = ctk.CTkFrame(self.frame, corner_radius=8)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Resolução CONTRAN 882/2021
        c1 = ctk.CTkFrame(top_frame, corner_radius=6, fg_color="#1E293B")
        c1.grid(row=0, column=0, sticky="nsew", padx=5, pady=8)
        ctk.CTkLabel(c1, text="📜 Resolução CONTRAN 882/2021", font=ctk.CTkFont(size=13, weight="bold"), text_color=THEME_COLORS["accent_cyan"]).pack(anchor="w", padx=10, pady=(6, 2))
        ctk.CTkLabel(
            c1,
            text="Regulamenta os limites de Peso Bruto Total (PBT) e Combinado (PBTC), novas composições como Carreta 4 eixos (58,5t) e regras para emissão de AET.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            wraplength=280,
            justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 6))

        # Card 2: Tolerância de Balança 5%
        c2 = ctk.CTkFrame(top_frame, corner_radius=6, fg_color="#1E293B")
        c2.grid(row=0, column=1, sticky="nsew", padx=5, pady=8)
        ctk.CTkLabel(c2, text="⚖️ Tolerância Metrológica de 5%", font=ctk.CTkFont(size=13, weight="bold"), text_color=THEME_COLORS["warning"]).pack(anchor="w", padx=10, pady=(6, 2))
        ctk.CTkLabel(
            c2,
            text="Margem de erro admitida para balanças rodoviárias no peso total do veículo (PBT/PBTC). Pesos dentro da tolerância são liberados sem autuação.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            wraplength=280,
            justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 6))

        # Card 3: Lei 14.229/2021 (Eixos 12,5%)
        c3 = ctk.CTkFrame(top_frame, corner_radius=6, fg_color="#1E293B")
        c3.grid(row=0, column=2, sticky="nsew", padx=5, pady=8)
        ctk.CTkLabel(c3, text="🚛 Lei 14.229/2021 (Eixos 12,5%)", font=ctk.CTkFont(size=13, weight="bold"), text_color=THEME_COLORS["success"]).pack(anchor="w", padx=10, pady=(6, 2))
        ctk.CTkLabel(
            c3,
            text="Elevou a tolerância por eixo ou tandem de 10% para 12,5% quando o PBTC total estiver regular. Ultrapassado o limite, exige remanejamento de carga.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            wraplength=280,
            justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 6))

        # ÁREA DA TABELA COMPARATIVA
        table_frame = ctk.CTkFrame(self.frame, corner_radius=8)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            table_frame,
            text="📊 Tabela Geral de Pesos Máximos Regulamentares (CONTRAN)",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        colunas = ("codigo", "veiculo", "categoria", "eixos", "legal", "tol_5", "teto", "aet", "tara_ref")
        tree = ttk.Treeview(table_frame, columns=colunas, show="headings", selectmode="browse")

        tree.heading("codigo", text="Código")
        tree.heading("veiculo", text="Configuração do Veículo")
        tree.heading("categoria", text="Categoria")
        tree.heading("eixos", text="Eixos")
        tree.heading("legal", text="Limite Legal")
        tree.heading("tol_5", text="Tol. (+5%)")
        tree.heading("teto", text="Teto Balança")
        tree.heading("aet", text="Requer AET?")
        tree.heading("tara_ref", text="Tara Média Ref.")

        tree.column("codigo", width=120, anchor="w")
        tree.column("veiculo", width=260, anchor="w")
        tree.column("categoria", width=150, anchor="w")
        tree.column("eixos", width=60, anchor="center")
        tree.column("legal", width=100, anchor="e")
        tree.column("tol_5", width=90, anchor="e")
        tree.column("teto", width=100, anchor="e")
        tree.column("aet", width=90, anchor="center")
        tree.column("tara_ref", width=105, anchor="e")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_y.set)

        tree.grid(row=1, column=0, sticky="nsew", padx=(8, 0), pady=(0, 8))
        scrollbar_y.grid(row=1, column=1, sticky="ns", padx=(0, 8), pady=(0, 8))

        # Popula a tabela com todos os veículos CONTRAN
        for k, v in VEHICLES_DATABASE.items():
            if k == "PERSONALIZADO":
                continue
            limite = v["pbtc_legal"]
            tol = limite * 0.05
            teto = limite + tol
            tree.insert(
                "",
                "end",
                values=(
                    k,
                    v["nome"],
                    v["categoria"],
                    v["eixos"],
                    formatar_toneladas(limite),
                    f"+{formatar_kg(tol)}",
                    formatar_toneladas(teto),
                    "Sim (Obrigatória)" if v["requer_aet"] else "Não (Dispensada)",
                    formatar_kg(v["tara_media_referencia"])
                )
            )
