# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: payment.spec.js >> UPI selected shows UPI input field
- Location: tests\e2e\ui\payment.spec.js:28:1

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
  27  | // UI014
  28  | test('UPI selected shows UPI input field', async ({ page }) => {
  29  |   // ARRANGE
  30  |   await reachPaymentMethod(page);
  31  | 
  32  |   // ACT
  33  |   await page.locator('input[name="payment-method"][value="upi"]').check();
  34  | 
  35  |   // ASSERT
  36  |   await expect(page.locator('#upi-id'), 'UPI input field should appear when UPI selected').toBeVisible();
  37  | });
  38  | 
  39  | // UI015
  40  | test('Invalid UPI ID without @ shows validation error', async ({ page }) => {
  41  |   // ARRANGE
  42  |   await reachPaymentMethod(page);
  43  |   await page.locator('input[name="payment-method"][value="upi"]').check();
  44  | 
  45  |   // ACT
  46  |   await page.locator('#upi-id').fill('testupi');
  47  |   await page.locator('button:has-text("Proceed to Pay")').click();
  48  | 
  49  |   // ASSERT
  50  |   await expect(page.locator('#err-upi'), 'Validation error should appear for UPI ID without @ symbol').toBeVisible();
  51  | });
  52  | 
  53  | // UI016
  54  | test('Valid UPI ID passes validation and proceeds', async ({ page }) => {
  55  |   // ARRANGE
  56  |   await reachPaymentMethod(page);
  57  |   await page.locator('input[name="payment-method"][value="upi"]').check();
  58  | 
  59  |   // ACT
  60  |   await page.locator('#upi-id').fill('test@upi');
  61  |   await page.locator('button:has-text("Proceed to Pay")').click();
  62  | 
  63  |   // ASSERT
  64  |   await expect(page.locator('#section-payment'), 'Valid UPI ID should pass validation and proceed').toBeVisible();
  65  | });
  66  | 
  67  | // UI017
  68  | test('Card selected shows all card input fields', async ({ page }) => {
  69  |   // ARRANGE
  70  |   await reachPaymentMethod(page);
  71  | 
  72  |   // ACT
  73  |   await page.locator('input[name="payment-method"][value="card"]').check();
  74  |   await page.waitForSelector('#card-number', { timeout: 5000 });
  75  | 
  76  |   // ASSERT
  77  |   await expect(page.locator('#card-number'), 'All card fields should appear when card selected').toBeVisible();
  78  |   await expect(page.locator('#card-expiry'), 'All card fields should appear when card selected').toBeVisible();
  79  |   await expect(page.locator('#card-cvv'), 'All card fields should appear when card selected').toBeVisible();
  80  | });
  81  | 
  82  | // UI018
  83  | test('Card number less than 16 digits shows error', async ({ page }) => {
  84  |   // ARRANGE
  85  |   await reachPaymentMethod(page);
  86  |   await page.locator('input[name="payment-method"][value="card"]').check();
  87  |   await page.waitForSelector('#card-number', { timeout: 5000 });
  88  | 
  89  |   // ACT
  90  |   await page.locator('#card-number').fill('1234');
  91  |   await page.locator('#card-expiry').fill('12/26');
  92  |   await page.locator('#card-cvv').fill('123');
  93  |   await page.locator('button:has-text("Proceed to Pay")').click();
  94  | 
  95  |   // ASSERT
  96  |   await expect(page.locator('#err-card-number'), 'Validation error should appear for card number less than 16 digits').toBeVisible();
  97  | });
  98  | 
  99  | // UI019
  100 | test('Invalid expiry format shows validation error', async ({ page }) => {
  101 |   // ARRANGE
  102 |   await reachPaymentMethod(page);
  103 |   await page.locator('input[name="payment-method"][value="card"]').check();
  104 |   await page.waitForSelector('#card-number', { timeout: 5000 });
  105 | 
  106 |   // ACT
  107 |   await page.locator('#card-number').fill('1234567890123456');
  108 |   await page.locator('#card-expiry').fill('13/99');
  109 |   await page.locator('#card-cvv').fill('123');
  110 |   await page.locator('button:has-text("Proceed to Pay")').click();
  111 | 
```