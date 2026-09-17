import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io
import base64
from PIL import Image

# STREAM_CHUNK:Configuring page setup and corporate design tokens...
st.set_page_config(
    page_title="Gestión de Planes de Acción - Grupo QBCO",
    page_icon="🟥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching the clean, executive enterprise blue header aesthetic with QBCO crimson branding
st.markdown("""
    <style>
    /* Global Background */
    .main {
        background-color: #f4f6f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* Executive Top Blue Header Banner */
    .exec-header {
        background: #0056b3;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 6px rgba(0, 86, 179, 0.15);
    }

    /* Card Containers matching template aesthetic */
    .dashboard-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
    }
    
    .card-title {
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 16px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 8px;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0056b3;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .metric-label {
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 6px;
    }

    /* Plant Badge Grid */
    .plant-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #dc2626;
        padding: 14px;
        border-radius: 8px;
        text-align: left;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    </style>
""", unsafe_allow_html=True)

# STREAM_CHUNK:Configuring sidebar inputs, file uploader, and custom logo upload...
st.sidebar.markdown("### 🏢 Configuración y Datos")

# Logo upload section
uploaded_logo = st.sidebar.file_uploader("Subir Logo Corporativo (PNG/JPG)", type=["png", "jpg", "jpeg"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo de Planes de Acción (CSV o XLSX)", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("¡Archivo cargado con éxito!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")
        df = None
else:
    st.sidebar.info("💡 Modo Demostración activo: Usando base simulada para las 6 plantas nacionales de Grupo QBCO.")

# STREAM_CHUNK:Defining sample data loader and cleaning utilities...
@st.cache_data
def load_sample_data():
    import numpy as np
    np.random.seed(42)
    
    plantas = ["QBCO Buga", "DL", "Llano", "Auralac", "CF", "Fadeplast"]
    origenes = ["Auditoría Interna", "Inspección de Seguridad", "Reclamo de Cliente", "Hallazgo Calidad", "Mejora Continua"]
    procesos = ["Producción", "Mantenimiento", "Calidad", "Logística", "Seguridad Ocupacional"]
    responsables = ["Carlos Pérez", "Ana Gómez", "Luis Rodríguez", "María Torres", "Jorge Ramírez", "Diana Castro"]
    ifs_options = ["Sí", "No"]
    estados = ["Abierto", "En Proceso", "Cerrado", "Vencido"]
    
    n = 350
    fechas_inicio = pd.date_range(start="2024-01-01", end="2026-03-01", periods=n)
    fechas_fin = [d + pd.Timedelta(days=int(np.random.randint(5, 75))) for d in fechas_inicio]
    
    data = {
        "Planta": np.random.choice(plantas, n, p=[0.25, 0.15, 0.15, 0.15, 0.15, 0.15]),
        "Fecha Inicio": fechas_inicio,
        "Fecha Final": fechas_fin,
        "Origen": np.random.choice(origenes, n),
        "IFS": np.random.choice(ifs_options, n, p=[0.4, 0.6]),
        "Responsable": np.random.choice(responsables, n),
        "Proceso": np.random.choice(procesos, n),
        "Estado": np.random.choice(estados, n, p=[0.25, 0.25, 0.35, 0.15]),
        "Descripción Acción": [f"Acción correctiva #{i} de mejora en planta nacional QBCO" for i in range(n)]
    }
    
    return pd.DataFrame(data)

if uploaded_file is None:
    df = load_sample_data()

def limpiar_datos(dataframe):
    column_mapping = {}
    for col in dataframe.columns:
        col_lower = col.strip().lower()
        if 'planta' in col_lower: column_mapping[col] = 'Planta'
        elif 'inicio' in col_lower: column_mapping[col] = 'Fecha Inicio'
        elif 'final' in col_lower or 'fin' in col_lower: column_mapping[col] = 'Fecha Final'
        elif 'origen' in col_lower: column_mapping[col] = 'Origen'
        elif 'ifs' in col_lower: column_mapping[col] = 'IFS'
        elif 'responsable' in col_lower: column_mapping[col] = 'Responsable'
        elif 'proceso' in col_lower: column_mapping[col] = 'Proceso'
        elif 'estado' in col_lower: column_mapping[col] = 'Estado'
    
    dataframe = dataframe.rename(columns=column_mapping)
    if 'Fecha Inicio' in dataframe.columns:
        dataframe['Fecha Inicio'] = pd.to_datetime(dataframe['Fecha Inicio'], errors='coerce')
    if 'Fecha Final' in dataframe.columns:
        dataframe['Fecha Final'] = pd.to_datetime(dataframe['Fecha Final'], errors='coerce')
    return dataframe

df = limpiar_datos(df)

# STREAM_CHUNK:Rendering executive header banner with logo support...
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if uploaded_logo is not None:
        try:
            image = Image.open(uploaded_logo)
            st.image(image, width=130)
        except Exception:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 12px; padding: 10px;">
                    <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); border-radius: 8px; box-shadow: 0 4px 6px rgba(185,28,28,0.2); display: flex; align-items: center; justify-content: center; color: white; font-weight: 900; font-size: 22px;">Q</div>
                    <div>
                        <span style="font-size: 10px; font-weight: 800; color: #64748b; letter-spacing: 1px;">GRUPO</span><br>
                        <span style="font-size: 16px; font-weight: 900; color: #0f172a;">QBCo.</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; padding: 10px;">
                <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); border-radius: 8px; box-shadow: 0 4px 6px rgba(185,28,28,0.2); display: flex; align-items: center; justify-content: center; color: white; font-weight: 900; font-size: 22px;">Q</div>
                <div>
                    <span style="font-size: 10px; font-weight: 800; color: #64748b; letter-spacing: 1px;">GRUPO</span><br>
                    <span style="font-size: 16px; font-weight: 900; color: #0f172a;">QBCo.</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
        <div class="exec-header">
            <div>
                <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: white;">Análisis de Indicadores — Planes de Acción</h2>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: #e2e8f0;">Control Operativo Nacional — 6 Plantas Grupo QBCO</p>
            </div>
            <div style="text-align: right; font-size: 12px; font-weight: 600; background: rgba(255,255,255,0.15); padding: 6px 12px; border-radius: 6px;">
                MODO EJECUTIVO
            </div>
        </div>
    """, unsafe_allow_html=True)

# STREAM_CHUNK:Configuring plant and detailed filters in sidebar...
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Selección de Nivel")

plantas_oficiales = ["QBCO Buga", "DL", "Llano", "Auralac", "CF", "Fadeplast"]
vista_opciones = ["🌐 Consolidado Nacional (6 Plantas)"] + plantas_oficiales
seleccion_vista = st.sidebar.selectbox("Seleccionar Planta o Consolidado", options=vista_opciones)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros Detallados")

procesos_disp = sorted(df['Proceso'].dropna().unique().tolist()) if 'Proceso' in df.columns else []
selected_procesos = st.sidebar.multiselect("Proceso(s)", options=procesos_disp, default=procesos_disp)

responsables_disp = sorted(df['Responsable'].dropna().unique().tolist()) if 'Responsable' in df.columns else []
selected_responsables = st.sidebar.multiselect("Responsable(s)", options=responsables_disp, default=responsables_disp)

ifs_disp = sorted(df['IFS'].dropna().unique().tolist()) if 'IFS' in df.columns else []
selected_ifs = st.sidebar.multiselect("IFS (Sí / No)", options=ifs_disp, default=ifs_disp)

# Filter application
if seleccion_vista == "🌐 Consolidado Nacional (6 Plantas)":
    df_filtered = df.copy()
else:
    df_filtered = df[df['Planta'] == seleccion_vista].copy()

if selected_procesos and 'Proceso' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Proceso'].isin(selected_procesos)]
if selected_responsables and 'Responsable' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Responsable'].isin(selected_responsables)]
if selected_ifs and 'IFS' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['IFS'].isin(selected_ifs)]

# STREAM_CHUNK:Rendering exact geographical plants diagram matching user's image reference...
if seleccion_vista == "🌐 Consolidado Nacional (6 Plantas)":
    st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">🗺️ Mapa de Ubicación Geográfica y Portafolio de Plantas — Grupo QBCO</div>
            <p style="font-size: 13px; color: #64748b; margin-bottom: 18px;">Distribución estratégica nacional de las 6 plantas productivas y sus líneas de especialidad (Referencia Corporativa):</p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;">
                <div class="plant-box">
                    <span style="font-size: 10px; font-weight: 800; color: #dc2626;">PLANTA LLANOS DE CUIVÁ</span><br>
                    <b style="font-size: 14px; color: #0f172a;">El Llano</b><br>
                    <span style="font-size: 11px; color: #475569;">🧀 Lácteos y Quesos</span>
                </div>
                <div class="plant-box">
                    <span style="font-size: 10px; font-weight: 800; color: #dc2626;">PLANTA RIONEGRO</span><br>
                    <b style="font-size: 14px; color: #0f172a;">Auralac</b><br>
                    <span style="font-size: 11px; color: #475569;">🥛 Lácteos y Derivados</span>
                </div>
                <div class="plant-box">
                    <span style="font-size: 10px; font-weight: 800; color: #dc2626;">PLANTA TOCANCIPÁ</span><br>
                    <b style="font-size: 14px; color: #0f172a;">CF (Carnes Frías)</b><br>
                    <span style="font-size: 11px; color: #475569;">🥩 Carnes Frías y Embutidos</span>
                </div>
                <div class="plant-box">
                    <span style="font-size: 10px; font-weight: 800; color: #dc2626;">PLANTA TOCANCIPÁ</span><br>
                    <b style="font-size: 14px; color: #0f172a;">DL</b><br>
                    <span style="font-size: 11px; color: #475569;">🧀 Quesos Especiales</span>
                </div>
                <div class="plant-box" style="border-left: 5px solid #0056b3;">
                    <span style="font-size: 10px; font-weight: 800; color: #0056b3;">PLANTA BUGA (SEDE PRINCIPAL)</span><br>
                    <b style="font-size: 14px; color: #0f172a;">QBCO Buga</b><br>
                    <span style="font-size: 11px; color: #475569;">🥫 Salsas, Aceites, Bebidas, Vinagres</span>
                </div>
                <div class="plant-box">
                    <span style="font-size: 10px; font-weight: 800; color: #dc2626;">VALLE DEL CAUCA</span><br>
                    <b style="font-size: 14px; color: #0f172a;">Fadeplast</b><br>
                    <span style="font-size: 11px; color: #475569;">🧴 Envases PET</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# STREAM_CHUNK:Calculating core metrics and KPIs...
hoy = pd.to_datetime('today').normalize()
total_acciones = len(df_filtered)
cerradas = len(df_filtered[df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)]) if 'Estado' in df_filtered.columns else 0
abiertas = len(df_filtered[df_filtered['Estado'].str.lower().str.contains('abierto|proceso', na=False)]) if 'Estado' in df_filtered.columns else 0

if 'Fecha Final' in df_filtered.columns and 'Estado' in df_filtered.columns:
    df_abiertas_temp = df_filtered[~df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)]
    vencidas = len(df_abiertas_temp[df_abiertas_temp['Fecha Final'] < hoy])
    proximas_vencer = len(df_abiertas_temp[(df_abiertas_temp['Fecha Final'] >= hoy) & ((df_abiertas_temp['Fecha Final'] - hoy).dt.days <= 20)])
else:
    vencidas = 0
    proximas_vencer = 0

cumplimiento_pct = (cerradas / total_acciones * 100) if total_acciones > 0 else 0

# STREAM_CHUNK:Rendering KPI metric cards section...
if seleccion_vista == "🌐 Consolidado Nacional (6 Plantas)":
    st.markdown("#### 🌐 Indicadores Globales — Consolidado Nacional")
else:
    st.markdown(f"#### 🏭 Indicadores de Gestión — Planta: **{seleccion_vista}**")

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Total Acciones</div><div class="metric-value">{total_acciones:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Cerradas</div><div class="metric-value">{cerradas:,}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Abiertas</div><div class="metric-value">{abiertas:,}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card" style="border-left-color: #16a34a;"><div class="metric-label">% Cumplimiento</div><div class="metric-value">{cumplimiento_pct:.1f}%</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card" style="border-left-color: #dc2626;"><div class="metric-label">Vencidas</div><div class="metric-value">{vencidas:,}</div></div>', unsafe_allow_html=True)
with col6:
    st.markdown(f'<div class="metric-card" style="border-left-color: #d97706;"><div class="metric-label">Prox. Vencer (20d)</div><div class="metric-value">{proximas_vencer:,}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# STREAM_CHUNK:Rendering historical and operational analytical charts...
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 Cumplimiento por Año (Énfasis Últimos 2 Años)</div>', unsafe_allow_html=True)
    if 'Fecha Inicio' in df_filtered.columns and not df_filtered.empty:
        df_filtered['Año'] = df_filtered['Fecha Inicio'].dt.year
        max_year = df_filtered['Año'].max() if not df_filtered['Año'].isna().all() else datetime.now().year
        target_years = [max_year - 1, max_year]
        df_recent = df_filtered[df_filtered['Año'].isin(target_years)]
        
        if not df_recent.empty:
            anual_summary = df_recent.groupby(['Año', 'Estado']).size().reset_index(name='Cantidad')
            fig_anual = px.bar(
                anual_summary, x='Año', y='Cantidad', color='Estado',
                barmode='group', color_discrete_sequence=['#dc2626', '#0056b3', '#64748b', '#cbd5e1']
            )
            fig_anual.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_anual, use_container_width=True)
        else:
            st.info("Sin registros suficientes para los últimos dos años.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_c2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📅 Evolución Mensual de Acciones</div>', unsafe_allow_html=True)
    if 'Fecha Inicio' in df_filtered.columns and not df_filtered.empty:
        df_filtered['Mes_Año'] = df_filtered['Fecha Inicio'].dt.to_period('M').astype(str)
        mensual_summary = df_filtered.groupby(['Mes_Año', 'Estado']).size().reset_index(name='Cantidad')
        if not mensual_summary.empty:
            fig_mensual = px.line(
                mensual_summary, x='Mes_Año', y='Cantidad', color='Estado',
                markers=True, color_discrete_sequence=['#dc2626', '#0056b3', '#f59e0b', '#10b981']
            )
            fig_mensual.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), xaxis_tickangle=-45, legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_mensual, use_container_width=True)
        else:
            st.info("Sin datos mensuales disponibles.")
    st.markdown('</div>', unsafe_allow_html=True)

if seleccion_vista == "🌐 Consolidado Nacional (6 Plantas)":
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏭 Comparativo de Carga y Desempeño por Planta QBCO</div>', unsafe_allow_html=True)
    if 'Planta' in df_filtered.columns and not df_filtered.empty:
        comp_planta = df_filtered.groupby(['Planta', 'Estado']).size().reset_index(name='Cantidad')
        fig_comp = px.bar(
            comp_planta, x='Planta', y='Cantidad', color='Estado',
            barmode='stack', color_discrete_sequence=['#dc2626', '#0056b3', '#f59e0b', '#64748b']
        )
        fig_comp.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig_comp, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚙️ Procesos por Volumen</div>', unsafe_allow_html=True)
    if 'Proceso' in df_filtered.columns and not df_filtered.empty:
        proc_vol = df_filtered['Proceso'].value_counts().reset_index()
        proc_vol.columns = ['Proceso', 'Volumen']
        fig_proc = px.pie(
            proc_vol, names='Proceso', values='Volumen', 
            hole=0.5, color_discrete_sequence=['#0056b3', '#dc2626', '#475569', '#94a3b8', '#cbd5e1']
        )
        fig_proc.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_proc, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_p2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Origen de los Planes de Acción</div>', unsafe_allow_html=True)
    if 'Origen' in df_filtered.columns and not df_filtered.empty:
        origen_vol = df_filtered['Origen'].value_counts().reset_index()
        origen_vol.columns = ['Origen', 'Cantidad']
        fig_orig = px.bar(
            origen_vol, x='Origen', y='Cantidad', text='Cantidad',
            color='Origen', color_discrete_sequence=['#0056b3', '#1e293b', '#475569', '#94a3b8', '#cbd5e1']
        )
        fig_orig.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig_orig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# STREAM_CHUNK:Rendering Top lists for delayed and upcoming actions...
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🚨 Alertas Operativas y Top Listas de Seguimiento</div>', unsafe_allow_html=True)

col_l1, col_l2 = st.columns(2)

with col_l1:
    st.markdown("##### 🔴 Top 10 Acciones con Mayor Retraso")
    if 'Fecha Final' in df_filtered.columns and 'Estado' in df_filtered.columns:
        df_abiertas = df_filtered[~df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)].copy()
        if not df_abiertas.empty:
            df_abiertas['Dias_Retraso'] = (hoy - df_abiertas['Fecha Final']).dt.days
            df_retrasadas = df_abiertas[df_abiertas['Dias_Retraso'] > 0].sort_values(by='Dias_Retraso', ascending=False).head(10)
            if not df_retrasadas.empty:
                cols_show = [c for c in ['Planta', 'Proceso', 'Responsable', 'Fecha Final', 'Dias_Retraso'] if c in df_retrasadas.columns]
                st.dataframe(df_retrasadas[cols_show], use_container_width=True)
            else:
                st.success("¡Excelente! No hay acciones abiertas vencidas.")
        else:
            st.success("No hay acciones abiertas registradas.")

with col_l2:
    st.markdown("##### 🟠 Top 10 Acciones Próximas a Vencer (20 Días)")
    if 'Fecha Final' in df_filtered.columns and 'Estado' in df_filtered.columns:
        df_abiertas = df_filtered[~df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)].copy()
        if not df_abiertas.empty:
            df_abiertas['Dias_Para_Vencer'] = (df_abiertas['Fecha Final'] - hoy).dt.days
            df_proximas = df_abiertas[(df_abiertas['Dias_Para_Vencer'] >= 0) & (df_abiertas['Dias_Para_Vencer'] <= 20)].sort_values(by='Dias_Para_Vencer', ascending=True).head(10)
            if not df_proximas.empty:
                cols_show = [c for c in ['Planta', 'Proceso', 'Responsable', 'Fecha Final', 'Dias_Para_Vencer'] if c in df_proximas.columns]
                st.dataframe(df_proximas[cols_show], use_container_width=True)
            else:
                st.info("No hay acciones próximas a vencer en los siguientes 20 días.")
        else:
            st.info("No hay acciones abiertas registradas.")

st.markdown('</div>', unsafe_allow_html=True)

# STREAM_CHUNK:Rendering export helper section...
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📥 Exportar Reporte Consolidado</div>', unsafe_allow_html=True)

def convertir_excel(df_export):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Planes_Accion_QBCO')
    return output.getvalue()

excel_data = convertir_excel(df_filtered)
st.download_button(
    label="📥 Descargar Reporte Filtrado en Excel",
    data=excel_data,
    file_name=f"Informe_Planes_Accion_QBCO_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.markdown('</div>', unsafe_allow_html=True)
