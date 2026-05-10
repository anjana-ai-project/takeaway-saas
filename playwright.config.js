const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: 'http://localhost:8000',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'uvicorn app.main:app --host 0.0.0.0 --port 8000',
    url: 'http://localhost:8000/',
    reuseExistingServer: true,
    timeout: 15000,
  },
});
