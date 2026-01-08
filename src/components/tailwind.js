// TailwindCSS via Twind
// Basado en https://observablehq.com/@saneef/tailwindcss

import { twind, cssom, observe } from "npm:@twind/core";
import presetAutoprefix from "npm:@twind/preset-autoprefix";
import presetTailwind from "npm:@twind/preset-tailwind";

export function initializeTWind({ invalidation } = {}) {
  const sheet = cssom(new CSSStyleSheet());
  const tw = twind(
    {
      presets: [presetAutoprefix(), presetTailwind()],
      hash: false
    },
    sheet
  );

  // Insertar el stylesheet en el documento
  document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet.target];

  // Limpiar cuando se invalida la celda
  if (invalidation) {
    invalidation.then(() => {
      document.adoptedStyleSheets = document.adoptedStyleSheets.filter(
        (s) => s !== sheet.target
      );
    });
  }

  return tw;
}
