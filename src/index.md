---
title: Datalized Public
toc: false
---

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {
  --datalized-teal: #31B694;
  --datalized-teal-light: #52BE9D;
  --datalized-dark: #111827;
  --datalized-gray: #374151;
  --datalized-gray-light: #4B5563;
  --datalized-bg: #FAF9F5;
}

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 4rem 1rem;
  font-family: Raleway, "Raleway Fallback", sans-serif;
}

.hero .logo {
  width: 120px;
  height: auto;
  margin-bottom: 1.5rem;
}

.projects, .site-footer {
  font-family: Raleway, "Raleway Fallback", sans-serif;
}

.hero h1 {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, var(--datalized-teal) 0%, var(--datalized-teal-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero p {
  font-size: 1.25rem;
  color: var(--datalized-gray);
  max-width: 600px;
  margin-bottom: 2rem;
}

.projects {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.project-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s ease;
  text-decoration: none;
  color: inherit;
  display: block;
  background: white;
}

.project-card:hover {
  border-color: var(--datalized-teal);
  box-shadow: 0 4px 12px rgba(49, 182, 148, 0.15);
  transform: translateY(-2px);
}

.project-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  color: var(--datalized-dark);
}

.project-card p {
  margin: 0;
  color: var(--datalized-gray-light);
  font-size: 0.9rem;
}

.project-card .tag {
  display: inline-block;
  background: rgba(49, 182, 148, 0.1);
  color: var(--datalized-teal);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 1rem;
}

.project-card.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.project-card.disabled .tag {
  background: #f3f4f6;
  color: var(--datalized-gray-light);
}

.site-footer {
  text-align: center;
  padding: 2rem;
  color: var(--datalized-gray-light);
  font-size: 0.85rem;
}

.site-footer a {
  color: var(--datalized-teal);
  text-decoration: none;
}

.site-footer a:hover {
  text-decoration: underline;
}
</style>

<div class="hero">
  <img src="./logo-datalized.png" alt="Datalized" class="logo" />
  <h1>Datalized Public</h1>
  <p>Datos públicos de Chile, visualizados y analizados. Exploraciones interactivas de información oficial para entender mejor nuestro país.</p>
</div>

<div class="projects">
  <a href="./paes-2026/" class="project-card">
    <h3>PAES 2026</h3>
    <p>Resultados de la Prueba de Acceso a la Educación Superior. Rankings de establecimientos, análisis por dependencia y brechas educativas.</p>
    <span class="tag">306K postulantes</span>
  </a>

  <div class="project-card disabled">
    <h3>Próximamente</h3>
    <p>Más proyectos de datos públicos en desarrollo.</p>
    <span class="tag">En desarrollo</span>
  </div>
</div>

<div class="site-footer">
  <p>Un proyecto de <a href="https://datalized.cl">Datalized</a></p>
</div>
