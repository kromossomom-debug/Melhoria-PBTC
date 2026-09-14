"""
Aba de Histórico de Pesagens da Sessão e Exportação para Relatórios (CSV/Excel).
"""

import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List
import customtkinter as ctk

from pbtc_core import ResultadoPBTC
from ui.theme import THEME_COLORS, formatar_kg, formatar_toneladas


class TabHistory:
    def __init__(self, parent_frame: ctk.CTkFrame, app_instance):
        self.frame = parent_frame
        self.app = app_instance
        self.historico: List[ResultadoPBTC] = []

        self._criar_layout()

    def _criar_layout(self):
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)

        # BARRA DE RESUMO / KPIS DO TURNO (TOPO)
        kpi_bar = ctk.CTkFrame(self.frame, corner_radius=8)
        kpi_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        kpi_bar.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.kpi_total = self._criar_kpi(kpi_bar, 0, "Pesagens Realizadas", "0", "#FFFFFF")
        self.kpi_conforme = self._criar_kpi(kpi_bar, 1, "Liberados (100% OK)", "0", THEME_COLORS["success"])
        self.kpi_tolerancia = self._criar_kpi(kpi_bar, 2, "Em Tolerância (5%)", "0", THEME_COLORS["warning"])
        self.kpi_excesso = self._criar_kpi(kpi_bar, 3, "Reprovados / Excesso", "0", THEME_COLORS["danger"])
        self.kpi_volume = self._criar_kpi(kpi_bar, 4, "Volume Líquido Total", "0,00 t", THEME_COLORS["accent_cyan"])

        # BARRA DE AÇÕES E PESQUISA
        action_bar = ctk.CTkFrame(self.frame, corner_radius=8, fg_color="transparent")
        action_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        action_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(action_bar, text="🔍 Buscar:").grid(row=0, column=0, padx=(5, 5))
        self.entry_busca = ctk.CTkEntry(action_bar, placeholder_text="Filtrar por Placa, Romaneio, Motorista ou Produto...")
        self.entry_busca.grid(row=0, column=1, sticky="ew", padx=5)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._atualizar_tabela())

        btn_exportar = ctk.CTkButton(
            action_bar,
            text="📊 Exportar CSV (Excel)",
            fg_color="#059669",
            hover_color="#047857",
            command=self._exportar_csv
        )
        btn_exportar.grid(row=0, column=2, padx=5)

        btn_ver_ticket = ctk.CTkButton(
            action_bar,
            text="📄 Ver Ticket",
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_hover"],
            command=self._ver_ticket_selecionado
        )
        btn_ver_ticket.grid(row=0, column=3, padx=5)

        btn_limpar = ctk.CTkButton(
            action_bar,
            text="🗑️ Limpar",
            fg_color=THEME_COLORS["secondary"],
            width=90,
            command=self._limpar_historico
        )
        btn_limpar.grid(row=0, column=4, padx=(5, 5))

        # TABELA DE DADOS (TREEVIEW ESTILIZADA)
        frame_tabela = ctk.CTkFrame(self.frame, corner_radius=8)
        frame_tabela.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        frame_tabela.grid_columnconfigure(0, weight=1)
        frame_tabela.grid_rowconfigure(0, weight=1)

        # Configura estilo do Treeview para se integrar ao tema moderno
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#1E293B",
            foreground="#FFFFFF",
            fieldbackground="#1E293B",
            rowheight=28,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#0F172A",
            foreground="#38BDF8",
            font=("Segoe UI", 10, "bold")
        )
        style.map("Treeview", background=[("selected", "#1D4ED8")])

        colunas = (
            "hora", "romaneio", "placa", "veiculo", "produto",
            "tara", "liquido", "pbtc", "limite", "status", "transbordo"
        )
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", selectmode="browse")

        self.tree.heading("hora", text="Horário")
        self.tree.heading("romaneio", text="Romaneio")
        self.tree.heading("placa", text="Placa")
        self.tree.heading("veiculo", text="Configuração")
        self.tree.heading("produto", text="Produto")
        self.tree.heading("tara", text="Tara (kg)")
        self.tree.heading("liquido", text="Líquido (kg)")
        self.tree.heading("pbtc", text="PBTC Total (kg)")
        self.tree.heading("limite", text="Limite Legal")
        self.tree.heading("status", text="Status")
        self.tree.heading("transbordo", text="Transbordo")

        self.tree.column("hora", width=110, anchor="center")
        self.tree.column("romaneio", width=90, anchor="center")
        self.tree.column("placa", width=90, anchor="center")
        self.tree.column("veiculo", width=160, anchor="w")
        self.tree.column("produto", width=120, anchor="w")
        self.tree.column("tara", width=90, anchor="e")
        self.tree.column("liquido", width=90, anchor="e")
        self.tree.column("pbtc", width=105, anchor="e")
        self.tree.column("limite", width=95, anchor="e")
        self.tree.column("status", width=130, anchor="center")
        self.tree.column("transbordo", width=95, anchor="e")

        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scrollbar_y.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        self.tree.bind("<Double-1>", lambda e: self._ver_ticket_selecionado())

    def _criar_kpi(self, parent, col, titulo, valor_inicial, cor):
        card = ctk.CTkFrame(parent, corner_radius=6, border_width=1, border_color="#334155")
        card.grid(row=0, column=col, sticky="ew", padx=4, pady=6)

        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"]).pack(anchor="w", padx=8, pady=(4, 0))
        lbl_v = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=16, weight="bold"), text_color=cor)
        lbl_v.pack(anchor="w", padx=8, pady=(0, 4))
        return lbl_v

    def adicionar_registro(self, res: ResultadoPBTC):
        """Adiciona um novo registro de pesagem ao histórico e atualiza a view."""
        self.historico.insert(0, res)
        self._atualizar_tabela()
        self._atualizar_kpis()

    def _atualizar_tabela(self):
        # Limpa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        termo = self.entry_busca.get().strip().lower()

        for idx, r in enumerate(self.historico):
            # Filtro de busca
            texto_busca = f"{r.placa_cavalo} {r.placa_carreta} {r.romaneio} {r.motorista} {r.produto} {r.veiculo_nome}".lower()
            if termo and termo not in texto_busca:
                continue

            placa_exibicao = r.placa_cavalo or r.placa_carreta or "N/D"
            transbordo_txt = f"{r.transbordo_obrigatorio_kg:,.0f} kg".replace(",", ".") if r.transbordo_obrigatorio_kg > 0 else "-"

            status_simples = "🟢 Conforme" if r.status_codigo == "OK" else ("🟡 Tolerância" if r.status_codigo == "ALERTA" else "🔴 Excesso")

            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    r.timestamp.split(" ")[-1] if " " in r.timestamp else r.timestamp,
                    r.romaneio or "-",
                    placa_exibicao,
                    r.veiculo_nome,
                    r.produto or "-",
                    f"{r.tara_kg:,.0f}".replace(",", "."),
                    f"{r.carga_liquida_kg:,.0f}".replace(",", "."),
                    f"{r.pbtc_aferido_kg:,.0f}".replace(",", "."),
                    f"{r.limite_legal_kg:,.0f}".replace(",", "."),
                    status_simples,
                    transbordo_txt
                )
            )

    def _atualizar_kpis(self):
        total = len(self.historico)
        conforme = sum(1 for r in self.historico if r.status_codigo == "OK")
        tolerancia = sum(1 for r in self.historico if r.status_codigo == "ALERTA")
        excesso = sum(1 for r in self.historico if r.status_codigo == "EXCESSO")
        vol_total = sum(r.carga_liquida_kg for r in self.historico)

        self.kpi_total.configure(text=str(total))
        self.kpi_conforme.configure(text=str(conforme))
        self.kpi_tolerancia.configure(text=str(tolerancia))
        self.kpi_excesso.configure(text=str(excesso))
        self.kpi_volume.configure(text=formatar_toneladas(vol_total))

    def _ver_ticket_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione uma pesagem na tabela para visualizar o ticket.")
            return

        idx = int(selecionado[0])
        if 0 <= idx < len(self.historico):
            res = self.historico[idx]
            from pbtc_core import gerar_ticket_pesagem_texto

            # Janela de diálogo com o ticket
            janela = ctk.CTkToplevel(self.frame)
            janela.title(f"Ticket de Pesagem - {res.romaneio or res.placa_cavalo or 'Registro'}")
            janela.geometry("540x580")
            janela.transient(self.app.root)

            txt = ctk.CTkTextbox(janela, font=ctk.CTkFont(family="Consolas", size=11))
            txt.pack(fill="both", expand=True, padx=12, pady=12)
            txt.insert("0.0", gerar_ticket_pesagem_texto(res))

    def _exportar_csv(self):
        if not self.historico:
            messagebox.showinfo("Aviso", "Nenhum registro para exportar.")
            return

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Planilha CSV", "*.csv")],
            initialfile="Historico_Pesagens_PBTC.csv"
        )
        if not arquivo:
            return

        try:
            # Exporta com BOM UTF-8 e delimitador ';' para abrir perfeitamente no Excel brasileiro
            with open(arquivo, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                # Cabeçalhos
                writer.writerow([
                    "Data_Hora", "Romaneio", "Motorista", "Placa_Cavalo", "Placa_Carreta",
                    "Produto", "Veiculo_Nome", "Categoria", "Eixos",
                    "Tara_kg", "Carga_Liquida_kg", "PBTC_Aferido_kg",
                    "Limite_Legal_kg", "Teto_Balanca_5pct_kg", "Status_Liberacao",
                    "Saldo_Disponivel_kg", "Excesso_Legal_kg", "Transbordo_Obrigatorio_kg",
                    "Ocupacao_Balanca_pct", "Observacoes"
                ])

                for r in self.historico:
                    writer.writerow([
                        r.timestamp, r.romaneio, r.motorista, r.placa_cavalo, r.placa_carreta,
                        r.produto, r.veiculo_nome, r.categoria, r.eixos,
                        f"{r.tara_kg:.0f}", f"{r.carga_liquida_kg:.0f}", f"{r.pbtc_aferido_kg:.0f}",
                        f"{r.limite_legal_kg:.0f}", f"{r.limite_balanca_kg:.0f}", r.status,
                        f"{r.saldo_carga_disponivel_kg:.0f}", f"{r.excesso_sobre_legal_kg:.0f}",
                        f"{r.transbordo_obrigatorio_kg:.0f}", f"{r.percentual_utilizacao_balanca:.2f}".replace(".", ","),
                        r.observacoes
                    ])

            messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso para:\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", f"Falha ao gerar arquivo CSV:\n{e}")

    def _limpar_historico(self):
        if not self.historico:
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar todos os registros de pesagem da sessão atual?"):
            self.historico.clear()
            self._atualizar_tabela()
            self._atualizar_kpis()
