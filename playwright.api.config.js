const { defineConfig } = require('@playwright/test');

// API-only config — no webServer block so tests fail for real if server is down.
module.exports = defineConfig({
  testDir: './tests/e2e/api',
  timeout: 15000,
  retries: 0,
  reporter: [
    ['html', { outputFolder: 'reports/playwright-api-report', open: 'never' }],
    ['list'],
  ],
  use: {
    // Explicitly no baseURL so every test must use the full http://localhost:8000 URL.
  },
});
