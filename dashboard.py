import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Configuración visual de la página
st.set_page_config(page_title="Panel de Consultoría", page_icon="📊", layout="wide")

st.title("📊 Panel de Control: Análisis y Estrategia")
st.write("Monitoreo en tiempo real de prospectos y solicitudes institucionales.")

# Extraer datos de SQLite
def cargar_datos():
    conexion = sqlite3.connect("consultoria.db")
    df = pd.read_sql_query("SELECT * FROM prospectos", conexion)
    conexion.close()
    return df

df_prospectos = cargar_datos()

# Validar si hay datos antes de graficar
if df_prospectos.empty:
    st.info("Aún no hay prospectos registrados. El tablero se actualizará automáticamente cuando ingresen datos.")
else:
    # --- SECCIÓN 1: KPIs (Métricas Rápidas) ---
    st.markdown("### Visión General")
    col1, col2, col3 = st.columns(3)
    
    total_prospectos = len(df_prospectos)
    servicio_top = df_prospectos['servicio_interes'].mode()[0]
    
    col1.metric("Total de Solicitudes", total_prospectos)
    col2.metric("Servicio Más Solicitado", servicio_top)
    col3.metric("Último Registro", df_prospectos['fecha_registro'].max().split()[0])

    st.markdown("---")

    # --- SECCIÓN 2: GRÁFICOS INTERACTIVOS ---
    col_grafico, col_tabla = st.columns([1, 1])

    with col_grafico:
        st.markdown("### Demanda por Área Estratégica")
        conteo = df_prospectos['servicio_interes'].value_counts().reset_index()
        conteo.columns = ['Servicio', 'Cantidad']
        
        # Crear gráfico de dona con Plotly
        fig = px.pie(conteo, values='Cantidad', names='Servicio', hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)

    with col_tabla:
        st.markdown("### Últimos Prospectos Captados")
        # Mostrar una tabla limpia solo con las columnas más relevantes
        tabla_limpia = df_prospectos[['nombre', 'institucion_o_empresa', 'servicio_interes']].tail(10)
        st.dataframe(tabla_limpia, use_container_width=True, hide_index=True)
        