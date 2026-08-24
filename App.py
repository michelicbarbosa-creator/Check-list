import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(layout="wide", page_title="Sistema OEKO-Tex com Banco de Dados")

# ==========================================
# 1. CONEXÃO E CRIAÇÃO DO BANCO DE DADOS (SQLITE)
# ==========================================
def conectar_banco():
    conn = sqlite3.connect("gestor_certificacoes.db")
    return conn

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela 1: Informações Gerais do Projeto
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, artigo TEXT, modelo TEXT, bom TEXT
        )
    """)
    
    # Tabela 2: Checklist Fixo de Processos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fase TEXT, tarefa TEXT, concluido INTEGER
        )
    """)
    
    # Tabela 3: Componentes, Amostras e Certificados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS componentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT, nome TEXT, documento TEXT, amostra TEXT,
            data_envio TEXT, aprovado TEXT, tabela_medidas TEXT,
            medidas_aprovadas TEXT, tamanho_amostra TEXT,
            num_certificado TEXT, expira TEXT, notas TEXT
        )
    """)
    
    # Inserir dados iniciais na checklist caso esteja vazia
    cursor.execute("SELECT COUNT(*) FROM checklist")
    if cursor.fetchone()[0] == 0:
        tarefas_iniciais = [
            ("Documentação", "Application form OETI", 0),
            ("Documentação", "Technical document OETI", 0),
            ("Documentação", "Technical documentation SPLAG", 0),
            ("Finalização", "Technical sheet revision", 0),
            ("Finalização", "BOM revision", 0),
            ("Finalização", "Care label revision", 0)
        ]
        cursor.executemany("INSERT INTO checklist (fase, tarefa, concluido) VALUES (?, ?, ?)", tarefas_iniciais)
        
    # Inserir projeto padrão caso esteja vazio
    cursor.execute("SELECT COUNT(*) FROM projetos")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO projetos (nome, artigo, modelo, bom) VALUES (?, ?, ?, ?)", 
                       ("35. ta-d winter + rain parkas", "409 130 - 409 110", "4100-M-ZR-ZH-U", "BOM-L + BOM-C"))
        
    conn.commit()
    conn.close()

inicializar_banco()

# ==========================================
# 2. CONFIGURAÇÕES VISUAIS DA BARRA LATERAL
# ==========================================
st.sidebar.header("⚙️ Configurações do Banco")
dias_aviso = st.sidebar.number_input("Dias de antecedência para Alerta", min_value=5, max_value=120, value=30)

# ==========================================
# 3. LEITURA DOS DADOS DO BANCO DE DADOS
# ==========================================
conn = conectar_banco()
df_projeto = pd.read_sql_query("SELECT * FROM projetos LIMIT 1", conn)
df_checklist = pd.read_sql_query("SELECT * FROM checklist", conn)
df_componentes = pd.read_sql_query("SELECT * FROM componentes", conn)
conn.close()

# ==========================================
# 4. CABEÇALHO DO PROJETO (ATUALIZA NO BANCO)
# ==========================================
st.title("💾 Sistema com Persistência em Banco de Dados (SQLite)")
if not df_projeto.empty:
    st.subheader("Informações Gerais do Projeto")
    with st.form("form_projeto"):
        c1, c2, c3, c4 = st.columns(4)
        novo_nome = c1.text_input("Nome do Projeto", df_projeto.iloc[0]["nome"])
        novo_artigo = c2.text_input("Artigo", df_projeto.iloc[0]["artigo"])
        novo_modelo = c3.text_input("Modelo", df_projeto.iloc[0]["modelo"])
        novo_bom = c4.text_input("BOM Status", df_projeto.iloc[0]["bom"])
        
        if st.form_submit_button("Atualizar Informações do Projeto"):
            conn = conectar_banco()
            conn.execute("UPDATE projetos SET nome=?, artigo=?, modelo=?, bom=? WHERE id=1", 
                         (novo_nome, novo_artigo, novo_modelo, novo_bom))
            conn.commit()
            conn.close()
            st.success("Dados do projeto atualizados no Banco de Dados!")
            st.rerun()

# ==========================================
# 5. GERENCIAMENTO DE ALERTAS DE PRAZO
# ==========================================
hoje = date.today()
alertas_criticos = []
alertas_aviso = []

if not df_componentes.empty:
    for idx, row in df_componentes.iterrows():
        data_fim = datetime.strptime(row["expira"], "%Y-%m-%d").date()
        dias_restantes = (data_fim - hoje).days
        
        if dias_restantes < 0:
            alertas_criticos.append(f"O certificado **{row['num_certificado']}** ({row['nome']}) expirou há {abs(dias_restantes)} dias!")
        elif dias_restantes <= dias_aviso:
            alertas_aviso.append(f"O documento do item **{row['nome']}** ({row['categoria']}) vence em {dias_restantes} dias.")

if alertas_criticos or alertas_aviso:
    st.subheader("🔔 Alertas de Vencimento (Filtro do Banco)")
    for erro in alertas_criticos: st.error(erro)
    for aviso in alertas_aviso: st.warning(aviso)
    st.markdown("---")

# ==========================================
# 6. MÓDULO 1: CHECKLIST DE PROCESSOS
# ==========================================
st.header("1. Checklist de Processos e Validações")
col_chk1, col_chk2 = st.columns(2)

conn = conectar_banco()
with col_chk1:
    st.markdown("### 📑 Documentação")
    for idx, row in df_checklist[df_checklist["fase"] == "Documentação"].iterrows():
        id_tarefa = row["id"]
        status_atual = bool(row["concluido"])
        novo_status = st.checkbox(row["tarefa"], value=status_atual, key=f"t_{id_tarefa}")
        if novo_status != status_atual:
            conn.execute("UPDATE checklist SET concluido=? WHERE id=?", (int(novo_status), id_tarefa))
            conn.commit()

with col_chk2:
    st.markdown("### 🏁 Finalização")
    for idx, row in df_checklist[df_checklist["fase"] == "Finalização"].iterrows():
        id_tarefa = row["id"]
        status_atual = bool(row["concluido"])
        novo_status = st.checkbox(row["tarefa"], value=status_atual, key=f"t_{id_tarefa}")
        if novo_status != status_atual:
            conn.execute("UPDATE checklist SET concluido=? WHERE id=?", (int(novo_status), id_tarefa))
            conn.commit()
conn.close()

st.markdown("---")

# ==========================================
# 7. MÓDULO 2: CADASTRO DE MATERIAIS NO BANCO
# ==========================================
st.header("2. Painel de Componentes, Amostras e Certificados")

with st.form("form_componente_db", clear_on_submit=True):
    st.markdown("##### ➕ Adicionar Registro Permanente no Banco de Dados")
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        cat = f1.selectbox("Categoria", ["Tecido", "Reflex", "Elastic", "Buttons", "Extras"])
        nome_material = f1.text_input("Nome do Componente")
    with f2:
        doc_tipo = f2.selectbox("Tipo Documento", ["OEKO-Tex Standard 100", "Test Report Fabric", "Test Report Accessories"])
        status_amostra = f2.selectbox("Amostra Status", ["Pendente", "Em Progresso", "Feita"])
    with f3:
        dt_envio = f3.date_input("Data de Envio", hoje)
        aprov_amostra = f3.selectbox("Amostra Aprovada?", ["Pendente", "Sim", "Não"])
    with f4:
        tab_med = f4.selectbox("Tabela de Medidas?", ["Sim", "Não", "N/A"])
        med_aprov = f4.selectbox("Medidas Aprovadas?", ["Pendente", "Sim", "Não"])
    with f5:
        tam_amostra = f5.text_input("Tam. Amostra", placeholder="Ex: M")
        nr_cert = f5.text_input("Nº Certificado")
        
    c_obs = st.text_input("Observações Gerais")
    dt_expira = st.date_input("Data de Vencimento do Documento", hoje)

    if st.form_submit_button("Inserir Registro no Banco"):
        if nome_material:
            conn = conectar_banco()
            conn.execute("""
                INSERT INTO componentes (categoria, nome, documento, amostra, data_envio, aprovado, tabela_medidas, medidas_aprovadas, tamanho_amostra, num_certificado, expira, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cat, nome_material, doc_tipo, status_amostra, str(dt_envio), aprov_amostra, tab_med, med_aprov, tam_amostra, nr_cert, str(dt_expira), c_obs))
            conn.commit()
            conn.close()
            st.success(f"{nome_material} guardado com segurança no banco de dados!")
            st.rerun()

# ==========================================
# 8. EXIBIÇÃO EM ABAS (BUSCA DIRETA NO BANCO)
# ==========================================
if not df_componentes.empty:
    categorias_abas = ["Tecido", "Reflex", "Elastic", "Buttons", "Extras"]
    tabs = st.tabs(categorias_abas)
    
    for idx, cat_nome in enumerate(categorias_abas):
        with tabs[idx]:
            df_filtrado = df_componentes[df_componentes["categoria"] == cat_nome]
            if not df_filtrado.empty:
                st.dataframe(df_filtrado[["nome", "documento", "amostra", "data_envio", "aprovado", "tabela_medidas", "medidas_aprovadas", "tamanho_amostra", "num_certificado", "expira", "notas"]], use_container_width=True)
            else:
                st.info(f"Nenhum material cadastrado na categoria: {cat_nome}")
