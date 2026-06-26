const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');

(async () => {
  const server = http.createServer((req, res) => {
    let filePath = path.join(__dirname, 'money-maker-ui', req.url === '/' ? 'index.html' : req.url);
    if (fs.existsSync(filePath)) {
        const ext = path.extname(filePath);
        const mime = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css' }[ext] || 'text/plain';
        res.writeHead(200, { 'Content-Type': mime });
        fs.createReadStream(filePath).pipe(res);
    } else {
        res.writeHead(404);
        res.end();
    }
  });
  server.listen(9999);

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 } // Desktop
  });
  const page = await context.newPage();

  try {
    await page.goto('http://localhost:9999');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'desktop_view.png' });
    console.log('Desktop view verified.');

    // Mobile View
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'mobile_view.png' });
    console.log('Mobile view verified.');

    const onboardingVisible = await page.isVisible('#setup-overlay');
    console.log('Onboarding overlay detected:', onboardingVisible);

  } catch (e) {
    console.error(e);
  } finally {
    await browser.close();
    server.close();
  }
})();
