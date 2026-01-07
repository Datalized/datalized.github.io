"""
PAES 2026 - Explorador de Datos
Aplicación Streamlit para visualizar resultados de la PAES
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="PAES 2026 - Explorador",
    page_icon="📊",
    layout="wide"
)

# Conexión a la base de datos
@st.cache_resource
def get_connection():
    return duckdb.connect("paes.duckdb", read_only=True)

con = get_connection()

# Título
st.title("📊 PAES 2026 - Explorador de Datos")
st.markdown("Análisis de resultados de la Prueba de Acceso a la Educación Superior de Chile")

# Sidebar con filtros
st.sidebar.header("Filtros")

# Cargar datos de referencia para filtros
regiones = con.execute("""
    SELECT DISTINCT cod_region, region
    FROM comunas
    ORDER BY cod_region
""").df()

dependencias = con.execute("SELECT * FROM ref_dependencia ORDER BY codigo").df()
ramas = con.execute("SELECT * FROM ref_rama ORDER BY codigo").df()

# Filtros
region_sel = st.sidebar.multiselect(
    "Región",
    options=regiones['cod_region'].tolist(),
    format_func=lambda x: regiones[regiones['cod_region']==x]['region'].values[0] if len(regiones[regiones['cod_region']==x]) > 0 else str(x)
)

dep_sel = st.sidebar.multiselect(
    "Dependencia",
    options=dependencias['codigo'].tolist(),
    format_func=lambda x: dependencias[dependencias['codigo']==x]['descripcion'].values[0]
)

rama_sel = st.sidebar.multiselect(
    "Rama Educacional",
    options=ramas['codigo'].tolist(),
    format_func=lambda x: ramas[ramas['codigo']==x]['descripcion'].values[0]
)

# Construir cláusula WHERE
where_clauses = []
if region_sel:
    where_clauses.append(f"cod_region IN ({','.join(map(str, region_sel))})")
if dep_sel:
    where_clauses.append(f"dependencia IN ({','.join(map(str, dep_sel))})")
if rama_sel:
    rama_str = ','.join([f"'{r}'" for r in rama_sel])
    where_clauses.append(f"rama IN ({rama_str})")

where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📈 Resumen", "🏫 Por Establecimiento", "🗺️ Por Región", "🔍 Explorar Datos"])

with tab1:
    st.header("Resumen General")

    # Métricas generales
    stats = con.execute(f"""
        SELECT
            COUNT(*) as total,
            COUNT(lectora_reg) as rindieron_lectora,
            ROUND(AVG(lectora_reg), 1) as prom_lectora,
            ROUND(AVG(mate1_reg), 1) as prom_mate1,
            ROUND(AVG(puntaje_nem), 1) as prom_nem
        FROM resultados_paes
        WHERE {where_sql}
    """).df()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Postulantes", f"{stats['total'].values[0]:,}")
    col2.metric("Rindieron Lectora", f"{stats['rindieron_lectora'].values[0]:,}")
    col3.metric("Prom. Lectora", stats['prom_lectora'].values[0])
    col4.metric("Prom. Matemática 1", stats['prom_mate1'].values[0])
    col5.metric("Prom. NEM", stats['prom_nem'].values[0])

    # Gráficos en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribución por Dependencia")
        dep_data = con.execute(f"""
            SELECT
                d.descripcion as dependencia,
                COUNT(*) as cantidad,
                ROUND(AVG(r.lectora_reg), 1) as prom_lectora
            FROM resultados_paes r
            JOIN ref_dependencia d ON r.dependencia = d.codigo
            WHERE {where_sql}
            GROUP BY d.descripcion
            ORDER BY cantidad DESC
        """).df()

        fig = px.bar(dep_data, x='dependencia', y='cantidad',
                     color='prom_lectora', color_continuous_scale='RdYlGn',
                     labels={'cantidad': 'Postulantes', 'prom_lectora': 'Prom. Lectora'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Distribución por Rama")
        rama_data = con.execute(f"""
            SELECT
                rm.descripcion as rama,
                COUNT(*) as cantidad
            FROM resultados_paes r
            JOIN ref_rama rm ON r.rama = rm.codigo
            WHERE {where_sql}
            GROUP BY rm.descripcion
            ORDER BY cantidad DESC
        """).df()

        fig = px.pie(rama_data, values='cantidad', names='rama', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    # Histograma de puntajes
    st.subheader("Distribución de Puntajes PAES Regular")

    prueba_sel = st.selectbox(
        "Seleccionar Prueba",
        ["lectora_reg", "mate1_reg", "mate2_reg", "historia_reg", "ciencias_reg"],
        format_func=lambda x: {
            "lectora_reg": "Competencia Lectora",
            "mate1_reg": "Matemática 1",
            "mate2_reg": "Matemática 2",
            "historia_reg": "Historia y Cs. Sociales",
            "ciencias_reg": "Ciencias"
        }[x]
    )

    hist_data = con.execute(f"""
        SELECT {prueba_sel} as puntaje
        FROM resultados_paes
        WHERE {where_sql} AND {prueba_sel} IS NOT NULL
    """).df()

    fig = px.histogram(hist_data, x='puntaje', nbins=50,
                       labels={'puntaje': 'Puntaje', 'count': 'Frecuencia'})
    fig.add_vline(x=hist_data['puntaje'].mean(), line_dash="dash",
                  annotation_text=f"Promedio: {hist_data['puntaje'].mean():.1f}")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Análisis por Establecimiento")

    # Top establecimientos
    top_n = st.slider("Cantidad de establecimientos", 10, 50, 20)

    orden = st.radio("Ordenar por", ["Mejor promedio", "Peor promedio", "Más postulantes"], horizontal=True)

    order_sql = {
        "Mejor promedio": "prom_lectora DESC NULLS LAST",
        "Peor promedio": "prom_lectora ASC NULLS LAST",
        "Más postulantes": "cantidad DESC"
    }[orden]

    est_data = con.execute(f"""
        SELECT
            e.nombre as establecimiento,
            d.descripcion as dependencia,
            c.region,
            COUNT(*) as cantidad,
            ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
            ROUND(AVG(r.puntaje_nem), 1) as prom_nem
        FROM resultados_paes r
        JOIN establecimientos e ON r.rbd = e.rbd
        JOIN ref_dependencia d ON r.dependencia = d.codigo
        LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
        WHERE {where_sql} AND r.lectora_reg IS NOT NULL
        GROUP BY e.nombre, d.descripcion, c.region
        HAVING COUNT(*) >= 5
        ORDER BY {order_sql}
        LIMIT {top_n}
    """).df()

    st.dataframe(est_data, use_container_width=True, hide_index=True)

    # Gráfico de barras
    if not est_data.empty:
        fig = px.bar(est_data.head(20), x='establecimiento', y='prom_lectora',
                     color='dependencia',
                     hover_data=['prom_mate1', 'prom_nem', 'cantidad'])
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Análisis por Región")

    region_data = con.execute(f"""
        SELECT
            c.region,
            COUNT(*) as postulantes,
            COUNT(r.lectora_reg) as rindieron,
            ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
            ROUND(AVG(r.puntaje_nem), 1) as prom_nem,
            ROUND(AVG(r.puntaje_ranking), 1) as prom_ranking
        FROM resultados_paes r
        LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
        WHERE {where_sql}
        GROUP BY c.region
        ORDER BY prom_lectora DESC NULLS LAST
    """).df()

    st.dataframe(region_data, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(region_data, x='region', y='prom_lectora',
                     color='prom_lectora', color_continuous_scale='RdYlGn',
                     title="Promedio Competencia Lectora por Región")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(region_data, x='prom_nem', y='prom_lectora',
                         size='postulantes', hover_name='region',
                         title="NEM vs Lectora por Región")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Explorar Datos")

    st.subheader("Consulta SQL")

    default_query = """SELECT
    id, rbd, rama, dependencia,
    puntaje_nem, puntaje_ranking,
    lectora_reg, mate1_reg, mate2_reg
FROM resultados_paes
WHERE lectora_reg IS NOT NULL
LIMIT 100"""

    query = st.text_area("Escribir consulta SQL", value=default_query, height=150)

    if st.button("Ejecutar", type="primary"):
        try:
            result = con.execute(query).df()
            st.success(f"Resultados: {len(result)} filas")
            st.dataframe(result, use_container_width=True, hide_index=True)

            # Opción de descargar
            csv = result.to_csv(index=False)
            st.download_button(
                "Descargar CSV",
                csv,
                "resultado_paes.csv",
                "text/csv"
            )
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    st.subheader("Estructura de Tablas")

    tabla_sel = st.selectbox("Seleccionar tabla",
                              ["resultados_paes", "establecimientos", "comunas",
                               "cod_ensenanza", "ref_dependencia", "ref_rama",
                               "ref_situacion_egreso", "ref_modulo_ciencias"])

    schema = con.execute(f"DESCRIBE {tabla_sel}").df()
    st.dataframe(schema, use_container_width=True, hide_index=True)

# Footer
st.divider()
st.markdown("""
**Fuente:** [DEMRE - Portal de Transparencia](https://portal-transparencia.demre.cl/portal-base-datos) |
Proceso de Admisión 2026

---
Hecho con ❤️ por [Datalized](https://datalized.cl/)
""")
