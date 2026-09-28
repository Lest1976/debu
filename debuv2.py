import streamlit as st
import pandas as pd
import os

# Configurações iniciais da página do painel
st.set_page_config(page_title="Painel Real-Time Debutantes", page_icon="📸", layout="wide")

CSV_FILE = "debu.csv"
FOTO_FILE = "fotografos.csv"

COLUMNS = [
    "Nr de Ordem", "Nome da Debutante", 
    "Espera Família", "Família (Fotógrafos)", 
    "Espera Individual", "Individual (Fotógrafos)", 
    "Espera Estúdio Pós", "Estúdio Pós (Fotógrafos)"
]

# ----------------- GERENCIAMENTO DOS ARQUIVOS (BBDD) -----------------
def inicializar_arquivos():
    """Cria os arquivos CSV com os cabeçalhos caso não existam."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(FOTO_FILE):
        df_foto = pd.DataFrame({"Nome": ["Will", "Dani", "Gui", "Ribeiro", "Rafa", "Fran", "Doris"]})
        df_foto.to_csv(FOTO_FILE, index=False, encoding='utf-8-sig')

def carregar_dados():
    inicializar_arquivos()
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype={"Nr de Ordem": str})
        return df.fillna("").reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def carregar_fotografos():
    inicializar_arquivos()
    try:
        df = pd.read_csv(FOTO_FILE, encoding='utf-8-sig')
        return sorted(df["Nome"].dropna().unique().tolist())
    except Exception:
        return ["Will", "Dani", "Gui", "Ribeiro", "Rafa", "Fran", "Doris"]

def salvar_dados(df):
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

def salvar_fotografos(lista_fotos):
    df = pd.DataFrame({"Nome": lista_fotos})
    df.to_csv(FOTO_FILE, index=False, encoding='utf-8-sig')

# ----------------- CONTROLES DE STATUS -----------------
def alternar_status(status_atual):
    if status_atual == "VERDE":
        return "BRANCO"
    elif status_atual == "BRANCO":
        return "AMARELO"
    else:
        return "VERDE"

def obter_label_botao(status):
    if status == "VERDE":
        return "🟢 Concluído"
    elif status == "BRANCO":
        return "⚪ Chamar"
    else:
        return "🟡 Na Fila"

# ----------------- GERADOR DE RELATÓRIO -----------------
def gerar_pdf_reportlab(df):
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    pdf_path = "relatorio_sessoes_debutantes.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#2C3E50'), alignment=1
    )
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=9, leading=11)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.white, fontName="Helvetica-Bold")
    
    story.append(Paragraph("<b>PAINEL OPERACIONAL DE SESSÕES - DEBUTANTES</b>", title_style))
    story.append(Spacer(1, 15))
    
    def formatar_status_pdf(status):
        if status == "VERDE": return "CONCLUÍDO"
        if status == "AMARELO": return "EM ESPERA"
        return "CHAMAR"

    table_data = [[Paragraph(col, header_style) for col in COLUMNS]]
    for _, row in df.iterrows():
        row_cells = [
            Paragraph(str(row["Nr de Ordem"]), normal_style),
            Paragraph(str(row["Nome da Debutante"]), normal_style),
            Paragraph(formatar_status_pdf(row["Espera Família"]), normal_style),
            Paragraph(str(row["Família (Fotógrafos)"]) if row["Família (Fotógrafos)"] else "-", normal_style),
            Paragraph(formatar_status_pdf(row["Espera Individual"]), normal_style),
            Paragraph(str(row["Individual (Fotógrafos)"]) if row["Individual (Fotógrafos)"] else "-", normal_style),
            Paragraph(formatar_status_pdf(row["Espera Estúdio Pós"]), normal_style),
            Paragraph(str(row["Estúdio Pós (Fotógrafos)"]) if row["Estúdio Pós (Fotógrafos)"] else "-", normal_style),
        ]
        table_data.append(row_cells)
        
    larguras_colunas = [60, 140, 75, 100, 75, 100, 75, 100]
    t = Table(table_data, colWidths=larguras_colunas, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9FA')])
    ]))
    
    story.append(t)
    doc.build(story)
    return pdf_path

# Carregamento inicial da memória/arquivos
df_dados = carregar_dados()
fotografos_disponiveis = carregar_fotografos()

st.title("📸 Gestão de Sessões em Tempo Real — Debutantes")
st.markdown("Controle de fluxo de estúdio, gerenciamento de filas e equipe de fotógrafos.")
st.markdown("---")

# ----------------- MENU LATERAL EXTERNO -----------------
st.sidebar.header("⚙️ Painel de Configurações")

# ABA 1: Cadastro de Debutantes
with st.sidebar.expander("➕ Adicionar Nova Debutante", expanded=False):
    with st.form("cadastro_form", clear_on_submit=True):
        nr_ordem = st.text_input("Nr de Ordem:")
        nome_deb = st.text_input("Nome da Debutante:")
        submit = st.form_submit_button("Inserir na Fila")
        
        if submit:
            if not nr_ordem.strip() or not nome_deb.strip():
                st.error("Preencha todos os campos.")
            elif nr_ordem.strip() in df_dados["Nr de Ordem"].astype(str).values:
                st.error("Este Número de Ordem já existe.")
            else:
                novo_reg = pd.DataFrame([{
                    "Nr de Ordem": nr_ordem.strip(),
                    "Nome da Debutante": nome_deb.strip(),
                    "Espera Família": "BRANCO",
                    "Família (Fotógrafos)": "",
                    "Espera Individual": "BRANCO",
                    "Individual (Fotógrafos)": "",
                    "Espera Estúdio Pós": "BRANCO",
                    "Estúdio Pós (Fotógrafos)": ""
                }])
                df_dados = pd.concat([df_dados, novo_reg], ignore_index=True)
                salvar_dados(df_dados)
                st.success("Debutante incluída!")
                st.rerun()

# ABA 2: EDITAR OU REMOVER DEBUTANTE
with st.sidebar.expander("✏️ Editar / ❌ Remover Debutante", expanded=False):
    if df_dados.empty:
        st.info("Nenhuma debutante na fila para gerenciar.")
    else:
        lista_opcoes_deb = [
            f"{idx} - #{row['Nr de Ordem']} {row['Nome da Debutante']}"
            for idx, row in df_dados.iterrows()
        ]
        deb_selecionada = st.selectbox("Selecione a Debutante:", lista_opcoes_deb, key="sb_gerenciar_deb")
        idx_gerenciar = int(deb_selecionada.split(" - ")[0])
        dados_atuais_deb = df_dados.loc[idx_gerenciar]
        
        with st.form("form_gerenciar_deb"):
            edit_nr_ordem = st.text_input("Alterar Nr de Ordem:", value=str(dados_atuais_deb["Nr de Ordem"]))
            edit_nome_deb = st.text_input("Alterar Nome da Debutante:", value=str(dados_atuais_deb["Nome da Debutante"]))
            
            col_btn_ed, col_btn_rem = st.columns(2)
            with col_btn_ed:
                btn_gravar_ed = st.form_submit_button("Gravar Alterações")
            with col_btn_rem:
                btn_remover_deb = st.form_submit_button("❌ Excluir Registro", type="primary")
                
            if btn_gravar_ed:
                if not edit_nr_ordem.strip() or not edit_nome_deb.strip():
                    st.error("Campos não podem ficar vazios.")
                else:
                    df_dados.at[idx_gerenciar, "Nr de Ordem"] = edit_nr_ordem.strip()
                    df_dados.at[idx_gerenciar, "Nome da Debutante"] = edit_nome_deb.strip()
                    salvar_dados(df_dados)
                    st.success("Dados alterados com sucesso!")
                    st.rerun()
                    
            if btn_remover_deb:
                df_dados = df_dados.drop(idx_gerenciar).reset_index(drop=True)
                salvar_dados(df_dados)
                st.success("Debutante removida do sistema.")
                st.rerun()

# ABA 3: Cadastro da Equipe de Fotógrafos
with st.sidebar.expander("👤 Equipe de Fotógrafos", expanded=False):
    st.markdown("**Adicionar Profissional**")
    novo_foto = st.text_input("Nome do Fotógrafo:", key="input_novo_foto")
    if st.button("Cadastrar Fotógrafo"):
        if novo_foto.strip() != "":
            if novo_foto.strip() not in fotografos_disponiveis:
                fotografos_disponiveis.append(novo_foto.strip())
                salvar_fotografos(fotografos_disponiveis)
                st.success(f"{novo_foto.strip()} adicionado!")
                st.rerun()
            else:
                st.warning("Este profissional já está cadastrado.")
        else:
            st.error("Digite um nome válido.")
            
    st.markdown("---")
    st.markdown("**Remover Profissional**")
    if fotografos_disponiveis:
        foto_remover = st.selectbox("Selecione para remover:", fotografos_disponiveis)
        if st.button("Excluir Cadastro", type="secondary"):
            fotografos_disponiveis.remove(foto_remover)
            salvar_fotografos(fotografos_disponiveis)
            st.success("Profissional removido.")
            st.rerun()
    else:
        st.info("Nenhum fotógrafo cadastrado.")

# ABA 4: Emissão de Relatório PDF
st.sidebar.markdown("---")
st.sidebar.header("📄 Exportações")
if not df_dados.empty:
    if st.sidebar.button("Gerar Relatório PDF"):
        try:
            caminho_pdf = gerar_pdf_reportlab(df_dados)
            with open(caminho_pdf, "rb") as f:
                st.sidebar.download_button(
                    label="📥 Baixar Relatório PDF",
                    data=f,
                    file_name="relatorio_sessoes_debutantes.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.sidebar.error(f"Erro ao processar PDF: {e}")
else:
    st.sidebar.info("Adicione registros para liberar o PDF.")

# ----------------- PAINEL DINÂMICO EM TEMPO REAL -----------------
st.subheader("📋 Painel Operacional de Controle")

if df_dados.empty:
    st.info("Nenhuma debutante na fila de atendimento neste momento.")
else:
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6, h_col7, h_col8 = st.columns([1, 2.5, 1.2, 2.2, 1.2, 2.2, 1.2, 2.2])
    h_col1.markdown("**Nº Ordem**")
    h_col2.markdown("**Nome da Debutante**")
    h_col3.markdown("**Espera 1**")
    h_col4.markdown("**Estúdio Família**")
    h_col5.markdown("**Espera 2**")
    h_col6.markdown("**Estúdio Individual**")
    h_col7.markdown("**Espera 3**")
    h_col8.markdown("**Estúdio Pós**")
    st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border-color: #BDC3C7;'>", unsafe_allow_html=True)

    for idx, row in df_dados.iterrows():
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2.5, 1.2, 2.2, 1.2, 2.2, 1.2, 2.2])
        
        c1.text(f"#{row['Nr de Ordem']}")
        
        with c2:
            st.markdown(f"**{row['Nome da Debutante']}**")
        #    if st.button("🗑️ Concluir Geral", key=f"del_{idx}"):
        #        df_dados = df_dados.drop(idx).reset_index(drop=True)
        #        salvar_dados(df_dados)
        #        st.rerun()
        
        # --- CONTROLE ESPERA 1 (FAMÍLIA) ---
        label_esp1 = obter_label_botao(row["Espera Família"])
        if c3.button(label_esp1, key=f"esp1_{idx}", use_container_width=True):
            df_dados.at[idx, "Espera Família"] = alternar_status(row["Espera Família"])
            salvar_dados(df_dados)
            st.rerun()
            
        # --- SELEÇÃO FOTÓGRAFOS FAMÍLIA ---
        lista_f1 = [f.strip() for f in str(row["Família (Fotógrafos)"]).split(",") if f.strip() != ""]
        lista_f1 = [f for f in lista_f1 if f in fotografos_disponiveis]
        f1_sel = c4.multiselect(
            "Fotógrafos", fotografos_disponiveis, default=lista_f1, key=f"f1_{idx}", label_visibility="collapsed"
        )
        str_f1 = ", ".join(f1_sel)
        if str_f1 != str(row["Família (Fotógrafos)"]):
            df_dados.at[idx, "Família (Fotógrafos)"] = str_f1
            salvar_dados(df_dados)
            
        # --- CONTROLE ESPERA 2 (INDIVIDUAL) ---
        label_esp2 = obter_label_botao(row["Espera Individual"])
        if c5.button(label_esp2, key=f"esp2_{idx}", use_container_width=True):
            df_dados.at[idx, "Espera Individual"] = alternar_status(row["Espera Individual"])
            salvar_dados(df_dados)
            st.rerun()
            
        # --- SELEÇÃO FOTÓGRAFOS INDIVIDUAL ---
        lista_f2 = [f.strip() for f in str(row["Individual (Fotógrafos)"]).split(",") if f.strip() != ""]
        lista_f2 = [f for f in lista_f2 if f in fotografos_disponiveis]
        f2_sel = c6.multiselect(
            "Fotógrafos", fotografos_disponiveis, default=lista_f2, key=f"f2_{idx}", label_visibility="collapsed"
        )
        str_f2 = ", ".join(f2_sel)
        if str_f2 != str(row["Individual (Fotógrafos)"]):
            df_dados.at[idx, "Individual (Fotógrafos)"] = str_f2
            salvar_dados(df_dados)

        # --- CONTROLE ESPERA 3 (ESTÚDIO PÓS) ---
        label_esp3 = obter_label_botao(row["Espera Estúdio Pós"])
        if c7.button(label_esp3, key=f"esp3_{idx}", use_container_width=True):
            df_dados.at[idx, "Espera Estúdio Pós"] = alternar_status(row["Espera Estúdio Pós"])
            salvar_dados(df_dados)
            st.rerun()
            
        # --- SELEÇÃO FOTÓGRAFOS ESTÚDIO PÓS ---
        lista_f3 = [f.strip() for f in str(row["Estúdio Pós (Fotógrafos)"]).split(",") if f.strip() != ""]
        lista_f3 = [f for f in lista_f3 if f in fotografos_disponiveis]
        f3_sel = c8.multiselect(
            "Fotógrafos", fotografos_disponiveis, default=lista_f3, key=f"f3_{idx}", label_visibility="collapsed"
        )
        str_f3 = ", ".join(f3_sel)
        if str_f3 != str(row["Estúdio Pós (Fotógrafos)"]):
            df_dados.at[idx, "Estúdio Pós (Fotógrafos)"] = str_f3
            salvar_dados(df_dados)
        
        st.markdown("<hr style='margin: 0.4rem 0; border-color: #ECEFF1;'>", unsafe_allow_html=True)
