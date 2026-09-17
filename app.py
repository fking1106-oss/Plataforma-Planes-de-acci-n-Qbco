import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

st.set_page_config(
    page_title="Gestión de Planes de Acción - QBCO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for a professional dashboard look
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Automatización de Informes - Planes de Acción QBCO")
st.markdown("""
Plataforma centralizada para la consolidación, filtrado y análisis de indicadores operativos para las **6 plantas a nivel nacional**. 
Sube tu archivo CSV o Excel para generar automáticamente los indicadores de cumplimiento, retrasos y proyecciones.
""")

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
    
    n = 300
    fechas_inicio = pd.date_range(start="2024-01-01", end="2026-03-01", periods=n)
    fechas_fin = [d + pd.Timedelta(days=int(np.random.randint(5, 75))) for d in fechas_inicio]
    
    data = {
        "Planta": np.random.choice(plantas, n),
        "Fecha Inicio": fechas_inicio,
        "Fecha Final": fechas_fin,
        "Origen": np.random.choice(origenes, n),
        "IFS": np.random.choice(ifs_options, n, p=[0.4, 0.6]),
        "Responsable": np.random.choice(responsables, n),
        "Proceso": np.random.choice(procesos, n),
        "Estado": np.random.choice(estados, n, p=[0.25, 0.25, 0.35, 0.15]),
        "Descripción Acción": [f"Acción correctiva #{i} de mejora en planta" for i in range(n)]
    }
    
    df = pd.DataFrame(data)
    return df

st.sidebar.header("📁 Carga de Datos")
uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo CSV o Excel (XLSX)", 
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("¡Archivo cargado exitosamente!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")
        df = load_sample_data()
else:
    st.sidebar.info("💡 Usando datos de simulación para las 6 plantas QBCO (QBCO Buga, DL, Llano, Auralac, CF, Fadeplast).")
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

# --- SELECTOR DE VISTA PRINCIPAL (NIVEL 1 Y NIVEL 2) ---
st.sidebar.markdown("---")
st.sidebar.header("🏢 Filtro Principal de Planta")

plantas_oficiales = ["QBCO Buga", "DL", "Llano", "Auralac", "CF", "Fadeplast"]
# Verificar si el dataset contiene las plantas oficiales, de lo contrario usar las disponibles
plantas_disponibles = sorted(df['Planta'].dropna().unique().tolist()) if 'Planta' in df.columns else plantas_oficiales

vista_opciones = ["🌐 Consolidado Nacional (6 Plantas)"] + plantas_oficiales
seleccion_vista = st.sidebar.selectbox("Seleccione Vista / Planta", options=vista_opciones)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros Detallados (Nivel 3)")

# Filtrar dataframe base según la selección principal de planta
if seleccion_vista == "🌐 Consolidado Nacional (6 Plantas)":
    df_filtered = df.copy()
    st.markdown("## 🌐 Nivel 1 — Consolidado Nacional de Plantas QBCO")
    st.markdown("Visualización global integrando la gestión de las 6 plantas a nivel nacional.")
else:
    df_filtered = df[df['Planta'] == seleccion_vista].copy()
    st.markdown(f"## 🏭 Nivel 2 — Gestión Específica: **{seleccion_vista}**")
    st.markdown(f"Análisis enfocado exclusivamente en la planta seleccionada.")

# Filtros adicionales en barra lateral
procesos_disp = sorted(df_filtered['Proceso'].dropna().unique().tolist()) if 'Proceso' in df_filtered.columns else []
selected_procesos = st.sidebar.multiselect("Proceso(s)", options=procesos_disp, default=procesos_disp)

responsables_disp = sorted(df_filtered['Responsable'].dropna().unique().tolist()) if 'Responsable' in df_filtered.columns else []
selected_responsables = st.sidebar.multiselect("Responsable(s)", options=responsables_disp, default=responsables_disp)

ifs_disp = sorted(df_filtered['IFS'].dropna().unique().tolist()) if 'IFS' in df.columns else []
selected_ifs = st.sidebar.multiselect("IFS (Sí / No)", options=ifs_disp, default=ifs_disp)

# Aplicar filtros detallados
if selected_procesos and 'Proceso' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Proceso'].isin(selected_procesos)]
if selected_responsables and 'Responsable' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Responsable'].isin(selected_responsables)]
if selected_ifs and 'IFS' in df.columns:
    df_filtered = df_filtered[df_filtered['IFS'].isin(selected_ifs)]

# Calcular métricas operativas clave
hoy = pd.to_datetime('today').normalize()
total_acciones = len(df_filtered)
cerradas = len(df_filtered[df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)]) if 'Estado' in df_filtered.columns else 0
abiertas = len(df_filtered[df_filtered['Estado'].str.lower().str.contains('abierto|proceso', na=False)]) if 'Estado' in df_filtered.columns else 0

# Calcular vencidas (abiertas con fecha final menor a hoy)
if 'Fecha Final' in df_filtered.columns and 'Estado' in df_filtered.columns:
    df_abiertas_temp = df_filtered[~df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)]
    vencidas = len(df_abiertas_temp[df_abiertas_temp['Fecha Final'] < hoy])
    proximas_vencer_count = len(df_abiertas_temp[(df_abiertas_temp['Fecha Final'] >= hoy) & ((df_abiertas_temp['Fecha Final'] - hoy).dt.days <= 20)])
else:
    vencidas = 0
    proximas_vencer_count = 0

cumplimiento_pct = (cerradas / total_acciones * 100) if total_acciones > 0 else 0

st.markdown("### 📊 Indicadores Clave de Desempeño (KPIs)")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="Total Acciones", value=f"{total_acciones:,}")
with col2:
    st.metric(label="Cerradas", value=f"{cerradas:,}")
with col3:
    st.metric(label="Abiertas", value=f"{abiertas:,}")
with col4:
    st.metric(label="% Cumplimiento", value=f"{cumplimiento_pct:.1f}%")
with col5:
    st.metric(label="Vencidas", value=f"{vencidas:,}", delta_color="inverse")
with col6:
    st.metric(label="Prox. Vencer (20d)", value=f"{proximas_vencer_count:,}")

st.markdown("---")

# --- ANÁLISIS HISTÓRICO Y COMPARATIVO ---
st.markdown("### 📈 Análisis Histórico y Tendencias")
if 'Fecha Inicio' in df_filtered.columns:
    df_filtered['Año'] = df_filtered['Fecha Inicio'].dt.year
    df_filtered['Mes_Año'] = df_filtered['Fecha Inicio'].dt.to_period('M').astype(str)
    
    max_year = df_filtered['Año'].max() if not df_filtered['Año'].isna().all() else datetime.now().year
    target_years = [max_year - 1, max_year]
    
    df_recent = df_filtered[df_filtered['Año'].isin(target_years)]
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader(f"Cumplimiento por Año (Foco: {target_years[0]} y {target_years[1]})")
        if not df_recent.empty:
            anual_summary = df_recent.groupby(['Año', 'Estado']).size().reset_index(name='Cantidad')
            fig_anual = px.bar(
                anual_summary, x='Año', y='Cantidad', color='Estado',
                barmode='group', title="Distribución por Año",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig_anual, use_container_width=True)
        else:
            st.warning("No hay suficientes datos para los últimos dos años.")
            
    with col_t2:
        st.subheader("Evolución Mensual")
        if not df_filtered.empty:
            mensual_summary = df_filtered.groupby(['Mes_Año', 'Estado']).size().reset_index(name='Cantidad')
            fig_mensual = px.line(
                mensual_summary, x='Mes_Año', y='Cantidad', color='Estado',
                markers=True, title="Comportamiento Mensual"
            )
            fig_mensual.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_mensual, use_container_width=True)

# Si estamos en vista consolidada, mostrar comparativo directo entre las 6 plantas
if seleccion_vista == "🌐 Consolidado Nacional (6 Plantas)":
    st.markdown("---")
    st.subheader("🏭 Comparativo de Carga y Desempeño entre las 6 Plantas QBCO")
    if 'Planta' in df_filtered.columns and not df_filtered.empty:
        comp_planta = df_filtered.groupby(['Planta', 'Estado']).size().reset_index(name='Cantidad')
        fig_comp = px.bar(
            comp_planta, x='Planta', y='Cantidad', color='Estado',
            barmode='stack', title="Volumen y Estado de Acciones por Planta Nacional"
        )
        st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")
col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown("### ⚙️ Procesos por Volumen")
    if 'Proceso' in df_filtered.columns and not df_filtered.empty:
        proc_vol = df_filtered['Proceso'].value_counts().reset_index()
        proc_vol.columns = ['Proceso', 'Volumen']
        fig_proc = px.pie(
            proc_vol, names='Proceso', values='Volumen', 
            hole=0.4, title="Acciones por Proceso Operativo"
        )
        st.plotly_chart(fig_proc, use_container_width=True)

with col_p2:
    st.markdown("### 📋 Origen de los Planes de Acción")
    if 'Origen' in df_filtered.columns and not df_filtered.empty:
        origen_vol = df_filtered['Origen'].value_counts().reset_index()
        origen_vol.columns = ['Origen', 'Cantidad']
        fig_orig = px.bar(
            origen_vol, x='Origen', y='Cantidad', text='Cantidad',
            color='Origen', title="Distribución por Origen del Hallazgo/Acción"
        )
        st.plotly_chart(fig_orig, use_container_width=True)

st.markdown("---")
st.markdown("### 🚨 Nivel 4 — Alertas Operativas y Top Listas")

col_l1, col_l2 = st.columns(2)

with col_l1:
    st.markdown("#### 🔴 Top 10 Acciones con Mayor Retraso")
    if 'Fecha Final' in df_filtered.columns and 'Estado' in df_filtered.columns:
        df_abiertas = df_filtered[~df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)].copy()
        if not df_abiertas.empty:
            df_abiertas['Dias_Retraso'] = (hoy - df_abiertas['Fecha Final']).dt.days
            df_retrasadas = df_abiertas[df_abiertas['Dias_Retraso'] > 0].sort_values(by='Dias_Retraso', ascending=False).head(10)
            
            if not df_retrasadas.empty:
                cols_to_show = [c for c in ['Planta', 'Proceso', 'Responsable', 'Fecha Final', 'Dias_Retraso'] if c in df_retrasadas.columns]
                st.dataframe(df_retrasadas[cols_to_show], use_container_width=True)
            else:
                st.success("¡Excelente! No hay acciones abiertas vencidas.")
        else:
            st.success("No hay acciones abiertas.")

with col_l2:
    st.markdown("#### 🟠 Top 10 Acciones Próximas a Vencer (20 Días)")
    if 'Fecha Final' in df_filtered.columns and 'Estado' in df_filtered.columns:
        df_abiertas = df_filtered[~df_filtered['Estado'].str.lower().str.contains('cerrado', na=False)].copy()
        if not df_abiertas.empty:
            df_abiertas['Dias_Para_Vencer'] = (df_abiertas['Fecha Final'] - hoy).dt.days
            df_proximas = df_abiertas[(df_abiertas['Dias_Para_Vencer'] >= 0) & (df_abiertas['Dias_Para_Vencer'] <= 20)].sort_values(by='Dias_Para_Vencer', ascending=True).head(10)
            
            if not df_proximas.empty:
                cols_to_show = [c for c in ['Planta', 'Proceso', 'Responsable', 'Fecha Final', 'Dias_Para_Vencer'] if c in df_proximas.columns]
                st.dataframe(df_proximas[cols_to_show], use_container_width=True)
            else:
                st.info("No hay acciones próximas a vencer en los siguientes 20 días.")
        else:
            st.info("No hay acciones abiertas.")

st.markdown("---")
st.markdown("### 📥 Exportar Reporte Consolidado")

def convertir_excel(df_export):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Planes_Accion_QBCO')
    processed_data = output.getvalue()
    return processed_data

excel_data = convertir_excel(df_filtered)
st.download_button(
    label="📥 Descargar Reporte Filtrado en Excel",
    data=excel_data,
    file_name=f"Informe_Planes_Accion_QBCO_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

with st.expander("🛠️ Guía de Despliegue en GitHub y Streamlit Cloud"):
    st.markdown("""
    1. **Repositorio GitHub:** Sube este código como `app.py`.
    2. **Requerimientos (`requirements.txt`):**
       ```text
       streamlit
       pandas
       plotly
       openpyxl
       numpy
       ```
    3. **Streamlit Cloud:** Conecta tu repositorio en [share.streamlit.io](https://share.streamlit.io/) para disponer del aplicativo web corporativo de forma permanente.
    """)