// يحوّل study.html إلى PDF بمتصفح Chromium (يدعم MathML والكتابة من اليمين إلى اليسار)
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const html = path.resolve(process.argv[2]);
  const pdf = path.resolve(process.argv[3]);
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + html, { waitUntil: 'networkidle' });
  await p.pdf({ path: pdf, format: 'A4', printBackground: true,
    margin: { top: '18mm', bottom: '18mm', left: '16mm', right: '16mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:9px;width:100%;text-align:center"><span class=pageNumber></span></div>' });
  await b.close();
})();
