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

# Orden geográfico de regiones (norte a sur)
ORDEN_REGIONES = {
    15: 1,   # Arica y Parinacota
    1: 2,    # Tarapacá
    2: 3,    # Antofagasta
    3: 4,    # Atacama
    4: 5,    # Coquimbo
    5: 6,    # Valparaíso
    13: 7,   # Metropolitana
    6: 8,    # O'Higgins
    7: 9,    # Maule
    16: 10,  # Ñuble
    8: 11,   # Biobío
    9: 12,   # Araucanía
    14: 13,  # Los Ríos
    10: 14,  # Los Lagos
    11: 15,  # Aysén
    12: 16,  # Magallanes
}

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

# Ordenar regiones geográficamente
regiones['orden'] = regiones['cod_region'].map(ORDEN_REGIONES)
regiones = regiones.sort_values('orden')

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
    where_clauses.append(f"r.cod_region IN ({','.join(map(str, region_sel))})")
if dep_sel:
    where_clauses.append(f"r.dependencia IN ({','.join(map(str, dep_sel))})")
if rama_sel:
    rama_str = ','.join([f"'{r}'" for r in rama_sel])
    where_clauses.append(f"r.rama IN ({rama_str})")

where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📈 Resumen", "🏫 Por Establecimiento", "🗺️ Por Región"])

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
        FROM resultados_paes r
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
        FROM resultados_paes r
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

    # Datos por región ordenados geográficamente
    region_data = con.execute(f"""
        SELECT
            c.cod_region,
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
        GROUP BY c.cod_region, c.region
        ORDER BY c.cod_region
    """).df()

    # Ordenar geográficamente
    region_data['orden'] = region_data['cod_region'].map(ORDEN_REGIONES)
    region_data = region_data.sort_values('orden').drop(columns=['orden', 'cod_region'])

    st.dataframe(region_data, use_container_width=True, hide_index=True)

    st.divider()

    # Top comunas por promedio Matemática 1
    st.subheader("Top 20 Comunas por Promedio Matemática 1")

    comuna_data = con.execute(f"""
        SELECT
            c.comuna,
            c.region,
            COUNT(*) as alumnos,
            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
            ROUND(AVG(r.lectora_reg), 1) as prom_lectora
        FROM resultados_paes r
        LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
        WHERE {where_sql} AND r.mate1_reg IS NOT NULL
        GROUP BY c.comuna, c.region
        HAVING COUNT(*) >= 10
        ORDER BY prom_mate1 DESC
        LIMIT 20
    """).df()

    fig = px.bar(comuna_data, x='comuna', y='prom_mate1',
                 color='prom_mate1', color_continuous_scale='RdYlGn',
                 hover_data=['region', 'alumnos', 'prom_lectora'],
                 labels={'prom_mate1': 'Promedio Matemática 1', 'comuna': 'Comuna'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Scatter de establecimientos
    st.subheader("Establecimientos: Lectora vs Matemática 1")

    est_scatter = con.execute(f"""
        SELECT
            e.nombre as establecimiento,
            c.comuna,
            c.region,
            COUNT(*) as alumnos,
            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
            ROUND(AVG(r.lectora_reg), 1) as prom_lectora
        FROM resultados_paes r
        JOIN establecimientos e ON r.rbd = e.rbd
        LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
        WHERE {where_sql} AND r.mate1_reg IS NOT NULL AND r.lectora_reg IS NOT NULL
        GROUP BY e.nombre, c.comuna, c.region
        HAVING COUNT(*) >= 5
    """).df()

    fig = px.scatter(est_scatter, x='prom_lectora', y='prom_mate1',
                     size='alumnos', hover_name='establecimiento',
                     hover_data=['comuna', 'region', 'alumnos'],
                     labels={'prom_lectora': 'Promedio Lectora', 'prom_mate1': 'Promedio Matemática 1'},
                     color='prom_mate1', color_continuous_scale='RdYlGn')
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.markdown("""
**Fuente:** [DEMRE - Portal de Transparencia](https://portal-transparencia.demre.cl/portal-base-datos) |
Proceso de Admisión 2026

---
Hecho con ❤️ por [Datalized](https://datalized.cl/)
""")
