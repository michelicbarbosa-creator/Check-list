import streamlit as st
import datetime
import sqlite3
import json

# Configuração Principal do Programa
st.set_page_config(page_title="Certification Checklist", layout="wide")
st.title("📋 Certification Checklist Program")

# 1. INICIALIZAÇÃO DE MEMÓRIA (Sempre no topo)
if 'materials_list' not in st.session_state:
    st.session_state.materials_list = []
if 'oeti_shipments' not in st.session_state:
    st.session_state.oeti_shipments = []

status_options = [
    "🟥 NO NEED", 
    "🟨 IN PROGRESS / EM PROCESSO", 
    "🟩 GREEN / OK / TERMINADO"
]

def check_expiration(exp_date):
    today = datetime.date.today()
    if exp_date < today:
        return "🟥 EXPIRED!", "error"
    elif (exp_date - today).days == 1:
        return "🟨 WARNING: Expires Tomorrow!", "warning"
    else:
        return "🟩 Valid Document", "success"

# --- PAINEL LATERAL CONTROLADOR DE ENTRADAS ---
st.sidebar.header("⚙️ Project Controls")

project_name = st.sidebar.text_input("PROJECT NAME", value="Project Alpha")
folder_number = st.sidebar.text_input("NUMBER OF THE PROJECT FOLDER", value="F-2026-001")
model_name = st.sidebar.text_input("MODEL", value="Standard V1")
article_name_t1 = st.sidebar.text_input("ARTICLE", value="Premium Cotton Fabric")
cert_type = st.sidebar.radio("CERTIFICATION TYPE", ["NEW CERTIFICATION", "APPLICATION OF EXTENSION", "RECERTIFICATION"])

st.sidebar.markdown("---")
st.sidebar.write("🏛️ Target Institutes:")
inst_oeti = st.sidebar.checkbox("OETI")
inst_testex = st.sidebar.checkbox("TESTEX")
inst_hohenstein = st.sidebar.checkbox("HOHENSTEIN")

st.sidebar.markdown("---")
add_bom = st.sidebar.checkbox("ADD BOM")
bom_notes = st.sidebar.text_area("BOM Notes", value="")

st.sidebar.markdown("---")
st.sidebar.write("🏁 Finalisation Status:")
bom_revision = st.sidebar.selectbox("BOM REVISION", status_options)
m_chart_revision = st.sidebar.selectbox("MEASUREMENT CHART REVISION", status_options)
care_label = st.sidebar.selectbox("CARE LABEL", status_options)
cert_docs = st.sidebar.selectbox("CERTIFICATES DOCS ARCHIVE", status_options)
inspec_report = st.sidebar.selectbox("INSPECTION REPORT IN FOLDER", status_options)


# --- ESTRUTURA RECONFIGURADA PARA 6 ABAS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Project Info", "2. Documents (Multi-Material)", "3. Technical Documentation", 
    "4. Sample Garment (Multi-Shipment)", "5. Sample Mockups", "6. Preview & Finalisation"
])

# ================= TAB 1: PROJECT INFO =================
with tab1:
    st.header("Project Identification Summary")
    st.write(f"**Project Name:** {project_name}")
    st.write(f"**Folder Number:** {folder_number}")
    st.write(f"**Model:** {model_name}")
    st.write(f"**Article:** {article_name_t1}")
    st.write(f"**Type:** {cert_type}")
    st.write(f"**BOM Attached:** {'YES' if add_bom else 'NO'} ({bom_notes})")

# ================= TAB 2: DOCUMENTS =================
with tab2:
    st.header("Materials & Document Expiration")
    material = st.selectbox("MATERIAL TYPE", ["ZIPPER", "VELCRO", "ELASTIC", "REFLEX", "BUTTON", "FABRIC", "LINING", "THREAD"])
    doc_art_name = st.text_input("ARTICLE NAME", value=article_name_t1)
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
        st.success("Material added!")

    st.markdown("---")
    st.subheader("📋 Registered Materials Table")
    if st.session_state.materials_list:
        st.dataframe(st.session_state.materials_list, use_container_width=True)
        if st.button("🗑️ Clear Materials"):
            st.session_state.materials_list = []
            st.rerun()

# ================= TAB 3: TECHNICAL DOCUMENTATION =================
with tab3:
    st.header("Technical Documentation Status")
    t_splag = st.selectbox("TECHNICAL DOCUMENTATION SPLAG", status_options)
    t_confirmed = st.selectbox("TECHNICAL DOCUMENTATION CONFIRMED", status_options)
    m_chart = st.selectbox("MEASUREMENT CHART", status_options)
    m_check = st.selectbox("MEASUREMENT CHECK OF SAMPLE", status_options)
    saved_folder = st.selectbox("SAVED IN FOLDER", status_options)
    label_status = st.selectbox("LABEL", status_options)

# ================= TAB 4: SAMPLE GARMENT =================
with tab4:
    st.header("Sample Garment Tracking & Shipment Batches")
    s_inprogress = st.selectbox("SAMPLE IN PROGRESS", status_options)
    s_revision = st.selectbox("SAMPLE REVISION AT KUNG", status_options)
    s_confirmed = st.selectbox("SAMPLE CONFIRMED", status_options)
    s_sent_oeti = st.selectbox("SAMPLE SENT TO OETI", status_options)
    s_excel = st.selectbox("SAMPLE ENTERED IN 'OVERVIEW OF REQUIRED SAMPLE'", status_options)
    
    st.markdown("---")
    samples_made = st.number_input("QUANTITY OF SAMPLES MADE", min_value=0, value=1)
    date_made = st.date_input("DATE SAMPLES MADE")
    
    st.markdown("---")
    shipment_qty = st.number_input("QUANTITY SENT IN THIS BATCH", min_value=1, value=1)
    shipment_date = st.date_input("DATE SENT TO OETI")
    ship_approval = st.selectbox("BATCH APPROVAL STATUS", ["PENDING / IN EVALUATION", "🟩 APPROVED", "🟥 NOT APPROVED"])
    
    ship_rejection = ""
    if ship_approval == "🟥 NOT APPROVED":
        ship_rejection = st.text_input("Reason for Rejection:")
        
    if st.button("➕ Add Shipment Batch"):
        status_text = f"{ship_approval}"
        if ship_approval == "🟥 NOT APPROVED" and ship_rejection:
            status_text += f" (Reason: {ship_rejection})"
        st.session_state.oeti_shipments.append({
            "qty": shipment_qty, "date": str(shipment_date), "approval": status_text
        })
        st.success("Shipment logged!")

    if st.session_state.oeti_shipments:
        st.dataframe(st.session_state.oeti_shipments, use_container_width=True)
        if st.button("🗑️ Clear Shipments"):
            st.session_state.oeti_shipments = []
            st.rerun()

# ================= TAB 5: SAMPLE MOCKUPS =================
with tab5:
    st.header("Sample Mockups Details")
    mockup_article = st.text_input("ARTICLE OF MOCKUPS", value="Mock-UX Fabric")
    mockups_ready = st.selectbox("MOCK-UPS READY Status", status_options)
    fabric_used = st.text_input("FABRIC USED")
    roll_number = st.text_input("ROLL NUMBER")
    fabric_number = st.text_input("FABRIC NUMBER")
    date_sent_lab = st.date_input("WHEN WAS IT SENT TO LABORATORY?")

# --- CONSTRUÇÃO DO TEXTO DO RELATÓRIO ---
selected_institutes = []
if inst_oeti: selected_institutes.append("OETI")
if inst_testex: selected_institutes.append("TESTEX")
if inst_hohenstein: selected_institutes.append("HOHENSTEIN")
institutes_text = ", ".join(selected_institutes) if selected_institutes else "None selected"

# Função auxiliar para gerar o texto formatado para visualização/download
def generate_report_text(p_name, f_num, m_name, art_t1, c_type, insts, b_att, b_not, splag, conf, chart, check, fld, lbl, s_made, d_made, m_art, m_rdy, f_used, r_num, f_num_pk, d_lab, b_rev, c_rev, c_lbl, c_doc, i_rep, m_list, s_list):
    lines = [
        "CERTIFICATION CHECKLIST REPORT\tVALUE / STATUS",
        "==================================================\t====================",
        f"\n[TAB 1] PROJECT INFO\t",
        f"Project Name:\t{p_name}",
        f"Folder Number:\t{f_num}",
        f"Model Name:\t{m_name}",
        f"Article Name:\t{art_t1}",
        f"Certification Type:\t{c_type}",
        f"Target Institute(s):\t{insts}",
        f"BOM Attached:\t{'YES' if b_att else 'NO'}",
        f"BOM Notes & Variations:\t{b_not if b_not else 'None'}",
        f"\n[TAB 2] REGISTERED MATERIALS\t"
    ]
    if m_list:
        for idx, m in enumerate(m_list):
            lines.append(f"Material #{idx+1} ({m['type']}):\tArt: {m['name']} | Num: {m['number']} | Expiry: {m['expiry']} ({m['status']})")
    else:
        lines.append("Materials:\tNo items registered.")
        
    lines.append(f"\n[TAB 3] TECHNICAL DOCUMENTATION STATUS\t")
    lines.append(f"TECHNICAL DOCUMENTATION SPLAG:\t{splag}")
    lines.append(f"TECHNICAL DOCUMENTATION CONFIRMED:\t{conf}")
    lines.append(f"MEASUREMENT CHART:\t{chart}")
    lines.append(f"MEASUREMENT CHECK OF SAMPLE:\t{check}")
    lines.append(f"SAVED IN FOLDER:\t{fld}")
    lines.append(f"LABEL:\t{lbl}")
    lines.append(f"Total Samples Made:\t{s_made} on {d_made}")
    
    lines.append("\nOETI Shipment History Log:\t")
    if s_list:
        for idx, s in enumerate(s_list):
            lines.append(f"-> Batch Shipment #{idx+1}:\t{s['qty']} sample(s) sent on {s['date']} | Status: {s['approval']}")
    else:
        lines.append("-> Shipment History:\tNo batches registered yet.")
        
    lines.append(f"\n[TAB 5] SAMPLE MOCKUPS\t")
    lines.append(f"ARTICLE OF MOCKUPS:\t{m_art}")
    lines.append(f"MOCK-UPS READY Status:\t{m_rdy}")
    lines.append(f"FABRIC USED:\t{f_used}")
    lines.append(f"ROLL NUMBER:\t{r_num}")
    lines.append(f"FABRIC NUMBER:\t{f_num_pk}")
    lines.append(f"WHEN WAS IT SENT TO LABORATORY:\t{d_lab}")
    lines.append(f"\n[TAB 6] FINALISATION\t")
    lines.append(f"BOM REVISION:\t{b_rev}")
    lines.append(f"MEASUREMENT CHART REVISION:\t{c_rev}")
    lines.append(f"CARE LABEL:\t{c_lbl}")
