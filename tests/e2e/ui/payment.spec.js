const { test, expect } = require('@playwright/test');

const PAGE = '/frontend/index.html';

test.beforeAll(async ({ browser }) => {
  const page = await browser.newPage();
  try {
    await page.goto('http://localhost:8000/');
    await page.close();
  } catch (e) {
    throw new Error('Server not running at localhost:8000. Start server before running UI tests.');
  }
});

async function reachPaymentMethod(page) {
  await page.goto(PAGE);
  await page.waitForSelector('.menu-item', { timeout: 10000 });
  await page.locator('.add-btn').first().click();
  await page.waitForTimeout(900);
  await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  await page.locator('#view-cart-btn').click();
  await page.waitForSelector('#place-order-btn', { timeout: 5000 });
  await page.locator('#place-order-btn').click();
  await page.waitForSelector('input[name="payment-method"]', { timeout: 5000 });
}

// UI014
test('UPI selected shows UPI input field', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);

  // ACT
  await page.locator('input[name="payment-method"][value="upi"]').check();
  const actual = await page.locator('#upi-id').isVisible();

  // ASSERT
  console.log(`[UI014] Checking: UPI input visible after selecting UPI | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI015
test('Invalid UPI ID without @ shows validation error', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="upi"]').check();

  // ACT
  await page.locator('#upi-id').fill('testupi');
  await page.locator('button:has-text("Proceed to Pay")').click();
  const actual = await page.locator('#err-upi').isVisible();

  // ASSERT
  console.log(`[UI015] Checking: UPI error visible for input "testupi" (no @) | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI016
test('Valid UPI ID passes validation and proceeds', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="upi"]').check();

  // ACT
  await page.locator('#upi-id').fill('test@upi');
  await page.locator('button:has-text("Proceed to Pay")').click();
  const actual = await page.locator('#section-payment').isVisible();

  // ASSERT
  console.log(`[UI016] Checking: Payment section visible after valid UPI "test@upi" | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI017
test('Card selected shows all card input fields', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);

  // ACT
  await page.locator('input[name="payment-method"][value="card"]').check();
  await page.waitForSelector('#card-number', { timeout: 5000 });
  const cardNumVisible = await page.locator('#card-number').isVisible();
  const expiryVisible = await page.locator('#card-expiry').isVisible();
  const cvvVisible = await page.locator('#card-cvv').isVisible();

  // ASSERT
  console.log(`[UI017] Checking: Card number field visible | Expected: true | Actual: ${cardNumVisible}`);
  expect(cardNumVisible, `Expected: true | Actual: ${cardNumVisible}`).toBe(true);

  console.log(`[UI017] Checking: Expiry field visible | Expected: true | Actual: ${expiryVisible}`);
  expect(expiryVisible, `Expected: true | Actual: ${expiryVisible}`).toBe(true);

  console.log(`[UI017] Checking: CVV field visible | Expected: true | Actual: ${cvvVisible}`);
  expect(cvvVisible, `Expected: true | Actual: ${cvvVisible}`).toBe(true);
});

// UI018
test('Card number less than 16 digits shows error', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="card"]').check();
  await page.waitForSelector('#card-number', { timeout: 5000 });

  // ACT
  await page.locator('#card-number').fill('1234');
  await page.locator('#card-expiry').fill('12/26');
  await page.locator('#card-cvv').fill('123');
  await page.locator('button:has-text("Proceed to Pay")').click();
  const actual = await page.locator('#err-card-number').isVisible();

  // ASSERT
  console.log(`[UI018] Checking: Card number error visible for "1234" (<16 digits) | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI019
test('Invalid expiry format shows validation error', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="card"]').check();
  await page.waitForSelector('#card-number', { timeout: 5000 });

  // ACT
  await page.locator('#card-number').fill('1234567890123456');
  await page.locator('#card-expiry').fill('13/99');
  await page.locator('#card-cvv').fill('123');
  await page.locator('button:has-text("Proceed to Pay")').click();
  const actual = await page.locator('#err-card-expiry').isVisible();

  // ASSERT
  console.log(`[UI019] Checking: Expiry error visible for "13/99" (invalid month) | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI020
test('CVV less than 3 digits shows validation error', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="card"]').check();
  await page.waitForSelector('#card-number', { timeout: 5000 });

  // ACT
  await page.locator('#card-number').fill('1234567890123456');
  await page.locator('#card-expiry').fill('12/26');
  await page.locator('#card-cvv').fill('12');
  await page.locator('button:has-text("Proceed to Pay")').click();
  const actual = await page.locator('#err-card-cvv').isVisible();

  // ASSERT
  console.log(`[UI020] Checking: CVV error visible for "12" (<3 digits) | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI021
test('Cash on delivery shows no extra input fields', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);

  // ACT
  await page.locator('input[name="payment-method"][value="cod"]').check();
  const upiVisible = await page.locator('#upi-id').isVisible();
  const cardVisible = await page.locator('#card-number').isVisible();

  // ASSERT
  console.log(`[UI021] Checking: UPI field hidden for COD | Expected: false | Actual: ${upiVisible}`);
  expect(upiVisible, `Expected: false | Actual: ${upiVisible}`).toBe(false);

  console.log(`[UI021] Checking: Card field hidden for COD | Expected: false | Actual: ${cardVisible}`);
  expect(cardVisible, `Expected: false | Actual: ${cardVisible}`).toBe(false);
});

// UI022
test('Cash on delivery simulate failure checkbox hidden', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="cod"]').check();

  // ACT
  await page.locator('button:has-text("Proceed to Pay")').click();
  await page.waitForSelector('#section-payment.active', { timeout: 5000 });
  const actual = await page.locator('#simulate-failure').isVisible();

  // ASSERT
  console.log(`[UI022] Checking: Simulate failure checkbox hidden for COD | Expected: false | Actual: ${actual}`);
  expect(actual, `Expected: false | Actual: ${actual}`).toBe(false);
});

// UI023
test('Back button from payment method returns to cart', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);

  // ACT
  await page.locator('button:has-text("← Back to Cart")').click();
  const actual = await page.locator('#section-cart').isVisible();

  // ASSERT
  console.log(`[UI023] Checking: Cart section visible after back navigation | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});
