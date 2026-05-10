const { test, expect } = require('@playwright/test');

const PAGE = '/frontend/index.html';

// ── Shared setup: add one item and reach the payment-method screen ───────────

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

// ── Test 1: Happy path — UPI payment ─────────────────────────────────────────

test('happy path: UPI payment succeeds and shows order ID', async ({ page }) => {
  await reachPaymentMethod(page);

  // Select UPI and fill ID
  await page.locator('input[name="payment-method"][value="upi"]').check();
  await page.waitForSelector('#upi-id', { timeout: 5000 });
  await page.locator('#upi-id').fill('test@upi');
  await page.locator('button:has-text("Proceed to Pay")').click();

  // Ensure simulate failure is off, then pay
  await page.waitForSelector('#pay-btn', { timeout: 5000 });
  const simFailure = page.locator('#simulate-failure');
  if (await simFailure.isChecked()) await simFailure.uncheck();
  await page.locator('#pay-btn').click();

  // ── Assertions ──────────────────────────────────────────────────────────────

  await page.waitForSelector('#result-title', { timeout: 10000 });

  // Success heading — exact text
  const headingText = await page.locator('#result-title').innerText();
  expect(headingText, 'Success heading should say "Payment Successful!"')
    .toBe('Payment Successful!');

  // Order ID — must be present and non-empty
  await page.waitForSelector('#result-order-id:not(.hidden)', { timeout: 5000 });
  const orderIdText = await page.locator('#result-order-id').innerText();
  expect(orderIdText.trim(), 'Order ID element should not be empty')
    .not.toBe('');
  expect(orderIdText, 'Order ID text should contain the "Order reference:" label')
    .toContain('Order reference:');

  // AI summary div must exist in the DOM
  const aiSummaryCount = await page.locator('#ai-summary').count();
  expect(aiSummaryCount, 'AI summary div should be present in the DOM')
    .toBe(1);
});

// ── Test 2: Payment failure path — card ──────────────────────────────────────

test('failure path: simulated card failure shows declined message and Try Again', async ({ page }) => {
  await reachPaymentMethod(page);

  // Select card and fill valid details
  await page.locator('input[name="payment-method"][value="card"]').check();
  await page.waitForSelector('#card-number', { timeout: 5000 });
  await page.locator('#card-number').fill('1234567890123456');
  await page.locator('#card-expiry').fill('12/26');
  await page.locator('#card-cvv').fill('123');
  await page.locator('button:has-text("Proceed to Pay")').click();

  // Enable simulate failure, then pay
  await page.waitForSelector('#simulate-failure', { timeout: 5000 });
  await page.locator('#simulate-failure').check();
  await page.locator('#pay-btn').click();

  // ── Assertions ──────────────────────────────────────────────────────────────

  await page.waitForSelector('#result-title', { timeout: 10000 });

  // Failure message from #result-msg — server returns "Payment declined. Please try again."
  const failureMsg = await page.locator('#result-msg').innerText();
  expect(failureMsg, 'Failure message should contain "declined"')
    .toContain('declined');

  // Try Again button text
  await page.waitForSelector('#try-again-btn:not(.hidden)', { timeout: 5000 });
  const tryAgainText = await page.locator('#try-again-btn').innerText();
  expect(tryAgainText.trim(), 'Try Again button should have correct label')
    .toBe('Try Again');
});

// ── Test 3: Empty cart ────────────────────────────────────────────────────────

test('empty cart: cart count is 0 and View Cart button is absent', async ({ page }) => {
  await page.goto(PAGE);
  await page.waitForSelector('.menu-item', { timeout: 10000 });

  // ── Assertions ──────────────────────────────────────────────────────────────

  // Cart count element shows "0"
  const cartCountText = await page.locator('#cart-count').innerText();
  expect(cartCountText.trim(), 'Cart count should be "0" on page load')
    .toBe('0');

  // View Cart button must not exist as a visible element (count = 0 visible)
  const viewCartCount = await page.locator('#view-cart-btn:not(.hidden)').count();
  expect(viewCartCount, 'View Cart button should not be visible with empty cart')
    .toBe(0);
});
