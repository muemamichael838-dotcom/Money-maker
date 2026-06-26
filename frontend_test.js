const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Create a local test server to serve the static index.html
  const http = require('http');
  const server = http.createServer((req, res) => {
    let filePath = path.join(__dirname, 'money-maker-ui', req.url === '/' ? 'index.html' : req.url);
    if (fs.existsSync(filePath)) {
        res.writeHead(200);
        fs.createReadStream(filePath).pipe(res);
    } else {
        res.writeHead(404);
        res.end();
    }
  });

  server.listen(8888);

  try {
    await page.goto('http://localhost:8888');
    await page.waitForTimeout(2000); // Wait for animations
    await page.screenshot({ path: 'frontend_verification.png', fullPage: true });
    console.log('Screenshot saved to frontend_verification.png');

    const title = await page.title();
    console.log('Page title:', title);

    const text = await page.innerText('body');
    if (text.includes('Money Maker 🤑')) {
        console.log('Rebranding verification: PASSED');
    } else {
        console.log('Rebranding verification: FAILED');
    }
  } catch (e) {
    console.error('Test failed:', e);
  } finally {
    await browser.close();
    server.close();
  }
})();
