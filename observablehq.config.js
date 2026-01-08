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
                { name: "Ranking", path: "/paes-2026/" },
                { name: "El Top 10", path: "/paes-2026/top" },
                { name: "La Ficha", path: "/paes-2026/ficha" }
            ]
        }
    ],
    base: "/",
    pager: false,
    search: true,
    footer: "Un proyecto de Datalized"
};
