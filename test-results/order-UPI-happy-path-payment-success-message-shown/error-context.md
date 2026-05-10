# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: order.spec.js >> UPI happy path payment success message shown
- Location: tests\e2e\ui\order.spec.js:54:1

# Error details

```
Error: Server not running at localhost:8000. Start server before running UI tests.
```

# Test source

```ts
  1   | const { test, expect } = require('@playwright/test');
  2   | 
  3   | const PAGE = '/frontend/index.html';
  4   | 
  5   | test.beforeAll(async ({ browser }) => {
  6   |   const page = await browser.newPage();
  7   |   try {
  8   |     await page.goto('http://localhost:8000/');
  9   |     await page.close();
  10  |   } catch (e) {
> 11  |     throw new Error('Server not running at localhost:8000. Start server before running UI tests.');
      |           ^ Error: Server not running at localhost:8000. Start server before running UI tests.
  12  |   }
  13  | });
  14  | 
  15  | async function reachPaymentMethod(page) {
  16  |   await page.goto(PAGE);
  17  |   await page.waitForSelector('.menu-item', { timeout: 10000 });
  18  |   await page.locator('.add-btn').first().click();
  19  |   await page.waitForTimeout(900);
  20  |   await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  21  |   await page.locator('#view-cart-btn').click();
  22  |   await page.waitForSelector('#place-order-btn', { timeout: 5000 });
  23  |   await page.locator('#place-order-btn').click();
  24  |   await page.waitForSelector('input[name="payment-method"]', { timeout: 5000 });
  25  | }
  26  | 
  27  | async function completeUpiPayment(page, { simulateFailure = false } = {}) {
  28  |   await reachPaymentMethod(page);
  29  |   await page.locator('input[name="payment-method"][value="upi"]').check();
  30  |   await page.waitForSelector('#upi-id', { timeout: 5000 });
  31  |   await page.locator('#upi-id').fill('test@upi');
  32  |   await page.locator('button:has-text("Proceed to Pay")').click();
  33  |   await page.waitForSelector('#pay-btn', { timeout: 5000 });
  34  |   if (simulateFailure) await page.locator('#simulate-failure').check();
  35  |   await page.locator('#pay-btn').click();
  36  |   await page.waitForSelector('#result-title', { timeout: 15000 });
  37  | }
  38  | 
  39  | async function completeCardPayment(page, { simulateFailure = false } = {}) {
  40  |   await reachPaymentMethod(page);
  41  |   await page.locator('input[name="payment-method"][value="card"]').check();
  42  |   await page.waitForSelector('#card-number', { timeout: 5000 });
  43  |   await page.locator('#card-number').fill('1234567890123456');
  44  |   await page.locator('#card-expiry').fill('12/26');
  45  |   await page.locator('#card-cvv').fill('123');
  46  |   await page.locator('button:has-text("Proceed to Pay")').click();
  47  |   await page.waitForSelector('#pay-btn', { timeout: 5000 });
  48  |   if (simulateFailure) await page.locator('#simulate-failure').check();
  49  |   await page.locator('#pay-btn').click();
  50  |   await page.waitForSelector('#result-title', { timeout: 15000 });
  51  | }
  52  | 
  53  | // UI024
  54  | test('UPI happy path payment success message shown', async ({ page }) => {
  55  |   // ARRANGE + ACT
  56  |   await completeUpiPayment(page);
  57  | 
  58  |   // ASSERT
  59  |   const actual = await page.locator('#result-title').textContent();
  60  |   expect(actual.trim(), 'Payment success message should appear after UPI payment').toBe('Payment Successful!');
  61  | });
  62  | 
  63  | // UI025
  64  | test('UPI happy path order ID visible and non-empty', async ({ page }) => {
  65  |   // ARRANGE + ACT
  66  |   await completeUpiPayment(page);
  67  | 
  68  |   // ASSERT
  69  |   await page.waitForSelector('#result-order-id:not(.hidden)', { timeout: 5000 });
  70  |   const actual = await page.locator('#result-order-id').textContent();
  71  |   expect(actual.trim(), 'Order ID should be visible and non-empty after successful payment').not.toBe('');
  72  | });
  73  | 
  74  | // UI026
  75  | test('UPI happy path AI summary appears after payment', async ({ page }) => {
  76  |   // ARRANGE + ACT
  77  |   await completeUpiPayment(page);
  78  | 
  79  |   // ASSERT
  80  |   await page.waitForFunction(
  81  |     () => {
  82  |       const el = document.getElementById('ai-summary');
  83  |       return el && el.textContent.trim().length > 0 && !el.textContent.includes('Generating');
  84  |     },
  85  |     { timeout: 20000 }
  86  |   );
  87  |   const actual = await page.locator('#ai-summary').textContent();
  88  |   expect(actual.trim().length, 'AI summary should appear after successful payment').toBeGreaterThan(0);
  89  | });
  90  | 
  91  | // UI027
  92  | test('UPI happy path Try Again button NOT visible on success', async ({ page }) => {
  93  |   // ARRANGE + ACT
  94  |   await completeUpiPayment(page);
  95  | 
  96  |   // ASSERT
  97  |   await expect(page.locator('#try-again-btn'), 'Try Again button should not appear on payment success screen').toBeHidden();
  98  | });
  99  | 
  100 | // UI028
  101 | test('Card with simulate failure shows failure message', async ({ page }) => {
  102 |   // ARRANGE + ACT
  103 |   await completeCardPayment(page, { simulateFailure: true });
  104 | 
  105 |   // ASSERT
  106 |   const actual = await page.locator('#result-title').textContent();
  107 |   expect(actual.trim(), 'Payment failure message should appear when simulate failure is checked').toBe('Payment Failed');
  108 | });
  109 | 
  110 | // UI029
  111 | test('Card simulate failure Try Again button visible', async ({ page }) => {
```