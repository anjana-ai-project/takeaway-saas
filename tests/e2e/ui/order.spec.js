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

async function completeUpiPayment(page, { simulateFailure = false } = {}) {
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="upi"]').check();
  await page.waitForSelector('#upi-id', { timeout: 5000 });
  await page.locator('#upi-id').fill('test@upi');
  await page.locator('button:has-text("Proceed to Pay")').click();
  await page.waitForSelector('#pay-btn', { timeout: 5000 });
  if (simulateFailure) await page.locator('#simulate-failure').check();
  await page.locator('#pay-btn').click();
  await page.waitForSelector('#result-title', { timeout: 15000 });
}

async function completeCardPayment(page, { simulateFailure = false } = {}) {
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="card"]').check();
  await page.waitForSelector('#card-number', { timeout: 5000 });
  await page.locator('#card-number').fill('1234567890123456');
  await page.locator('#card-expiry').fill('12/26');
  await page.locator('#card-cvv').fill('123');
  await page.locator('button:has-text("Proceed to Pay")').click();
  await page.waitForSelector('#pay-btn', { timeout: 5000 });
  if (simulateFailure) await page.locator('#simulate-failure').check();
  await page.locator('#pay-btn').click();
  await page.waitForSelector('#result-title', { timeout: 15000 });
}

// UI024
test('UPI happy path payment success message shown', async ({ page }) => {
  // ARRANGE + ACT
  await completeUpiPayment(page);

  // ASSERT
  const actual = (await page.locator('#result-title').textContent()).trim();
  console.log(`[UI024] Checking: Result title after UPI payment | Expected: "Payment Successful!" | Actual: "${actual}"`);
  expect(actual, `Expected: "Payment Successful!" | Actual: "${actual}"`).toBe('Payment Successful!');
});

// UI025
test('UPI happy path order ID visible and non-empty', async ({ page }) => {
  // ARRANGE + ACT
  await completeUpiPayment(page);

  // ASSERT
  await page.waitForSelector('#result-order-id:not(.hidden)', { timeout: 5000 });
  const actual = (await page.locator('#result-order-id').textContent()).trim();
  console.log(`[UI025] Checking: Order ID non-empty after UPI payment | Expected: non-empty string | Actual: "${actual}"`);
  expect(actual.length, `Expected: length > 0 | Actual: "${actual}"`).toBeGreaterThan(0);
});

// UI026
test('UPI happy path AI summary appears after payment', async ({ page }) => {
  // ARRANGE + ACT
  await completeUpiPayment(page);

  // ASSERT
  await page.waitForFunction(
    () => {
      const el = document.getElementById('ai-summary');
      return el && el.textContent.trim().length > 0 && !el.textContent.includes('Generating');
    },
    { timeout: 20000 }
  );
  const actual = (await page.locator('#ai-summary').textContent()).trim();
  console.log(`[UI026] Checking: AI summary non-empty after UPI payment | Expected: length > 0 | Actual length: ${actual.length}`);
  expect(actual.length, `Expected: length > 0 | Actual: "${actual}"`).toBeGreaterThan(0);
});

// UI027
test('UPI happy path Try Again button NOT visible on success', async ({ page }) => {
  // ARRANGE + ACT
  await completeUpiPayment(page);

  // ASSERT
  const actual = await page.locator('#try-again-btn').isVisible();
  console.log(`[UI027] Checking: Try Again button visible on UPI success | Expected: false | Actual: ${actual}`);
  expect(actual, `Expected: false | Actual: ${actual}`).toBe(false);
});

// UI028
test('Card with simulate failure shows failure message', async ({ page }) => {
  // ARRANGE + ACT
  await completeCardPayment(page, { simulateFailure: true });

  // ASSERT
  const actual = (await page.locator('#result-title').textContent()).trim();
  console.log(`[UI028] Checking: Result title on simulated card failure | Expected: "Payment Failed" | Actual: "${actual}"`);
  expect(actual, `Expected: "Payment Failed" | Actual: "${actual}"`).toBe('Payment Failed');
});

// UI029
test('Card simulate failure Try Again button visible', async ({ page }) => {
  // ARRANGE + ACT
  await completeCardPayment(page, { simulateFailure: true });

  // ASSERT
  await page.waitForSelector('#try-again-btn:not(.hidden)', { timeout: 5000 });
  const actual = await page.locator('#try-again-btn').isVisible();
  console.log(`[UI029] Checking: Try Again button visible on payment failure | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI030
test('Try Again button returns user to payment screen', async ({ page }) => {
  // ARRANGE
  await completeCardPayment(page, { simulateFailure: true });
  await page.waitForSelector('#try-again-btn:not(.hidden)', { timeout: 5000 });

  // ACT
  await page.locator('#try-again-btn').click();

  // ASSERT
  const actual = await page.locator('#section-payment-method').isVisible();
  console.log(`[UI030] Checking: Payment method section visible after Try Again | Expected: true | Actual: ${actual}`);
  expect(actual, `Expected: true | Actual: ${actual}`).toBe(true);
});

// UI031
test('Cash on delivery success message mentions delivery', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="cod"]').check();
  await page.locator('button:has-text("Proceed to Pay")').click();
  await page.waitForSelector('#pay-btn', { timeout: 5000 });

  // ACT
  await page.locator('#pay-btn').click();
  await page.waitForSelector('#result-title', { timeout: 15000 });

  // ASSERT
  const actual = (await page.locator('#result-msg').textContent()).toLowerCase();
  const containsDelivery = actual.includes('delivery');
  console.log(`[UI031] Checking: COD success message contains "delivery" | Expected: true | Actual: ${containsDelivery} (message="${actual}")`);
  expect(containsDelivery, `Expected: true | Actual: ${containsDelivery} (message="${actual}")`).toBe(true);
});

// UI032
test('Cash on delivery does not show Payment Successful', async ({ page }) => {
  // ARRANGE
  await reachPaymentMethod(page);
  await page.locator('input[name="payment-method"][value="cod"]').check();
  await page.locator('button:has-text("Proceed to Pay")').click();
  await page.waitForSelector('#pay-btn', { timeout: 5000 });

  // ACT
  await page.locator('#pay-btn').click();
  await page.waitForSelector('#result-title', { timeout: 15000 });

  // ASSERT
  const actual = (await page.locator('#result-title').textContent()).trim();
  const containsPaymentSuccessful = actual.includes('Payment Successful');
  console.log(`[UI032] Checking: COD result title does NOT say "Payment Successful" | Expected: false | Actual: ${containsPaymentSuccessful} (title="${actual}")`);
  expect(containsPaymentSuccessful, `Expected: false | Actual: ${containsPaymentSuccessful} (title="${actual}")`).toBe(false);
});

// UI033
test('Clicking logo resets app to home with empty cart', async ({ page }) => {
  // ARRANGE
  await page.goto(PAGE);
  await page.waitForSelector('.menu-item', { timeout: 10000 });
  await page.locator('.add-btn').first().click();
  await page.waitForTimeout(900);
  await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  await page.locator('#view-cart-btn').click();

  // ACT
  await page.locator('header h1').click();

  // ASSERT
  const menuVisible = await page.locator('#section-menu').isVisible();
  const actual = (await page.locator('#cart-count').textContent()).trim();
  console.log(`[UI033] Checking: Menu visible after logo click | Expected: true | Actual: ${menuVisible}`);
  expect(menuVisible, `Expected: true | Actual: ${menuVisible}`).toBe(true);
  console.log(`[UI033] Checking: Cart count reset after logo click | Expected: "0" | Actual: "${actual}"`);
  expect(actual, `Expected: "0" | Actual: "${actual}"`).toBe('0');
});

// UI034
test('Order ID has valid format after successful payment', async ({ page }) => {
  // ARRANGE + ACT
  await completeUpiPayment(page);

  // ASSERT
  await page.waitForSelector('#result-order-id:not(.hidden)', { timeout: 5000 });
  const actual = (await page.locator('#result-order-id').textContent()).trim();
  console.log(`[UI034] Checking: Order ID length > 5 after successful payment | Expected: length > 5 | Actual length: ${actual.length} (id="${actual}")`);
  expect(actual.length, `Expected: length > 5 | Actual: "${actual}"`).toBeGreaterThan(5);
});
