import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurações iniciais da página do painel
st.set_page_config(page_title="Painel Real-Time Debutantes", page_icon="📸", layout="wide")

CSV_FILE = "debu.csv"
COLUMNS = [
    "Nr de Ordem", "Nome da Debutante", 
    "Espera Família", "Família (Fotógrafos)", 
    "Espera Individual", "Individual (Fotógrafos)", 
    "Espera Estúdio Pós", "Estúdio Pós (Fotógrafos)"
]

# Lista de profissionais do estúdio
FOTOGRAFOS_DISPONIVEIS = [
     "Willian", "Gui", "Ribeiro", 
    "Vini Luz", "Fran", "Doris", "Rafa", "Rogério"
]

def inicializar_csv():
    """Cria a base debu.csv com os cabeçalhos caso não exista."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

def carregar_dados():
    """Carrega os dados garantindo a tipagem correta de listas e inteiros."""
    inicializar_csv()
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype={"Nr de Ordem": str})
        df = df.fillna("")
        return df.reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def salvar_dados(df):
    """Salva as modificações de volta no arquivo de persistência."""
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

def alternar_status(status_atual):
    """Ciclo de 3 estados para o controle de espera: Verde -> Branco -> Amarelo."""
    if status_atual == "VERDE":
        return "BRANCO"
    elif status_atual == "BRANCO":
        return "AMARELO"
    else:
        return "VERDE"

def obter_label_botao(status):
    """Retorna o emoji e o texto correto baseado no status atual."""
    if status == "VERDE":
        return "🟢 Concluído"
    elif status == "BRANCO":
        return "⚪ Chamar"
    else:
        return "🟡 Em Espera"

def gerar_pdf_reportlab(df):
    """Gera um relatório profissional em PDF usando ReportLab."""
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
    
    # Mapeamento do texto do status para legibilidade no PDF
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
        
    larguras_colunas = [45, 130, 75, 110, 75, 110, 75, 110]
    
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

# Fluxo de dados principal
df_dados = carregar_dados()

st.title("📸 Gestão de Sessões em Tempo Real — Debutantes")
st.markdown("Controle de fluxo de estúdio, gerenciamento de filas e alocação dinâmica de fotógrafos.")
st.markdown("---")

# Menu de controle lateral
st.sidebar.header("⚙️ Cadastro & Relatórios")
with st.sidebar.expander("➕ Adicionar Nova Debutante", expanded=True):
    with st.form("cadastro_form", clear_on_submit=True):
        nr_ordem = st.text_input("Nr de Ordem:")
        nome_deb = st.text_input("Nome da Debutante:")
        submit = st.form_submit_button("Inserir na Fila")
        
        if submit:
            if not nr_ordem.strip() or not nome_deb.strip():
                st.error("Preencha todos os campos obrigatórios.")
            elif nr_ordem.strip() in df_dados["Nr de Ordem"].astype(str).values:
                st.error("Este Número de Ordem já está cadastrado.")
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

# Seção de exportação de PDF
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
    st.sidebar.info("Adicione registros para liberar a emissão do PDF.")

# ----------------- PAINEL DINÂMICO EM TEMPO REAL -----------------
st.subheader("📋 Painel Operacional de Controle")

if df_dados.empty:
    st.info("Nenhuma debutante na fila de atendimento neste momento.")
else:
    # Cabeçalho customizado simulando uma Grid Table complexa
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6, h_col7, h_col8 = st.columns([1, 2.5, 1.2, 2.2, 1.2, 2.2, 1.2, 2.2])
    h_col1.markdown("**Nº Ordem**")
    h_col2.markdown("**Nome da Debutante**")
    h_col3.markdown("**Espera 1**")
    h_col4.markdown("**Família**")
    h_col5.markdown("**Espera 2**")
    h_col6.markdown("**Individual**")
    h_col7.markdown("**Espera 3**")
    h_col8.markdown("**Estúdio Pós**")
    st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border-color: #BDC3C7;'>", unsafe_allow_html=True)

    # Renderização dinâmica linha por linha
    for idx, row in df_dados.iterrows():
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2.5, 1.2, 2.2, 1.2, 2.2, 1.2, 2.2])
        
        # Identificadores fixos
        c1.text(f"#{row['Nr de Ordem']}")
        
        ###### Nome da debutante junto com botão de remover
        with c2:
            st.markdown(f"**{row['Nome da Debutante']}**")
            #if st.button("🗑️del", key=f"del_{idx}"):
            #    df_dados = df_dados.drop(idx).reset_index(drop=True)
            #    salvar_dados(df_dados)
            #   st.rerun()
        
        # --- CONTROLE ESPERA 1 (FAMÍLIA) ---
        label_esp1 = obter_label_botao(row["Espera Família"])
        if c3.button(label_esp1, key=f"esp1_{idx}", use_container_width=True):
            df_dados.at[idx, "Espera Família"] = alternar_status(row["Espera Família"])
            salvar_dados(df_dados)
            st.rerun()
            
        # --- SELEÇÃO FOTÓGRAFOS FAMÍLIA ---
        lista_f1 = [f.strip() for f in str(row["Família (Fotógrafos)"]).split(",") if f.strip() != ""]
        f1_sel = c4.multiselect(
            "Fotógrafos", FOTOGRAFOS_DISPONIVEIS, default=lista_f1, key=f"f1_{idx}", label_visibility="collapsed"
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
        f2_sel = c6.multiselect(
            "Fotógrafos", FOTOGRAFOS_DISPONIVEIS, default=lista_f2, key=f"f2_{idx}", label_visibility="collapsed"
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
        f3_sel = c8.multiselect(
            "Fotógrafos", FOTOGRAFOS_DISPONIVEIS, default=lista_f3, key=f"f3_{idx}", label_visibility="collapsed"
            )
        str_f3 = ", ".join(f3_sel)
        if str_f3 != str(row["Estúdio Pós (Fotógrafos)"]):
            df_dados.at[idx, "Estúdio Pós (Fotógrafos)"] = str_f3
            salvar_dados(df_dados)
            
            st.markdown("", unsafe_allow_html=True)
