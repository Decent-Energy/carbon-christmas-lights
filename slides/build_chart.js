// Renders the UK electricity unit-rate history as a slide background (1600x900).
const { chromium } = require('playwright');
const fs = require('fs');

// [period start (decimal year), p/kWh]. 2016-18: approx. DESNZ annual averages.
// 2019+: Ofgem price cap, GB average, Direct Debit (Energy Price Guarantee rate Oct 2022-Jun 2023).
const D = [
  [2016.83, 14.4], [2017.0, 15.3], [2018.0, 16.2],
  [2019.0, 16.52], [2019.25, 18.56], [2019.75, 17.85], [2020.25, 17.81], [2020.75, 17.19],
  [2021.25, 18.95], [2021.75, 20.80], [2022.25, 28.34], [2022.75, 34.04], [2023.25, 33.21],
  [2023.5, 30.11], [2023.75, 27.35], [2024.0, 28.62], [2024.25, 24.50], [2024.5, 22.36],
  [2024.75, 24.50], [2025.0, 24.86], [2025.25, 27.03], [2025.5, 25.73], [2025.75, 26.35],
  [2026.0, 27.69], [2026.25, 24.67], [2026.5, 26.11], [2026.75, 26.32],
];
const END = 2027.0, W = 1600, H = 900, X0 = 2016.83;
const TOP = 640, MAXV = 34.04;               // peak sits at y=TOP, zero at the bottom edge
const x = t => ((t - X0) / (END - X0)) * W;
const y = v => H - (v / MAXV) * (H - TOP);

let line = '';
D.forEach(([t, v], i) => {
  const t2 = i < D.length - 1 ? D[i + 1][0] : END;
  line += `${i ? 'L' : 'M'}${x(t).toFixed(1)},${y(v).toFixed(1)} L${x(t2).toFixed(1)},${y(v).toFixed(1)} `;
});
const area = `${line} L${W},${H} L0,${H} Z`;
const years = [];
for (let yr = 2017; yr <= 2026; yr++)
  years.push(`<text x="${(x(yr) + 8).toFixed(1)}" y="${H - 18}" class="yr">${yr}</text>
  <line x1="${x(yr).toFixed(1)}" x2="${x(yr).toFixed(1)}" y1="${H - 40}" y2="${H}" class="tick"/>`);

const svg = bg => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
<style>
  .yr{font:600 17px Inter,Arial,sans-serif;fill:#8FA36A;letter-spacing:.5px}
  .tick{stroke:#C3CF9F;stroke-width:1.5}
</style>
${bg ? `<rect width="${W}" height="${H}" fill="#F3EFE8"/>` : ''}
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#A8C653" stop-opacity=".30"/>
  <stop offset="1" stop-color="#A8C653" stop-opacity=".10"/>
</linearGradient></defs>
<path d="${area}" fill="url(#g)"/>
<path d="${line}" fill="none" stroke="#A8C653" stroke-opacity=".75" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="${W - 22}" cy="${y(26.32).toFixed(1)}" r="9" fill="#F98D66" stroke="#F3EFE8" stroke-width="3"/>
${years.join('\n')}
</svg>`;

(async () => {
  fs.writeFileSync('energy-price-background.svg', svg(true));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
  for (const [name, bg] of [['energy-price-background.png', true], ['energy-price-background-transparent.png', false]]) {
    await p.setContent(`<body style="margin:0;background:transparent">${svg(bg)}</body>`);
    await p.screenshot({ path: name, omitBackground: !bg });
  }
  // preview: multiply the user's slide over the chart
  const slide = process.argv[2];
  if (slide) {
    const b64 = fs.readFileSync(slide).toString('base64');
    await p.setContent(`<body style="margin:0"><div style="position:relative;width:${W}px;height:${H}px">${svg(true)}
      <img src="data:image/png;base64,${b64}" style="position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:multiply"></div></body>`);
    await p.screenshot({ path: process.argv[3] });
  }
  await b.close();
})();
