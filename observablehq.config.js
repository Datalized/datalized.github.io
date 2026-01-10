export default {
    root: "src",
    title: "Datalized Public",
    theme: ["light", "wide"],
    head: `<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700&display=swap" rel="stylesheet">`,
    pages: [
        {
            name: "PAES 2026",
            open: true,
            pages: [
                { name: "Exploración", path: "/paes-2026/" },
                { name: "Ranking", path: "/paes-2026/ranking" },
                { name: "Top 10", path: "/paes-2026/top" },
                { name: "Ficha colegios", path: "/paes-2026/ficha" },
                { name: "Metodología", path: "/paes-2026/metodologia" }
            ]
        }
    ],
    base: "/",
    pager: false,
    search: true,
    footer: `<div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; flex-wrap: wrap;">
      <span>Hecho con</span>
      <span style="color: #e25555; font-size: 1.1em;">♥</span>
      <span>por</span>
      <a href="https://datalized.cl" target="_blank" rel="noopener" style="display: inline-flex; align-items: center; gap: 0.3rem; text-decoration: none;">
        <img src="/logo-datalized.png" alt="Datalized" style="height: 20px; vertical-align: middle;">
      </a>
      <span style="color: var(--theme-foreground-muted); margin-left: 0.5rem;">· solving problems with data</span>
    </div>`
};
