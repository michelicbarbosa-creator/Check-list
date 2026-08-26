
import streamlit as st
import datetime
import sqlite3
import json

# Configuração Principal do Programa
st.set_page_config(page_title="Certification Checklist", layout="wide")
st.title("📋 Certification Checklist Program")

# 1. INICIALIZAÇÃO DE MEMÓRIA GLOBAL (Garante que nenhuma variável dê erro de leitura)
if 'materials_list' not in st.session_state:
    st.session_state.materials_list = []
if 'oeti_shipments' not in st.session_state:
    st.session_state.oeti_shipments = []

status_options = [
    "🟥 NO NEED", 
    "🟨 IN PROGRESS / EM PROCESSO", 
    "🟩 GREEN / OK / TERMINADO"
]

# CRIAÇÃO DOS VALORES PADRÃO (Garante a existência global das variáveis)
project_name = "Project Alpha"
folder_number = "F-2026-001"
model_name = "Standard V1"
article_name_t1 = "Premium Cotton Fabric"
cert_type = "NEW CERTIFICATION"
inst_oeti, inst_testex, inst_hohenstein = False, False, False
add_bom, bom_notes = False, ""
t_splag, t_confirmed, m_chart, m_check, saved_folder, label_status = status_options[0], status_options[0], status_options[0], status_options[0], status_options[0], status_options[0]
s_inprogress, s_revision, s_confirmed, s_sent_oeti, s_excel = status_options[0], status_options[0], status_options[0], status_options[0], status_options[0]
samples_made, date_made = 1, datetime.date.today()
mockup_article, mockups_ready, fabric_used, roll_number, fabric_number, date_sent_lab = "", status_options[0], "", "", "", datetime.date.today()
bom_revision, m_chart_revision, care_label, cert_docs, inspec_report = status_options[0], status_options[0], status_options[0], status_options[0], status_options[0]

def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today:
        return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1:
        return "🟨 WARNING: Expires Tomorrow!", "warning"
    else:
        return "🟩 Valid Document", "success"

# --- ESTRUTURA DAS 6 ABAS NA TELA ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", "2. Documents (Multi-Material)", "3. Technical Documentation", 
    "4. Sample Garment (Multi-Shipment)", "5. Sample Mockups", "6. Preview & Finalisation"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification")
    project_name = st.text_input("PROJECT NAME", value=project_name)
    folder_number = st.text_input("NUMBER OF THE PROJECT FOLDER", value=folder_number)
    model_name = st.text_input("MODEL", value=model_name)
    article_name_t1 = st.text_input("ARTICLE", value=article_name_t1)
    cert_type = st.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"])
    
    st.markdown("---")
    st.subheader("🏛️ TARGET CERTIFICATION INSTITUTE")
    inst_oeti = st.checkbox("OETI")
    inst_testex = st.checkbox("TESTEX")
    inst_hohenstein = st.checkbox("HOHENSTEIN")
    
    st.markdown("---")
    add_bom = st.checkbox("ADD BOM (Bill of Materials)")
    bom_notes = st.text_area("BOM NOTES / REVISIONS (e.g., BOM 1 for main fabric, BOM 2 for lining)", value=bom_notes)

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    st.subheader("Add Material Item")
    
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"])
    doc_art_name = st.text_input("ARTICLE NAME (for this material)", value=article_name_t1)
    doc_art_num = st.text_input("ARTICLE NUMBER", value="ART-9922")
    
    col1, col2 = st.columns(2)
    with col1: oekotex = st.checkbox("OEKO-TEX Compliance")
    with col2: text_report = st.checkbox("TEXT REPORT Attached")
    
    expiration_date = st.date_input("EXPIRATION DATE", datetime.date.today() + datetime.timedelta(days=2))
    alert_msg, alert_type = check_expiration(expiration_date)
    
    if alert_type == "error": st.error(alert_msg)
    elif alert_type == "warning": st.warning(alert_msg)
    else: st.success(alert_msg)
    
    if st.button("➕ Add Material to Project List"):
        st.session_state.materials_list.append({
            "type": material, "name": doc_art_name, "number": doc_art_num,
            "oekotex": "YES" if oekotex else "NO", "report": "YES" if text_report else "NO",
            "expiry": str(expiration_date), "status": alert_msg
        })
        st.success(f"Added {material} ({doc_art_num}) successfully!")

    st.markdown("---")
    st.subheader("📋 Current Project Materials List")
    if st.session_state.materials_list:
        st.dataframe(st.session_state.materials_list, use_container_width=True)
        if st.button("🗑️ Clear Materials List"):
            st.session_state.materials_list = []
            st.rerun()
    else:
        st.info("No materials added yet.")

# ================= TAB 3: TECHNICAL DOCUMENTATION =================
with tab3:
    st.header("Technical Documentation Status")
    t_splag = st.selectbox("TECHNICAL DOCUMENTATION SPLAG", status_options, index=0)
    t_confirmed = st.selectbox("TECHNICAL DOCUMENTATION CONFIRMED", status_options, index=0)
    m_chart = st.selectbox("MEASUREMENT CHART", status_options, index=0)
    m_check = st.selectbox("MEASUREMENT CHECK OF SAMPLE", status_options, index=0)
    saved_folder = st.selectbox("SAVED IN FOLDER", status_options, index=0)
    label_status = st.selectbox("LABEL", status_options, index=0)

# ================= TAB 4: SAMPLE GARMENT =================
with tab4:
    st.header("Sample Garment Tracking")
    s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options, index=0)
    s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options, index=0)
    s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options, index=0)
    s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options, index=0)
    s_excel = st.selectbox("SAMPLE ENTERED IN 'OVERVIEW OF REQUIRED SAMPLE (EXCEL FILE)'", status_options, index=0)
    
    st.markdown("---")
    st.subheader("Production & Shipment Log")
    col_made, col_log = st.columns(2)
    
    with col_made:
        samples_made = st.number_input("QUANTITY OF SAMPLES MADE", min_value=0, value=1)
        date_made = st.date_input("DATE SAMPLES MADE", value=date_made)
    
    with col_log:
        st.write("Record a specific shipment batch to OETI with its status:")
        shipment_qty = st.number_input("QUANTITY SENT IN THIS BATCH", min_value=1, value=1, key="ship_qty")
        shipment_date = st.date_input("DATE SENT", key="ship_date")
        ship_approval = st.selectbox("BATCH APPROVAL STATUS", ["PENDING / IN EVALUATION", "🟩 APPROVED", "🟥 NOT APPROVED"], key="ship_app")
        
        ship_rejection = ""
        if ship_approval == "🟥 NOT APPROVED":
            ship_rejection = st.text_input("Reason for Rejection:")
            
        if st.button("➕ Add Shipment to History List"):
            status_text = f"{ship_approval}"
            if ship_approval == "🟥 NOT APPROVED" and ship_rejection:
                status_text += f" (Reason: {ship_rejection})"
                
            st.session_state.oeti_shipments.append({
                "qty": shipment_qty, "date": str(shipment_date), "approval": status_text
            })
            st.success("Logged shipment batch!")

    st.markdown("---")
    st.subheader("🚚 History of Registered Shipments")
    if st.session_state.oeti_shipments:
        st.dataframe(st.session_state.oeti_shipments, use_container_width=True)
        if st.button("🗑️ Clear Shipment History"):
            st.session_state.oeti_shipments = []
            st.rerun()
    else:
        st.info("No shipments registered yet.")

# ================= TAB 5: SAMPLE MOCKUPS =================
with tab5:
    st.header("Sample Mockups Details")
    mockup_article = st.text_input("ARTICLE OF MOCKUPS", value=mockup_article)
    mockups_ready = st.selectbox("MOCK-UPS READY Status", status_options, index=0)
    fabric_used = st.text_input("FABRIC USED", value=fabric_used)
    roll_number = st.text_input("ROLL NUMBER", value=roll_number)
    fabric_number = st.text_input("FABRIC NUMBER", value=fabric_number)
    date_sent_lab = st.date_input("WHEN WAS IT SENT TO LABORATORY?", value=date_sent_lab)

# ================= TAB 6: PREVIEW & FINALISATION =================
with tab6:
    st.header("Review & Database Management")
    
    bom_revision = st.selectbox("BOM REVISION", status_options, index=0)
    m_chart_revision = st.selectbox("MEASUREMENT CHART REVISION", status_options, index=0)
    care_label = st.selectbox("CARE LABEL", status_options, index=0)
    cert_docs = st.selectbox("CERTIFICATES DOCS ARCHIVE", status_options, index=0)
    inspec_report = st.selectbox("INSPECTION REPORT SAVED IN FOLDER", status_options, index=0)
    
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    col_db, col_csv = st.columns(2)
    
    # Processamento do texto dos institutos
    selected_institutes = []
    if inst_oeti: selected_institutes.append("OETI")
    if inst_testex: selected_institutes.append("TESTEX")
    if inst_hohenstein: selected_institutes.append("HOHENSTEIN")
    institutes_text = ", ".join(selected_institutes) if selected_institutes else "None selected"

    # Montagem estável das linhas do relatório (Linha 197 Corrigida e Alinhada)
    lines = [
        "CERTIFICATION CHECKLIST REPORT\tVALUE / STATUS",
        "==================================================\t====================",
        f"Project Name:\t{project_name}",
        f"Folder Number:\t{folder_number}",
        f"Model Name:\t{model_name}",
        f"Article Name:\t{article_name_t1}",
        f"Certification Type:\t{cert_type}",
        f"Target Institute(s):\t{institutes_text}",
        f"BOM Attached:\t{'YES' if add_bom else 'NO'}",
        f"BOM Notes:\t{bom_notes}",
        f"SPLAG:\t{t_splag}",
        f"Confirmed:\t{t_confirmed}",
        f"Measurement Chart:\t{m_chart}",
        f"Measurement Check:\t{m_check}",
