"""
Janela Principal da Aplicação com Header Corporativo, Navegação em Abas e Gestão de Tema.
"""

from datetime import datetime
import customtkinter as ctk

from ui.theme import THEME_COLORS
from ui.tab_calculator import TabCalculator
from ui.tab_axles import TabAxles
from ui.tab_history import TabHistory
from ui.tab_reference import TabReference
from pbtc_core import ResultadoPBTC


class AppPBTC:
    def __init__(self):
        # Configurações globais do CustomTkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Janela principal
        self.root = ctk.CTk()
        self.root.title("PBTC Master - Gestão de Balança & Expedição (CONTRAN)")
        self.root.geometry("1180x750")
        self.root.minsize(1050, 680)

        self._criar_layout_principal()

    def _criar_layout_principal(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # ---------------------------------------------------------------------
        # 1. HEADER SUPERIOR CORPORATIVO
        # ---------------------------------------------------------------------
        header = ctk.CTkFrame(self.root, corner_radius=0, height=65, fg_color="#0F172A")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # Título e Logo
        f_titulo = ctk.CTkFrame(header, fg_color="transparent")
        f_titulo.grid(row=0, column=0, sticky="w", padx=20, pady=8)

        ctk.CTkLabel(
            f_titulo,
            text="🚛 PBTC MASTER",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w")

        ctk.CTkLabel(
            f_titulo,
            text="Sistema de Controle de Pesagem & Tolerâncias CONTRAN (Res. 882/2021 • Lei 14.229/2021)",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8"
        ).pack(anchor="w")

        # Lado Direito do Header: Alternador de Tema e Status
        f_acoes = ctk.CTkFrame(header, fg_color="transparent")
        f_acoes.grid(row=0, column=2, sticky="e", padx=20, pady=8)

        # Badge Operacional
        ctk.CTkLabel(
            f_acoes,
            text="🟢 Balança Conectada",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10B981"
        ).pack(side="left", padx=15)

        # Seletor de Tema
        self.switch_tema = ctk.CTkSwitch(
            f_acoes,
            text="Modo Escuro",
            command=self._alternar_tema,
            onvalue="Dark",
            offvalue="Light"
        )
        self.switch_tema.select()
        self.switch_tema.pack(side="left")

        # ---------------------------------------------------------------------
        # 2. SISTEMA DE NAVEGAÇÃO EM ABAS
        # ---------------------------------------------------------------------
        self.tabview = ctk.CTkTabview(self.root, corner_radius=10)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 5))

        tab_calc_frame = self.tabview.add("🚚 Calculadora PBTC & Expedição")
        tab_axle_frame = self.tabview.add("⚖️ Balança por Eixos (12,5%)")
        tab_hist_frame = self.tabview.add("📋 Histórico da Sessão")
        tab_refe_frame = self.tabview.add("📖 Legislação & Tabela CONTRAN")

        # Instancia as abas modulares
        self.tab_history = TabHistory(tab_hist_frame, self)
        self.tab_calculator = TabCalculator(tab_calc_frame, self)
        self.tab_axles = TabAxles(tab_axle_frame, self)
        self.tab_reference = TabReference(tab_refe_frame, self)

        # ---------------------------------------------------------------------
        # 3. BARRA DE STATUS INFERIOR (FOOTER)
        # ---------------------------------------------------------------------
        footer = ctk.CTkFrame(self.root, corner_radius=0, height=28, fg_color="#0F172A")
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            footer,
            text="PBTC Master v1.0.0 Pro | Operação de Balança Rodoviária & Grãos LDC",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=2)

        data_hoje = datetime.now().strftime("%d/%m/%Y")
        ctk.CTkLabel(
            footer,
            text=f"Data: {data_hoje} • Status: Operação Normal",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        ).grid(row=0, column=2, sticky="e", padx=15, pady=2)

    def _alternar_tema(self):
        novo_tema = self.switch_tema.get()
        ctk.set_appearance_mode(novo_tema)

    def adicionar_ao_historico(self, resultado: ResultadoPBTC):
        """Encaminha o resultado de pesagem para a aba de histórico."""
        self.tab_history.adicionar_registro(resultado)
        # Mostra feedback no ticket ou popup
        from tkinter import messagebox
        messagebox.showinfo(
            "Histórico Atualizado",
            f"Carregamento registrado com sucesso no histórico da sessão!\n"
            f"Veículo: {resultado.veiculo_nome}\n"
            f"Status: {resultado.status}"
        )

    def run(self):
        """Inicia o loop da aplicação."""
        self.root.mainloop()
