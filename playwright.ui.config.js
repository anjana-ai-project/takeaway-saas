const { defineConfig } = require('@playwright/test');

// UI-only config — no webServer block so tests fail for real if server is down.
module.exports = defineConfig({
  testDir: './tests/e2e/ui',
  timeout: 30000,
  retries: 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8000',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
