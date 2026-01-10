---
title: Ficha colegios - Buscar Establecimiento
toc: false
style: styles.css
head: |
  <link rel="canonical" href="https://public.datalized.cl/paes-2026/ficha">
  <meta name="description" content="Busca cualquier establecimiento educacional y explora su desempeño en la PAES 2026. Promedios, distribución de puntajes y comparación comunal.">
  <meta property="og:title" content="PAES 2026 - Ficha colegios">
  <meta property="og:description" content="Busca y compara el desempeño de establecimientos en la PAES 2026.">
  <meta property="og:url" content="https://public.datalized.cl/paes-2026/ficha">
  <meta property="og:type" content="website">
---

```js
const escuelas = FileAttachment("data/escuelas-ranking.json").json();
const filtros = FileAttachment("data/filtros.json").json();
import { rankBadge, depBadge, scoreValue, top10Indicator, rankingAlign, tableHeaders } from "./components/tableFormatters.js";
import { statsGrid } from "./components/statCard.js";
```

```js
import { coloresDependencia } from "./components/constants.js";

// Leer parámetro RBD de la URL (después de que escuelas esté cargado)
const urlParams = new URLSearchParams(window.location.search);
const rbdParam = urlParams.get('rbd');
const rbdSeleccionado = rbdParam ? parseInt(rbdParam) : null;
const escuelaPreseleccionada = rbdSeleccionado ? escuelas.find(d => d.rbd === rbdSeleccionado) : null;
```

```js
// Si hay una escuela preseleccionada, mostrar su ficha
if (escuelaPreseleccionada) {
  const e = escuelaPreseleccionada;

  display(html`
    <nav style="margin-bottom: 1rem; font-size: 0.875rem;">
      <a href="./ficha" style="color: var(--datalized-teal);">← Volver al directorio</a>
    </nav>
  `);

  display(html`
    <div class="school-header" style="border-left: 4px solid ${coloresDependencia[e.dependencia]}">
      <h1 style="margin-bottom: 0.5rem; font-size: 1.75rem;">${e.establecimiento}</h1>
      <div class="school-meta">
        <span><strong>RBD:</strong> ${e.rbd}</span>
        <span><strong>Comuna:</strong> ${e.comuna}</span>
        <span><strong>Región:</strong> ${e.region}</span>
        <span><strong>Dependencia:</strong> ${e.dependencia}</span>
        <span><strong>Estudiantes:</strong> ${e.cantidad}</span>
      </div>
    </div>
  `);

  display(html`<h2 class="section-title">Promedios por Prueba</h2>`);
  display(html`<p>Los promedios de puntajes obtenidos por los estudiantes del establecimiento en las pruebas obligatorias. El promedio Lectora + Matemática (L+M) es el indicador principal utilizado para el ranking.</p>`);

  display(statsGrid([
    { title: "Ranking Nacional", value: `#${e.rank_nacional}`, subtitle: `de ${escuelas.length.toLocaleString()}` },
    { title: "Ranking Comunal", value: `#${e.rank_comuna}` },
    { title: "Prom. Lectora", value: e.prom_lectora },
    { title: "Prom. Mate 1", value: e.prom_mate1 },
    { title: "Prom. L+M", value: e.prom_lect_mate, highlight: true }
  ]));

  display(html`<h2 class="section-title">Distribución de Puntajes</h2>`);
  display(html`<p>La distribución de puntajes muestra cómo varían los resultados dentro del establecimiento. El percentil 25 indica que el 25% de estudiantes obtuvo ese puntaje o menos, la mediana (percentil 50) representa el valor central, y el percentil 75 muestra que el 75% obtuvo ese puntaje o menos.</p>`);

  display(statsGrid([
    { title: "Percentil 25", value: e.p25 },
    { title: "Mediana", value: e.mediana },
    { title: "Percentil 75", value: e.p75 },
    { title: "En Top 10%", value: e.en_top10, subtitle: `${e.cantidad > 0 ? Math.round(e.en_top10 / e.cantidad * 100) : 0}%` }
  ]));

  const cercanas = escuelas
    .filter(x => x.comuna === e.comuna && x.rbd !== e.rbd)
    .slice(0, 10);

  if (cercanas.length > 0) {
    display(html`<h2 class="section-title">Comparación con otros establecimientos en ${e.comuna}</h2>`);

    const comparacion = [e, ...cercanas];
    display(html`
      <div class="grid grid-cols-2">
        <div class="card">
          <h3>Gráfico comparativo</h3>
          <figure>
            <div class="plot-container">
              ${resize((width) => Plot.plot({
                width,
                marginLeft: Math.min(180, width * 0.45),
                marginRight: 50,
                height: Math.max(280, comparacion.length * 28),
                style: {fontSize: "11px"},
                y: {label: null},
                x: {axis: null},
                marks: [
                  Plot.barX(comparacion, {
                    y: "establecimiento",
                    x: "prom_lect_mate",
                    fill: d => d.rbd === e.rbd ? "var(--datalized-teal)" : "#94a3b8",
                    sort: {y: "-x"},
                    tip: {
                      format: {
                        y: true,
                        x: d => d + " pts"
                      }
                    }
                  }),
                  Plot.text(comparacion, {
                    y: "establecimiento",
                    x: "prom_lect_mate",
                    text: d => d.prom_lect_mate,
                    dx: 5,
                    textAnchor: "start",
                    fontSize: 10,
                    fill: "currentColor"
                  })
                ]
              }))}
            </div>
            <figcaption>Barra verde = establecimiento actual</figcaption>
          </figure>
        </div>
        <div class="card">
          <h3>Tabla comparativa</h3>
          ${Inputs.table(comparacion.sort((a, b) => b.prom_lect_mate - a.prom_lect_mate), {
            columns: ["rank_comuna", "establecimiento", "dependencia", "prom_lect_mate"],
            header: {
              rank_comuna: "#",
              establecimiento: "Establecimiento",
              dependencia: "Dep.",
              prom_lect_mate: "Prom."
            },
            format: {
              rank_comuna: d => rankBadge(d),
              establecimiento: (d, i, data) => html`<a href="?rbd=${data[i].rbd}" style="color: var(--datalized-teal);">${d}</a>`,
              dependencia: d => depBadge(d)
            },
            layout: "auto",
            select: false,
            // badge increase row height
            rows: 11*2
          })}
        </div>
      </div>
    `);
  }

}
```

```js
import * as L from "npm:leaflet";
```

```js
// Sección de colegios cercanos geográficamente
if (escuelaPreseleccionada && escuelaPreseleccionada.lat && escuelaPreseleccionada.lon) {
  const e = escuelaPreseleccionada;

  // Función haversine para calcular distancia en km
  const haversine = (lat1, lon1, lat2, lon2) => {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  };

  // Encontrar los 10 colegios más cercanos
  const cercanos = escuelas
    .filter(x => x.rbd !== e.rbd && x.lat && x.lon)
    .map(x => ({...x, distancia: haversine(e.lat, e.lon, x.lat, x.lon)}))
    .sort((a, b) => a.distancia - b.distancia)
    .slice(0, 10);

  if (cercanos.length > 0) {
    // Crear el contenedor del mapa
    const mapContainer = document.createElement("div");
    mapContainer.style.cssText = "height: 350px; border-radius: 8px;";

    // Incluir colegio actual en la tabla con distancia 0
    const tablaData = [{...e, distancia: 0}, ...cercanos];

    // Crear la tabla
    const tabla = Inputs.table(tablaData, {
      columns: ["establecimiento", "dependencia", "prom_lect_mate", "distancia"],
      header: {
        establecimiento: "Establecimiento",
        dependencia: "Dep.",
        prom_lect_mate: "Prom.",
        distancia: "Dist."
      },
      format: {
        establecimiento: (d, i, data) => {
          const isActual = data[i].rbd === e.rbd;
          return html`<a href="?rbd=${data[i].rbd}" style="color: var(--datalized-teal); ${isActual ? 'font-weight: bold;' : ''}">${d}${isActual ? ' (actual)' : ''}</a>`;
        },
        dependencia: d => depBadge(d),
        distancia: d => d === 0 ? "-" : d.toFixed(1) + " km"
      },
      layout: "auto",
      select: false,
      rows: 11
    });

    // Renderizar todo el grid de una vez
    display(html`
      <h2 class="section-title">Colegios cercanos geográficamente</h2>
      <div class="grid grid-cols-2">
        <div class="card">
          <h3>Mapa de ubicación</h3>
          ${mapContainer}
          <figcaption style="margin-top: 0.5rem; font-size: 0.8rem;">🏫 actual · 🏠 cercanos</figcaption>
        </div>
        <div class="card">
          <h3>Colegios más cercanos</h3>
          ${tabla}
        </div>
      </div>
    `);

    // Inicializar el mapa después de que el contenedor esté en el DOM
    const map = L.map(mapContainer).setView([e.lat, e.lon], 14);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // Icono destacado para el colegio actual
    const iconoActual = L.divIcon({
      className: '',
      html: '<div style="background: var(--datalized-teal); width: 32px; height: 32px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; font-size: 16px;">🏫</div>',
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    // Icono para colegios cercanos
    const iconoCercano = L.divIcon({
      className: '',
      html: '<div style="background: #64748b; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; font-size: 12px;">🏠</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    // Marcador del colegio actual (destacado)
    L.marker([e.lat, e.lon], {icon: iconoActual}).addTo(map)
      .bindPopup(`<strong>${e.establecimiento}</strong><br>Prom: ${e.prom_lect_mate}`)
      .openPopup();

    // Marcadores de colegios cercanos
    cercanos.forEach(c => {
      L.marker([c.lat, c.lon], {icon: iconoCercano}).addTo(map)
        .bindPopup(`<strong>${c.establecimiento}</strong><br>Prom: ${c.prom_lect_mate}<br>${c.distancia.toFixed(1)} km`);
    });

    // Ajustar vista para mostrar todos los marcadores
    const bounds = L.latLngBounds([[e.lat, e.lon], ...cercanos.map(x => [x.lat, x.lon])]);
    map.fitBounds(bounds, {padding: [30, 30]});
  }
}
```

```js
// Si no hay escuela preseleccionada, mostrar el directorio
if (!escuelaPreseleccionada) {
  display(html`<h1>Directorio de Establecimientos</h1>`);
  display(html`<p>Busca cualquier establecimiento educacional y accede a su ficha detallada con desempeño en la PAES 2026. Haz clic en el nombre del establecimiento para ver promedios por prueba, distribución de puntajes y comparación comunal.</p>`);
}
```

<div class="filters">

```js
const busquedaTexto = escuelaPreseleccionada ? "" : view(Inputs.text({
  placeholder: "Escribe el nombre del establecimiento...",
  label: "Buscar"
}));

const regionSel = escuelaPreseleccionada ? null : view(Inputs.select(
  [null, ...filtros.regiones],
  {label: "Región", format: d => d ? d.nombre : "Todas"}
));

const depSel = escuelaPreseleccionada ? null : view(Inputs.select(
  [null, ...filtros.dependencias],
  {label: "Dependencia", format: d => d ? d.nombre : "Todas"}
));
```

</div>

```js
if (!escuelaPreseleccionada) {
  const hayFiltroActivo = busquedaTexto || regionSel || depSel;

  if (hayFiltroActivo) {
    const escuelasFiltradas = escuelas.filter(d => {
      const matchBusqueda = !busquedaTexto ||
        d.establecimiento.toLowerCase().includes(busquedaTexto.toLowerCase()) ||
        d.comuna?.toLowerCase().includes(busquedaTexto.toLowerCase());
      const matchRegion = !regionSel || d.cod_region === regionSel.codigo;
      const matchDependencia = !depSel || d.dependencia === depSel.nombre;
      return matchBusqueda && matchRegion && matchDependencia;
    }).sort((a, b) => a.establecimiento.localeCompare(b.establecimiento));

    display(html`<p style="color: var(--datalized-gray-light); margin-bottom: 1rem;">Mostrando <strong>${escuelasFiltradas.length.toLocaleString()}</strong> establecimientos</p>`);

    display(Inputs.table(escuelasFiltradas, {
      columns: ["rbd", "establecimiento", "dependencia", "comuna", "region"],
      header: {
        rbd: "RBD",
        establecimiento: "Establecimiento",
        dependencia: "Dep.",
        comuna: "Comuna",
        region: "Región"
      },
      format: {
        establecimiento: (d, i, data) => html`<a href="?rbd=${data[i].rbd}" class="school-name" style="text-decoration: none; color: var(--datalized-teal);">${d}</a>`,
        dependencia: d => depBadge(d)
      },
      layout: "auto",
      rows: 20,
      select: false
    }));
  } else {
    display(html`<p style="color: var(--datalized-gray-light); margin-top: 1rem;">Usa los filtros para buscar un establecimiento.</p>`);
  }
}
```
