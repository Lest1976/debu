#pip install streamlit-autorefresh reportlab pandas openpyxl
#streamlit run debuv6.py


import streamlit as st
import pandas as pd
import os

# Configurações iniciais da página do painel
st.set_page_config(page_title="Painel Real-Time Debutantes v6", page_icon="📸", layout="wide")

# Tenta importar o autorefresh oficial para sincronismo real-time automático nas TVs
try:
    from streamlit_autorefresh import st_autorefresh
    # Atualiza o painel de forma automática a cada 10 segundos
    st_autorefresh(interval=10000, limit=1000, key="auto_refresh_painel")
except ImportError:
    pass

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
    """Cria os arquivos CSV com os cabeçalhos caso não exista."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(FOTO_FILE):
        df_foto = pd.DataFrame({"Nome": ["Will", "Dani", "Gui", "Ribeiro", "Fran", "Doris", "Rafa", "Rogério", "Vini Luz"]})
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
        return ["Will", "Dani", "Gui", "Ribeiro", "Fran", "Doris", "Rafa", "Rogério", "Vini Luz"]

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
        if status == "VERDE": return "Concluído"
        if status == "AMARELO": return "Na Fila"
        return "Chamar"

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
        
    larguras_colunas = [60, 150, 75, 110, 75, 110, 75, 110]
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

st.sidebar.header("🔐 Controle de Acesso")
perfil = st.sidebar.selectbox("Perfil de Usuário:", ["Visualizador", "Fotógrafo", "Coordenador"])

pode_alterar_painel = False
pode_gerenciar_bbdd = False

if perfil == "Coordenador":
    senha_coord = st.sidebar.text_input("Senha Coordenador:", type="password", key="senha_coordenador")
    if senha_coord == "silvas":
        pode_alterar_painel = True
        pode_gerenciar_bbdd = True
        st.sidebar.success("🔓 Modo Coordenador Ativo")
    elif senha_coord != "":
        st.sidebar.error("❌ Senha Incorreta")
elif perfil == "Fotógrafo":
    senha_foto = st.sidebar.text_input("Senha Fotógrafo:", type="password", key="senha_fotografo")
    if senha_foto == "foto":
        pode_alterar_painel = True
        pode_gerenciar_bbdd = False
        st.sidebar.success("📸 Modo Fotógrafo Ativo")
    elif senha_foto != "":
        st.sidebar.error("❌ Senha Incorreta")
else:
    pode_alterar_painel = False
    pode_gerenciar_bbdd = False
    st.sidebar.info("👁️ Modo Visualização (Apenas Leitura)")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Painel de Configurações")

# ABA 1: Cadastro de Debutantes (Apenas Coordenador)
with st.sidebar.expander("➕ Adicionar Nova Debutante", expanded=False):
    if not pode_gerenciar_bbdd:
        st.warning("🔒 Apenas Coordenadores podem incluir novas debutantes.")
    else:
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

# ABA 2: EDITAR OU REMOVER DEBUTANTE (Apenas Coordenador)
with st.sidebar.expander("✏️ Editar / ❌ Remover Debutante", expanded=False):
    if not pode_gerenciar_bbdd:
        st.warning("🔒 Apenas Coordenadores podem editar ou remover registros.")
    elif df_dados.empty:
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
            
            btn_gravar_ed = st.form_submit_button("Gravar Alterações")
            
            if btn_gravar_ed:
                if not edit_nr_ordem.strip() or not edit_nome_deb.strip():
                    st.error("Campos não podem ficar vazios.")
                else:
                    df_dados.at[idx_gerenciar, "Nr de Ordem"] = edit_nr_ordem.strip()
                    df_dados.at[idx_gerenciar, "Nome da Debutante"] = edit_nome_deb.strip()
                    salvar_dados(df_dados)
                    st.success("Dados alterados com sucesso!")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("⚠️ **Zona de Exclusão Definitiva**")
        confirmar_exclusao = st.checkbox("Estou ciente de que esta ação removerá a debutante permanentemente.", key=f"check_del_{idx_gerenciar}")
        
        if st.button("❌ Excluir Registro Definitivamente", type="primary"):
            if confirmar_exclusao:
                df_dados = df_dados.drop(idx_gerenciar).reset_index(drop=True)
                salvar_dados(df_dados)
                st.success("Debutante removida com sucesso.")
                st.rerun()
            else:
                st.error("Marque a caixa de confirmação acima para autorizar o apagamento.")



        #############################################################################################################################################   
# ABA 3: Cadastro da Equipe de Fotógrafos (Apenas Coordenador)
with st.sidebar.expander("👤 Equipe de Fotógrafos", expanded=False):
    if not pode_gerenciar_bbdd:
        st.warning("🔒 Apenas Coordenadores podem gerenciar a equipe de fotógrafos.")
    else:
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
            confirmar_foto_del = st.checkbox("Confirmar remoção do profissional da lista global.")
            if st.button("Excluir Cadastro", type="secondary"):
                if confirmar_foto_del:
                    fotografos_disponiveis.remove(foto_remover)
                    salvar_fotografos(fotografos_disponiveis)
                    st.success("Profissional removido.")
                    st.rerun()
                else:
                    st.error("Marque a caixa de confirmação para remover o fotógrafo.")
        else:
            st.info("Nenhum fotógrafo cadastrado.")
             
             # ABA 4: Emissão de Relatório PDF (Disponível para todos)
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
             
        ##############################################################################################################################################
        #----------------- PAINEL DINÂMICO EM TEMPO REAL -----------------
st.subheader("📋 Painel Operacional de Controle")

if df_dados.empty:
    st.info("Nenhuma debutante na fila de atendimento neste momento.")
else:
    # Criação do cabeçalho da Grid com proporções exatas para cada coluna
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

    # Armazena o estado de travamento baseado no perfil (Visualizador desabilita)
    desabilitar_botoes = not pode_alterar_painel

    # Varredura linha por linha para renderização dinâmica
    for idx, row in df_dados.iterrows():
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 2.5, 1.2, 2.2, 1.2, 2.2, 1.2, 2.2])
        
        # 1. Número de Ordem
        c1.text(f"#{row['Nr de Ordem']}")
        
        # 2. Nome da Debutante + Botão de Conclusão Rápida (Apenas Coordenador)
        with c2:
            st.markdown(f"**{row['Nome da Debutante']}**")
        #    if pode_gerenciar_bbdd:
        #        if st.button("🗑️ Concluir Geral", key=f"del_{idx}"):
        #            df_dados = df_dados.drop(idx).reset_index(drop=True)
        #            salvar_dados(df_dados)
        #            st.rerun()




         #############################################################################################################################################   
             
                # --- CONTROLE ESPERA 1 (FAMÍLIA) ---
        label_esp1 = obter_label_botao(row["Espera Família"])
        if pode_alterar_painel:
            if c3.button(label_esp1, key=f"esp1_{idx}", use_container_width=True):
                df_dados.at[idx, "Espera Família"] = alternar_status(row["Espera Família"])
                salvar_dados(df_dados)
                st.rerun()
        else:
            c3.markdown(f"<div style='text-align:center; padding:6px; font-weight:bold; font-size:15px;'>{label_esp1}</div>", unsafe_allow_html=True)
            
        # --- SELEÇÃO FOTÓGRAFOS FAMÍLIA ---
        lista_f1 = [f.strip() for f in str(row["Família (Fotógrafos)"]).split(",") if f.strip() != ""]
        lista_f1 = [f for f in lista_f1 if f in fotografos_disponiveis]
        if pode_alterar_painel:
            f1_sel = c4.multiselect(
                "Fotógrafos", fotografos_disponiveis, default=lista_f1, key=f"f1_{idx}", label_visibility="collapsed"
            )
            str_f1 = ", ".join(f1_sel)
            if str_f1 != str(row["Família (Fotógrafos)"]):
                df_dados.at[idx, "Família (Fotógrafos)"] = str_f1
                salvar_dados(df_dados)
        else:
            txt_f1 = ", ".join(lista_f1) if lista_f1 else "Nenhum alocado"
            c4.markdown(f"<div style='padding:6px; color:#1A252F; font-size:14px;'>👤 {txt_f1}</div>", unsafe_allow_html=True)
            
        # --- CONTROLE ESPERA 2 (INDIVIDUAL) ---
        label_esp2 = obter_label_botao(row["Espera Individual"])
        if pode_alterar_painel:
            if c5.button(label_esp2, key=f"esp2_{idx}", use_container_width=True):
                df_dados.at[idx, "Espera Individual"] = alternar_status(row["Espera Individual"])
                salvar_dados(df_dados)
                st.rerun()
        else:
            c5.markdown(f"<div style='text-align:center; padding:6px; font-weight:bold; font-size:15px;'>{label_esp2}</div>", unsafe_allow_html=True)
            
        # --- SELEÇÃO FOTÓGRAFOS INDIVIDUAL ---
        lista_f2 = [f.strip() for f in str(row["Individual (Fotógrafos)"]).split(",") if f.strip() != ""]
        lista_f2 = [f for f in lista_f2 if f in fotografos_disponiveis]
        if pode_alterar_painel:
            f2_sel = c6.multiselect(
                "Fotógrafos", fotografos_disponiveis, default=lista_f2, key=f"f2_{idx}", label_visibility="collapsed"
            )
            str_f2 = ", ".join(f2_sel)
            if str_f2 != str(row["Individual (Fotógrafos)"]):
                df_dados.at[idx, "Individual (Fotógrafos)"] = str_f2
                salvar_dados(df_dados)
        else:
            txt_f2 = ", ".join(lista_f2) if lista_f2 else "Nenhum alocado"
            c6.markdown(f"<div style='padding:6px; color:#1A252F; font-size:14px;'>👤 {txt_f2}</div>", unsafe_allow_html=True)

        # --- CONTROLE ESPERA 3 (ESTÚDIO PÓS) ---
        label_esp3 = obter_label_botao(row["Espera Estúdio Pós"])
        if pode_alterar_painel:
            if c7.button(label_esp3, key=f"esp3_{idx}", use_container_width=True):
                df_dados.at[idx, "Espera Estúdio Pós"] = alternar_status(row["Espera Estúdio Pós"])
                salvar_dados(df_dados)
                st.rerun()
        else:
            c7.markdown(f"<div style='text-align:center; padding:6px; font-weight:bold; font-size:15px;'>{label_esp3}</div>", unsafe_allow_html=True)
            
        # --- SELEÇÃO FOTÓGRAFOS ESTÚDIO PÓS ---
        lista_f3 = [f.strip() for f in str(row["Estúdio Pós (Fotógrafos)"]).split(",") if f.strip() != ""]
        lista_f3 = [f for f in lista_f3 if f in fotografos_disponiveis]
        if pode_alterar_painel:
            f3_sel = c8.multiselect(
                "Fotógrafos", fotografos_disponiveis, default=lista_f3, key=f"f3_{idx}", label_visibility="collapsed"
            )
            str_f3 = ", ".join(f3_sel)
            if str_f3 != str(row["Estúdio Pós (Fotógrafos)"]):
                df_dados.at[idx, "Estúdio Pós (Fotógrafos)"] = str_f3
                salvar_dados(df_dados)
        else:
            txt_f3 = ", ".join(lista_f3) if lista_f3 else "Nenhum alocado"
            c8.markdown(f"<div style='padding:6px; color:#1A252F; font-size:14px;'>👤 {txt_f3}</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 0.4rem 0; border-color: #ECEFF1;'>", unsafe_allow_html=True)

        

