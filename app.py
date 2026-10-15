import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página en modo ancho
st.set_page_config(
    page_title="HR People Analytics Executive Dashboard", 
    page_icon="👥", 
    layout="wide"
)

st.title("👥 Dashboard Ejecutivo: HR People Analytics & Talento")
st.markdown("Monitoreo estratégico de retención de personal, rotación (*Attrition*), clima laboral y equidad salarial por departamento.")

# Generación de datos simulados de empleados (300 colaboradores)
@st.cache_data
def load_hr_data():
    np.random.seed(42)
    n_empleados = 300
    
    ids = [f"EMP-{i:03d}" for i in range(1, n_empleados + 1)]
    departamentos = np.random.choice(['Tecnología', 'Ventas & Marketing', 'Operaciones', 'Finanzas & Legal'], size=n_empleados, p=[0.3, 0.3, 0.25, 0.15])
    niveles = np.random.choice(['Junior', 'Senior', 'Lead / Gerente'], size=n_empleados, p=[0.5, 0.35, 0.15])
    
    # Simulación lógica: Tecnología y Ventas suelen tener mayor rotación
    attrition_probs = {'Tecnología': 0.22, 'Ventas & Marketing': 0.25, 'Operaciones': 0.15, 'Finanzas & Legal': 0.10}
    attrition = [np.random.choice(['Activo', 'Dio de Baja'], p=[1 - attrition_probs[dept], attrition_probs[dept]]) for dept in departamentos]
    
    satisfaccion = np.random.randint(1, 6, size=n_empleados) # Escala del 1 al 5
    rendimiento = np.random.randint(2, 6, size=n_empleados)  # Escala del 2 al 5
    
    # Salarios basados en nivel y departamento
    base_salarios = {'Junior': 18000, 'Senior': 38000, 'Lead / Gerente': 65000}
    salarios = [base_salarios[niv] + np.random.randint(-3000, 5000) for niv in niveles]
    
    anos_experiencia = np.random.randint(1, 15, size=n_empleados)

    df = pd.DataFrame({
        'ID_Empleado': ids,
        'Departamento': departamentos,
        'Nivel': niveles,
        'Estado': attrition,
        'Satisfaccion_Laboral': satisfaccion,
        'Evaluacion_Desempeno': rendimiento,
        'Salario_Mensual ($)': salarios,
        'Anos_Experiencia': anos_experiencia
    })
    return df

df_hr = load_hr_data()

# -------------------------------------------------------------
# SIDEBAR: FILTROS ESTRATÉGICOS DE RRHH
# -------------------------------------------------------------
st.sidebar.header("⚙️ Filtros de Talento")

# 1. Filtro por Departamento
deptos_disponibles = df_hr['Departamento'].unique().tolist()
deptos_seleccionados = st.sidebar.multiselect(
    "Departamentos",
    options=deptos_disponibles,
    default=deptos_disponibles
)

# 2. Filtro por Nivel de Puesto
niveles_disponibles = df_hr['Nivel'].unique().tolist()
niveles_seleccionados = st.sidebar.multiselect(
    "Nivel Jerárquico",
    options=niveles_disponibles,
    default=niveles_disponibles
)

# Aplicar filtros
mask = (
    df_hr['Departamento'].isin(deptos_seleccionados) & 
    df_hr['Nivel'].isin(niveles_seleccionados)
)
df_filtered = df_hr.loc[mask]

# -------------------------------------------------------------
# VALIDACIÓN Y MÉTRICAS CLAVE (KPIs)
# -------------------------------------------------------------
if df_filtered.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados. Ajusta los criterios en la barra lateral.")
else:
    total_colaboradores = len(df_filtered)
    bajas = len(df_filtered[df_filtered['Estado'] == 'Dio de Baja'])
    tasa_rotacion = (bajas / total_colaboradores) * 100 if total_colaboradores > 0 else 0
    satisfaccion_promedio = df_filtered['Satisfaccion_Laboral'].mean()
    salario_promedio = df_filtered['Salario_Mensual ($)'].mean()

    # Alertas inteligentes de talento
    if tasa_rotacion > 20.0:
        st.error(f"🚨 **Alerta de Retención:** La tasa de rotación en el grupo seleccionado es alta ({tasa_rotacion:.1f}%). Se recomienda revisar planes de compensación y clima laboral.")
    elif satisfaccion_promedio < 3.0:
        st.warning(f"⚠️ **Atención al Clima Laboral:** El puntaje promedio de satisfacción ({satisfaccion_promedio:.1f} / 5.0) está por debajo de la meta.")
    else:
        st.success("✅ **Indicadores de Talento Estables:** La retención y satisfacción operan dentro de parámetros saludables.")

    # Tarjetas KPI Superiores
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Colaboradores en Scope", f"{total_colaboradores}")
    col2.metric("Tasa de Rotación (Attrition)", f"{tasa_rotacion:.1f}%", "-2.1% vs año ant.")
    col3.metric("Satisfacción Promedio", f"{satisfaccion_promedio:.1f} / 5.0")
    col4.metric("Salario Mensual Promedio", f"${salario_promedio:,.2f}")

    st.markdown("---")

    # -------------------------------------------------------------
    # GRÁFICAS ANALÍTICAS (PLOTLY)
    # -------------------------------------------------------------
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Rotación de Personal por Departamento")
        df_attrition = df_filtered.groupby(['Departamento', 'Estado']).size().reset_index(name='Cantidad')
        fig_attr = px.bar(
            df_attrition, x='Departamento', y='Cantidad', color='Estado',
            barmode='group',
            color_discrete_sequence=['#38bdf8', '#f43f5e']
        )
        fig_attr.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#f8fafc')
        )
        st.plotly_chart(fig_attr, use_container_width=True)

    with col_b:
        st.subheader("💰 Distribución Salarial por Nivel y Depto")
        fig_box = px.box(
            df_filtered, x='Nivel', y='Salario_Mensual ($)', color='Departamento',
            color_discrete_sequence=['#38bdf8', '#8b5cf6', '#ec4899', '#10b981']
        )
        fig_box.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#f8fafc')
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------
    # TABLA DE DATOS Y EXPORTACIÓN
    # -------------------------------------------------------------
    st.subheader("📋 Directorio y Detalle de Colaboradores")
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

    csv_hr = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte de HR People Analytics (CSV)",
        data=csv_hr,
        file_name="reporte_hr_people_analytics.csv",
        mime="text/csv",
    )