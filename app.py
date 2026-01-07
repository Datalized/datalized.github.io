"""
PAES 2026 - Explorador de Datos
Aplicación Streamlit para visualizar resultados de la PAES
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_searchbox import st_searchbox

# Configuración de la página
st.set_page_config(
    page_title="PAES 2026 - Explorador",
    page_icon="📊",
    layout="wide"
)

# Conexión a la base de datos
# Siguiendo recomendaciones de https://duckdb.org/2025/03/28/using-duckdb-in-streamlit
# - Usar conexión por sesión de usuario (no global compartida entre usuarios)
# - TTL para refrescar conexiones periódicamente y evitar corrupción
import datetime

@st.cache_resource(ttl=datetime.timedelta(hours=1))
def get_connection(_session_id):
    """Conexión DuckDB por sesión de usuario con TTL de 1 hora."""
    return duckdb.connect("paes.duckdb", read_only=True)

# Usar session_id para que cada usuario tenga su propia conexión cacheada
con = get_connection(st.session_state.get("_session_id", id(st.session_state)))

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

# Colores consistentes por dependencia (usados en toda la app)
COLORES_DEPENDENCIA = {
    'Particular Pagado': '#E63946',      # Rojo
    'Particular Subvencionado': '#457B9D',  # Azul
    'Municipal': '#2A9D8F',              # Verde azulado
    'Serv. Local Educación': '#E9C46A',  # Amarillo
    'Corp. Administración Delegada': '#9B5DE5'  # Púrpura
}

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    """Calcula la distancia en km entre dos puntos usando fórmula de Haversine"""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Radio de la Tierra en km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Resumen", "🏫 Por Establecimiento", "🔍 Buscar Establecimiento", "🗺️ Por Región", "📊 Análisis de Brechas"])

with tab1:
    st.header("Resumen General")

    # Métricas generales
    stats = con.execute(f"""
        SELECT
            COUNT(*) as total,
            COUNT(lectora_reg) as rindieron_lectora,
            COUNT(mate1_reg) as rindieron_mate1,
            ROUND(AVG(lectora_reg), 1) as prom_lectora,
            ROUND(AVG(mate1_reg), 1) as prom_mate1,
            ROUND(AVG(puntaje_nem), 1) as prom_nem
        FROM resultados_paes r
        WHERE {where_sql}
    """).df()

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Postulantes", f"{stats['total'].values[0]:,}")
    col2.metric("Rindieron Lectora", f"{stats['rindieron_lectora'].values[0]:,}")
    col3.metric("Rindieron Mate 1", f"{stats['rindieron_mate1'].values[0]:,}")
    col4.metric("Prom. Lectora", stats['prom_lectora'].values[0])
    col5.metric("Prom. Matemática 1", stats['prom_mate1'].values[0])
    col6.metric("Prom. NEM", stats['prom_nem'].values[0])

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
                     color='dependencia',
                     color_discrete_map=COLORES_DEPENDENCIA,
                     hover_data=['prom_lectora'],
                     labels={'cantidad': 'Postulantes', 'prom_lectora': 'Prom. Lectora'})
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")

    # Histograma de puntajes
    st.subheader("Distribución de Puntajes PAES Regular")

    col_lect, col_mate = st.columns(2)

    with col_lect:
        st.markdown("**Competencia Lectora**")
        hist_lectora = con.execute(f"""
            SELECT
                d.descripcion as dependencia,
                r.lectora_reg as puntaje
            FROM resultados_paes r
            JOIN ref_dependencia d ON r.dependencia = d.codigo
            WHERE {where_sql} AND r.lectora_reg IS NOT NULL
        """).df()

        fig = px.histogram(hist_lectora, x='puntaje', color='dependencia', nbins=50,
                           color_discrete_map=COLORES_DEPENDENCIA,
                           labels={'puntaje': 'Puntaje', 'count': 'Frecuencia'},
                           barmode='stack')
        fig.add_vline(x=hist_lectora['puntaje'].mean(), line_dash="dash",
                      annotation_text=f"Prom: {hist_lectora['puntaje'].mean():.1f}")
        fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, width="stretch")

    with col_mate:
        st.markdown("**Matemática 1**")
        hist_mate = con.execute(f"""
            SELECT
                d.descripcion as dependencia,
                r.mate1_reg as puntaje
            FROM resultados_paes r
            JOIN ref_dependencia d ON r.dependencia = d.codigo
            WHERE {where_sql} AND r.mate1_reg IS NOT NULL
        """).df()

        fig = px.histogram(hist_mate, x='puntaje', color='dependencia', nbins=50,
                           color_discrete_map=COLORES_DEPENDENCIA,
                           labels={'puntaje': 'Puntaje', 'count': 'Frecuencia'},
                           barmode='stack')
        fig.add_vline(x=hist_mate['puntaje'].mean(), line_dash="dash",
                      annotation_text=f"Prom: {hist_mate['puntaje'].mean():.1f}")
        fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, width="stretch")

with tab2:
    st.header("Análisis por Establecimiento")

    st.info("💡 **Nota metodológica**: El DEMRE advierte que la PAES no fue diseñada para medir calidad educativa de establecimientos. Los rankings reflejan principalmente el nivel socioeconómico de los estudiantes. Use la opción 'Comparación Contextualizada' para comparaciones más justas.")

    # Sub-tabs para diferentes vistas
    sub_tab1, sub_tab2 = st.tabs(["📋 Ranking General", "⚖️ Comparación Contextualizada"])

    with sub_tab1:
        # Top establecimientos (ranking original)
        top_n = st.slider("Cantidad de establecimientos", 10, 50, 20, key="ranking_slider")

        orden = st.radio("Ordenar por", ["Mejor promedio", "Peor promedio", "Más postulantes", "Más alumnos en top 10%"], horizontal=True)

        order_sql = {
            "Mejor promedio": "prom_lect_mate DESC NULLS LAST",
            "Peor promedio": "prom_lect_mate ASC NULLS LAST",
            "Más postulantes": "cantidad DESC",
            "Más alumnos en top 10%": "en_top10 DESC"
        }[orden]

        # Calcular umbral top 10%
        p90_threshold = con.execute("""
            SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2) as p90
            FROM resultados_paes
            WHERE lectora_reg IS NOT NULL AND mate1_reg IS NOT NULL
        """).df()['p90'].values[0]

        est_data = con.execute(f"""
            SELECT
                e.nombre as establecimiento,
                d.descripcion as dependencia,
                c.region,
                COUNT(*) as cantidad,
                ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
                ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
                ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg)) / 2, 1) as prom_lect_mate,
                ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p25,
                ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p75,
                SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90_threshold} THEN 1 ELSE 0 END) as en_top10,
                ROUND(AVG(r.puntaje_nem), 1) as prom_nem
            FROM resultados_paes r
            JOIN establecimientos e ON r.rbd = e.rbd
            JOIN ref_dependencia d ON r.dependencia = d.codigo
            LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
            WHERE {where_sql} AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
            GROUP BY e.nombre, d.descripcion, c.region
            HAVING COUNT(*) >= 5
            ORDER BY {order_sql}
            LIMIT {top_n}
        """).df()

        # Agregar columna de ranking
        est_data.insert(0, 'ranking', range(1, len(est_data) + 1))

        st.dataframe(est_data, width="stretch", hide_index=True)

        # Gráfico de barras horizontal
        if not est_data.empty:
            chart_data = est_data.head(20).copy()
            chart_data = chart_data.iloc[::-1]  # Invertir para que el primero quede arriba
            fig = px.bar(chart_data, y='establecimiento', x='prom_lect_mate',
                         color='dependencia',
                         color_discrete_map=COLORES_DEPENDENCIA,
                         hover_data=['prom_lectora', 'prom_mate1', 'p25', 'p75', 'cantidad', 'en_top10'],
                         labels={'prom_lect_mate': 'Promedio Lectora+Mate1', 'establecimiento': ''},
                         orientation='h')
            fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, width="stretch")

    with sub_tab2:
        st.subheader("Comparación entre establecimientos similares")
        st.caption("Compare establecimientos según los filtros seleccionados en el sidebar")

        top_n_ctx = st.slider("Cantidad de establecimientos", 10, 50, 20, key="ctx_slider")

        orden_ctx = st.radio("Ordenar por", ["Mejor promedio", "Peor promedio", "Más postulantes", "Más alumnos en top 10%"], horizontal=True, key="orden_ctx")

        order_sql_ctx = {
            "Mejor promedio": "promedio DESC NULLS LAST",
            "Peor promedio": "promedio ASC NULLS LAST",
            "Más postulantes": "estudiantes DESC",
            "Más alumnos en top 10%": "en_top10_nacional DESC"
        }[orden_ctx]

        # Ranking contextualizado aplicando filtros del sidebar
        est_ctx = con.execute(f"""
            SELECT
                e.nombre as establecimiento,
                d.descripcion as dependencia,
                c.region,
                COUNT(*) as estudiantes,
                ROUND(AVG((r.lectora_reg + r.mate1_reg)/2), 1) as promedio,
                ROUND(PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p10,
                ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as mediana,
                ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p90,
                SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90_threshold} THEN 1 ELSE 0 END) as en_top10_nacional
            FROM resultados_paes r
            JOIN establecimientos e ON r.rbd = e.rbd
            JOIN ref_dependencia d ON r.dependencia = d.codigo
            LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
            WHERE {where_sql} AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
            GROUP BY e.nombre, d.descripcion, c.region
            HAVING COUNT(*) >= 5
            ORDER BY {order_sql_ctx}
            LIMIT {top_n_ctx}
        """).df()

        # Agregar columna de ranking
        est_ctx.insert(0, 'ranking', range(1, len(est_ctx) + 1))

        st.dataframe(est_ctx, width="stretch", hide_index=True)

        # Gráfico de barras horizontal con color por dependencia
        if not est_ctx.empty:
            chart_ctx = est_ctx.head(20).copy()
            chart_ctx = chart_ctx.iloc[::-1]  # Invertir para que el primero quede arriba
            fig = px.bar(chart_ctx, y='establecimiento', x='promedio',
                         color='dependencia',
                         color_discrete_map=COLORES_DEPENDENCIA,
                         hover_data=['mediana', 'p10', 'p90', 'estudiantes', 'en_top10_nacional'],
                         labels={'promedio': 'Promedio Lectora+Mate1', 'establecimiento': ''},
                         orientation='h')
            fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, width="stretch")

with tab3:
    st.header("Buscar Establecimiento")

    st.markdown("Busca un establecimiento para ver los resultados individuales de sus estudiantes y comparar con colegios cercanos.")

    # Obtener lista de establecimientos con resultados PAES
    establecimientos_con_paes = con.execute("""
        SELECT DISTINCT
            e.rbd,
            e.nombre,
            e.nom_comuna,
            e.nom_region,
            e.latitud,
            e.longitud,
            COUNT(r.id) as n_estudiantes
        FROM establecimientos e
        INNER JOIN resultados_paes r ON e.rbd = r.rbd
        WHERE r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
        GROUP BY e.rbd, e.nombre, e.nom_comuna, e.nom_region, e.latitud, e.longitud
        HAVING COUNT(r.id) >= 1
        ORDER BY e.nombre
    """).df()

    # Crear lista de opciones como tuplas (label, rbd) para el searchbox
    opciones_lista = [
        (f"{row['nombre']} - {row['nom_comuna']} ({row['n_estudiantes']} est.)", row['rbd'])
        for _, row in establecimientos_con_paes.iterrows()
    ]

    # Función de búsqueda para el searchbox
    def buscar_establecimiento(searchterm: str):
        if not searchterm:
            return []
        return [opt for opt in opciones_lista if searchterm.lower() in opt[0].lower()][:20]

    # Searchbox con autocompletado
    rbd_seleccionado = st_searchbox(
        buscar_establecimiento,
        placeholder="Buscar establecimiento (ej: Instituto Nacional...)",
        key="searchbox_establecimiento",
        clear_on_submit=False,
    )

    if rbd_seleccionado:
        # Información del establecimiento
        info_estab = con.execute(f"""
            SELECT
                e.nombre,
                e.nom_comuna,
                e.nom_region,
                e.latitud,
                e.longitud,
                e.mat_total,
                e.rural,
                e.convenio_pie,
                e.pace,
                e.pago_mensual,
                dm.descripcion as dependencia
            FROM establecimientos e
            LEFT JOIN ref_dependencia_mineduc2 dm ON e.cod_depe2 = dm.codigo
            WHERE e.rbd = {rbd_seleccionado}
        """).df()

        if not info_estab.empty:
            estab_info = info_estab.iloc[0]

            st.subheader(f"📍 {estab_info['nombre']}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Comuna", estab_info['nom_comuna'])
            col2.metric("Región", estab_info['nom_region'])
            col3.metric("Dependencia", estab_info['dependencia'] or "Sin info")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Matrícula Total", f"{estab_info['mat_total'] or 0:,}")
            col2.metric("Zona", "Rural" if estab_info['rural'] == 1 else "Urbana")
            col3.metric("Convenio PIE", "Sí" if estab_info['convenio_pie'] == 1 else "No")
            col4.metric("Programa PACE", "Sí" if estab_info['pace'] == 1 else "No")

            st.divider()

            # Datos de los estudiantes del establecimiento
            estudiantes = con.execute(f"""
                SELECT
                    r.lectora_reg,
                    r.mate1_reg,
                    r.mate2_reg,
                    r.historia_reg,
                    r.ciencias_reg,
                    r.puntaje_nem,
                    r.puntaje_ranking,
                    d.descripcion as dependencia,
                    rm.descripcion as rama
                FROM resultados_paes r
                LEFT JOIN ref_dependencia d ON r.dependencia = d.codigo
                LEFT JOIN ref_rama rm ON r.rama = rm.codigo
                WHERE r.rbd = {rbd_seleccionado}
                AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
            """).df()

            if not estudiantes.empty:
                # Estadísticas agregadas
                st.subheader("📊 Resultados PAES del Establecimiento")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Estudiantes", len(estudiantes))
                col2.metric("Prom. Lectora", f"{estudiantes['lectora_reg'].mean():.1f}")
                col3.metric("Prom. Matemática 1", f"{estudiantes['mate1_reg'].mean():.1f}")
                prom_lm = (estudiantes['lectora_reg'] + estudiantes['mate1_reg']) / 2
                col4.metric("Prom. Lect+Mate", f"{prom_lm.mean():.1f}")

                # Scatter plot de resultados individuales
                st.subheader("🔵 Resultados Individuales: Matemática 1 vs Lectora")

                fig = px.scatter(estudiantes, x='lectora_reg', y='mate1_reg',
                                 hover_data=['puntaje_nem', 'rama'],
                                 labels={'lectora_reg': 'Competencia Lectora', 'mate1_reg': 'Matemática 1'},
                                 opacity=0.7)
                fig.update_traces(marker=dict(size=10, color='#457B9D'))

                # Añadir líneas de referencia (promedios nacionales aproximados)
                fig.add_hline(y=500, line_dash="dot", line_color="gray", annotation_text="Prom. Nacional M1")
                fig.add_vline(x=500, line_dash="dot", line_color="gray", annotation_text="Prom. Nacional Lect")

                fig.update_layout(height=500)
                st.plotly_chart(fig, width="stretch")

                # Box plots de puntajes
                st.subheader("📦 Distribución de Puntajes")

                pruebas_data = pd.DataFrame({
                    'Prueba': ['Lectora']*len(estudiantes) + ['Matemática 1']*len(estudiantes),
                    'Puntaje': list(estudiantes['lectora_reg']) + list(estudiantes['mate1_reg'])
                })

                fig = px.box(pruebas_data, x='Prueba', y='Puntaje', color='Prueba')
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, width="stretch")

                st.divider()

                # Sección de colegios cercanos
                st.subheader("🏫 Colegios Cercanos y Comparación")

                if estab_info['latitud'] and estab_info['longitud']:
                    lat_ref = estab_info['latitud']
                    lon_ref = estab_info['longitud']

                    # Obtener colegios cercanos (misma comuna o por distancia)
                    colegios_cercanos = con.execute(f"""
                        SELECT
                            e.rbd,
                            e.nombre,
                            e.nom_comuna,
                            e.latitud,
                            e.longitud,
                            dm.descripcion as dependencia,
                            COUNT(r.id) as n_estudiantes,
                            ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
                            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
                            ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg))/2, 1) as prom_lect_mate
                        FROM establecimientos e
                        INNER JOIN resultados_paes r ON e.rbd = r.rbd
                        LEFT JOIN ref_dependencia_mineduc2 dm ON e.cod_depe2 = dm.codigo
                        WHERE r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
                        AND e.latitud IS NOT NULL AND e.longitud IS NOT NULL
                        AND e.rbd != {rbd_seleccionado}
                        GROUP BY e.rbd, e.nombre, e.nom_comuna, e.latitud, e.longitud, dm.descripcion
                        HAVING COUNT(r.id) >= 5
                    """).df()

                    if not colegios_cercanos.empty:
                        # Calcular distancias
                        colegios_cercanos['distancia_km'] = colegios_cercanos.apply(
                            lambda row: calcular_distancia_km(lat_ref, lon_ref, row['latitud'], row['longitud']),
                            axis=1
                        )

                        # Filtrar por distancia (máximo 10 km) y ordenar
                        cercanos = colegios_cercanos[colegios_cercanos['distancia_km'] <= 10].sort_values('distancia_km').head(15)

                        if not cercanos.empty:
                            st.caption(f"Mostrando {len(cercanos)} establecimientos a menos de 10 km")

                            # Agregar el establecimiento seleccionado para comparación
                            estab_actual = pd.DataFrame({
                                'nombre': [estab_info['nombre']],
                                'nom_comuna': [estab_info['nom_comuna']],
                                'dependencia': [estab_info['dependencia']],
                                'n_estudiantes': [len(estudiantes)],
                                'prom_lectora': [estudiantes['lectora_reg'].mean()],
                                'prom_mate1': [estudiantes['mate1_reg'].mean()],
                                'prom_lect_mate': [prom_lm.mean()],
                                'distancia_km': [0],
                                'es_seleccionado': [True]
                            })

                            cercanos['es_seleccionado'] = False
                            comparacion = pd.concat([estab_actual, cercanos[['nombre', 'nom_comuna', 'dependencia', 'n_estudiantes', 'prom_lectora', 'prom_mate1', 'prom_lect_mate', 'distancia_km', 'es_seleccionado']]], ignore_index=True)

                            # Gráfico de comparación
                            fig = px.bar(comparacion, x='nombre', y='prom_lect_mate',
                                         color='dependencia',
                                         color_discrete_map=COLORES_DEPENDENCIA,
                                         hover_data=['nom_comuna', 'n_estudiantes', 'distancia_km'],
                                         labels={'prom_lect_mate': 'Promedio Lect+Mate', 'nombre': ''})
                            fig.update_layout(xaxis_tickangle=-45, height=500)

                            # Destacar el establecimiento seleccionado
                            fig.add_annotation(x=estab_info['nombre'], y=prom_lm.mean() + 20,
                                               text="⭐ Seleccionado", showarrow=False)

                            st.plotly_chart(fig, width="stretch")

                            # Tabla de comparación
                            tabla_comp = comparacion[['nombre', 'dependencia', 'n_estudiantes', 'prom_lectora', 'prom_mate1', 'prom_lect_mate', 'distancia_km']].copy()
                            tabla_comp.columns = ['Establecimiento', 'Dependencia', 'Estudiantes', 'Prom. Lectora', 'Prom. Mate1', 'Prom. L+M', 'Distancia (km)']
                            tabla_comp['Distancia (km)'] = tabla_comp['Distancia (km)'].round(1)
                            st.dataframe(tabla_comp, width="stretch", hide_index=True)
                        else:
                            st.info("No se encontraron establecimientos con resultados PAES a menos de 10 km")
                else:
                    st.warning("Este establecimiento no tiene coordenadas geográficas registradas para buscar colegios cercanos")

                    # Mostrar comparación por comuna si no hay coordenadas
                    st.subheader("🏘️ Comparación con establecimientos de la misma comuna")
                    comuna = estab_info['nom_comuna']

                    comp_comuna = con.execute(f"""
                        SELECT
                            e.nombre,
                            dm.descripcion as dependencia,
                            COUNT(r.id) as n_estudiantes,
                            ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
                            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
                            ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg))/2, 1) as prom_lect_mate
                        FROM establecimientos e
                        INNER JOIN resultados_paes r ON e.rbd = r.rbd
                        LEFT JOIN ref_dependencia_mineduc2 dm ON e.cod_depe2 = dm.codigo
                        WHERE e.nom_comuna = '{comuna}'
                        AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
                        GROUP BY e.nombre, dm.descripcion
                        HAVING COUNT(r.id) >= 5
                        ORDER BY prom_lect_mate DESC
                    """).df()

                    if not comp_comuna.empty:
                        st.dataframe(comp_comuna, width="stretch", hide_index=True)
            else:
                st.warning("No se encontraron datos de estudiantes para este establecimiento")

with tab4:
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
            ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg))/2, 1) as prom_lect_mate,
            ROUND(AVG(r.puntaje_nem), 1) as prom_nem
        FROM resultados_paes r
        LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
        WHERE {where_sql}
        GROUP BY c.cod_region, c.region
        ORDER BY c.cod_region
    """).df()

    # Ordenar geográficamente
    region_data['orden'] = region_data['cod_region'].map(ORDEN_REGIONES)
    region_data = region_data.sort_values('orden')

    # Selector de región para filtrar comunas
    region_options = ["Todas las regiones"] + region_data['region'].tolist()
    selected_region = st.selectbox("Seleccionar región para ver sus comunas", region_options, key="region_selector")

    # Mostrar tabla sin cod_region y orden
    region_display = region_data.drop(columns=['orden', 'cod_region'])
    st.dataframe(region_display, width="stretch", hide_index=True)

    st.divider()

    # Top comunas por promedio Lectora + Matemática 1
    st.subheader("Top 20 Comunas por Promedio Lectora + Matemática 1")

    # Construir filtro de región para comunas
    if selected_region != "Todas las regiones":
        cod_region_sel = region_data[region_data['region'] == selected_region]['cod_region'].values[0]
        region_filter = f"AND c.cod_region = {cod_region_sel}"
    else:
        region_filter = ""

    comuna_data = con.execute(f"""
        SELECT
            c.comuna,
            c.region,
            COUNT(*) as alumnos,
            ROUND((AVG(r.mate1_reg) + AVG(r.lectora_reg))/2, 1) as prom_lect_mate,
            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
            ROUND(AVG(r.lectora_reg), 1) as prom_lectora
        FROM resultados_paes r
        LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
        WHERE {where_sql} AND r.mate1_reg IS NOT NULL AND r.lectora_reg IS NOT NULL {region_filter}
        GROUP BY c.comuna, c.region
        HAVING COUNT(*) >= 10
        ORDER BY prom_lect_mate DESC
        LIMIT 20
    """).df()

    fig = px.bar(comuna_data, x='comuna', y='prom_lect_mate',
                 color='prom_lect_mate', color_continuous_scale='RdYlGn',
                 hover_data=['region', 'alumnos', 'prom_lectora', 'prom_mate1'],
                 labels={'prom_lect_mate': 'Promedio Lectora + Mate1', 'comuna': 'Comuna'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, width="stretch")

    st.divider()

    # Scatter de establecimientos
    st.subheader("Establecimientos: Lectora vs Matemática 1")

    est_scatter = con.execute(f"""
        SELECT
            e.nombre as establecimiento,
            d.descripcion as dependencia,
            c.comuna,
            c.region,
            COUNT(*) as alumnos,
            ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
            ROUND(AVG(r.lectora_reg), 1) as prom_lectora
        FROM resultados_paes r
        JOIN establecimientos e ON r.rbd = e.rbd
        JOIN ref_dependencia d ON r.dependencia = d.codigo
        LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
        WHERE {where_sql} AND r.mate1_reg IS NOT NULL AND r.lectora_reg IS NOT NULL {region_filter}
        GROUP BY e.nombre, d.descripcion, c.comuna, c.region
        HAVING COUNT(*) >= 5
    """).df()

    fig = px.scatter(est_scatter, x='prom_lectora', y='prom_mate1',
                     size='alumnos', hover_name='establecimiento',
                     hover_data=['comuna', 'region', 'alumnos'],
                     labels={'prom_lectora': 'Promedio Lectora', 'prom_mate1': 'Promedio Matemática 1'},
                     color='dependencia', color_discrete_map=COLORES_DEPENDENCIA)
    fig.update_layout(height=600)
    st.plotly_chart(fig, width="stretch")

with tab5:
    st.header("Análisis de Brechas Educativas")

    st.markdown("""
    Este análisis responde a la pregunta: **¿De dónde viene realmente el talento académico?**

    Los rankings tradicionales de "mejores colegios" pueden ser engañosos porque:
    - Miden principalmente el nivel socioeconómico, no la calidad educativa
    - Invisibilizan a miles de estudiantes destacados de colegios públicos
    - No consideran el contexto ni el valor agregado de cada establecimiento

    *Inspirado en el análisis de [@elaval](https://elaval.github.io/PAES-2026/)*
    """)

    st.divider()

    # Calcular umbrales del top 10% y 20%
    thresholds = con.execute("""
        SELECT
            PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2) as p90,
            PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2) as p80
        FROM resultados_paes
        WHERE lectora_reg IS NOT NULL AND mate1_reg IS NOT NULL
    """).df()
    p90 = thresholds['p90'].values[0]
    p80 = thresholds['p80'].values[0]

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Umbral Top 10%", f"{p90:.0f} pts", help="Promedio Lectora + Matemática 1")
    col2.metric("Umbral Top 20%", f"{p80:.0f} pts", help="Promedio Lectora + Matemática 1")

    total_top10 = con.execute(f"""
        SELECT COUNT(*) FROM resultados_paes
        WHERE (lectora_reg + mate1_reg)/2 >= {p90}
        AND lectora_reg IS NOT NULL AND mate1_reg IS NOT NULL
    """).df().iloc[0, 0]
    col3.metric("Estudiantes en Top 10%", f"{total_top10:,}")

    st.divider()

    # Sección 1: Origen del Top 10%
    st.subheader("🎯 ¿De dónde vienen los estudiantes del Top 10%?")

    origen_top10 = con.execute(f"""
        SELECT
            d.descripcion as dependencia,
            COUNT(*) as estudiantes,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as porcentaje
        FROM resultados_paes r
        JOIN ref_dependencia d ON r.dependencia = d.codigo
        WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90}
        AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
        GROUP BY d.descripcion
        ORDER BY estudiantes DESC
    """).df()

    # Tabla resumen
    st.dataframe(origen_top10, width="stretch", hide_index=True)

    # Calcular % no particular pagado
    pct_no_pagado = origen_top10[origen_top10['dependencia'] != 'Particular Pagado']['porcentaje'].sum()
    st.success(f"**{pct_no_pagado:.1f}%** del Top 10% NO viene de colegios particulares pagados")

    # Obtener datos detallados por establecimiento para visualización de cuadros
    escuelas_top10 = con.execute(f"""
        SELECT
            e.nombre as establecimiento,
            d.descripcion as dependencia,
            COUNT(*) as estudiantes_top10
        FROM resultados_paes r
        JOIN establecimientos e ON r.rbd = e.rbd
        JOIN ref_dependencia d ON r.dependencia = d.codigo
        WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90}
        AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
        GROUP BY e.nombre, d.descripcion
        HAVING COUNT(*) >= 1
        ORDER BY estudiantes_top10 DESC
    """).df()

    # Treemap con cuadros por establecimiento agrupados por dependencia
    fig = px.treemap(escuelas_top10,
                     path=['dependencia', 'establecimiento'],
                     values='estudiantes_top10',
                     color='dependencia',
                     color_discrete_map=COLORES_DEPENDENCIA,
                     title="Establecimientos con estudiantes en el Top 10% (tamaño = cantidad de estudiantes)")
    fig.update_traces(textinfo="label+value")
    fig.update_layout(height=600)
    st.plotly_chart(fig, width="stretch")

    st.divider()

    # Sección 2: Box plots por dependencia
    st.subheader("📊 Distribución de puntajes por tipo de establecimiento")
    st.caption("Los box plots muestran la distribución completa, no solo promedios")

    # Obtener datos para box plot (muestra para rendimiento)
    box_data = con.execute(f"""
        SELECT
            d.descripcion as dependencia,
            (r.lectora_reg + r.mate1_reg)/2 as promedio
        FROM resultados_paes r
        JOIN ref_dependencia d ON r.dependencia = d.codigo
        WHERE {where_sql} AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
        USING SAMPLE 10 PERCENT (bernoulli)
    """).df()

    fig = px.box(box_data, x='dependencia', y='promedio',
                 color='dependencia',
                 color_discrete_map=COLORES_DEPENDENCIA,
                 labels={'promedio': 'Promedio Lectora + Matemática 1', 'dependencia': 'Dependencia'},
                 title="Distribución de puntajes por dependencia")
    fig.add_hline(y=p90, line_dash="dash", line_color="green",
                  annotation_text=f"Top 10% ({p90:.0f})")
    fig.add_hline(y=p80, line_dash="dot", line_color="orange",
                  annotation_text=f"Top 20% ({p80:.0f})")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

    st.divider()

    # Sección 3: Probabilidad de estar en el Top por dependencia
    st.subheader("📈 ¿Qué tan probable es estar en el Top según tu colegio?")

    prob_data = con.execute(f"""
        SELECT
            d.descripcion as dependencia,
            COUNT(*) as total,
            SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) as en_top10,
            SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p80} THEN 1 ELSE 0 END) as en_top20,
            ROUND(100.0 * SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_top10,
            ROUND(100.0 * SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p80} THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_top20
        FROM resultados_paes r
        JOIN ref_dependencia d ON r.dependencia = d.codigo
        WHERE r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
        GROUP BY d.descripcion
        ORDER BY pct_top10 DESC
    """).df()

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(prob_data, x='dependencia', y='pct_top10',
                     color='dependencia',
                     color_discrete_map=COLORES_DEPENDENCIA,
                     text='pct_top10',
                     labels={'pct_top10': '% en Top 10%'},
                     title="% de estudiantes en el Top 10% nacional")
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(prob_data, x='dependencia', y='pct_top20',
                     color='dependencia',
                     color_discrete_map=COLORES_DEPENDENCIA,
                     text='pct_top20',
                     labels={'pct_top20': '% en Top 20%'},
                     title="% de estudiantes en el Top 20% nacional")
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.dataframe(prob_data, width="stretch", hide_index=True)

# Footer
st.divider()
st.markdown("""
**Fuente:** [DEMRE - Portal de Transparencia](https://portal-transparencia.demre.cl/portal-base-datos) |
Proceso de Admisión 2026

---
Hecho con ❤️ por [Datalized](https://datalized.cl/)
""")
