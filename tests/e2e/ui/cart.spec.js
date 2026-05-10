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

async function gotoMenu(page) {
  await page.goto(PAGE);
  await page.waitForSelector('.menu-item', { timeout: 10000 });
}

async function addItemAndOpenCart(page, itemIndex = 0) {
  await page.locator('.add-btn').nth(itemIndex).click();
  await page.waitForTimeout(900);
  await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  await page.locator('#view-cart-btn').click();
  await page.waitForSelector('.cart-row', { timeout: 5000 });
}

// UI007
test('Empty cart View Cart button not visible', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);

  // ACT
  const actual = await page.locator('#view-cart-btn').isVisible();

  // ASSERT
  console.log(`[UI007] Checking: View Cart button visible with empty cart | Expected: false | Actual: ${actual}`);
  expect(actual, `Expected: false | Actual: ${actual}`).toBe(false);
});

// UI008
test('Cart shows correct item name and price', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);
  const expectedName = (await page.locator('.menu-item').first().locator('.menu-item-name').textContent()).trim();
  const expectedPrice = (await page.locator('.menu-item').first().locator('.menu-item-price').textContent()).trim();

  // ACT
  await addItemAndOpenCart(page, 0);
  const actualName = (await page.locator('.cart-row-name').first().textContent()).trim();
  const actualPrice = (await page.locator('.cart-row-price').first().textContent()).trim();

  // ASSERT
  console.log(`[UI008] Checking: Cart item name | Expected: "${expectedName}" | Actual: "${actualName}"`);
  expect(actualName, `Expected: "${expectedName}" | Actual: "${actualName}"`).toBe(expectedName);

  console.log(`[UI008] Checking: Cart item price | Expected: "${expectedPrice}" | Actual: "${actualPrice}"`);
  expect(actualPrice, `Expected: "${expectedPrice}" | Actual: "${actualPrice}"`).toBe(expectedPrice);
});

// UI009
test('Cart total is sum of all items', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);
  const price1 = parseInt((await page.locator('.menu-item').nth(0).locator('.menu-item-price').textContent()).replace(/[^\d]/g, ''));
  const price2 = parseInt((await page.locator('.menu-item').nth(3).locator('.menu-item-price').textContent()).replace(/[^\d]/g, ''));
  const expectedTotal = price1 + price2;

  // ACT
  await page.locator('.add-btn').nth(0).click();
  await page.waitForTimeout(900);
  await page.locator('.add-btn').nth(3).click();
  await page.waitForTimeout(900);
  await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  await page.locator('#view-cart-btn').click();
  await page.waitForSelector('.cart-row', { timeout: 5000 });
  const actualTotal = parseInt((await page.locator('#cart-total').textContent()).replace(/[^\d]/g, ''));

  // ASSERT
  console.log(`[UI009] Checking: Cart total | Expected: ${expectedTotal} | Actual: ${actualTotal}`);
  expect(actualTotal, `Expected: ${expectedTotal} | Actual: ${actualTotal}`).toBe(expectedTotal);
});

// UI010
test('Increasing quantity updates total correctly', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);
  const unitPrice = parseInt((await page.locator('.menu-item').first().locator('.menu-item-price').textContent()).replace(/[^\d]/g, ''));
  const expectedTotal = unitPrice * 2;

  // ACT
  await addItemAndOpenCart(page, 0);
  await page.locator('.qty-btn:has-text("+")').first().click();
  await page.waitForTimeout(400);
  const actualTotal = parseInt((await page.locator('#cart-total').textContent()).replace(/[^\d]/g, ''));

  // ASSERT
  console.log(`[UI010] Checking: Total after qty increase | Expected: ${expectedTotal} (${unitPrice}×2) | Actual: ${actualTotal}`);
  expect(actualTotal, `Expected: ${expectedTotal} | Actual: ${actualTotal}`).toBe(expectedTotal);
});

// UI011
test('Decreasing quantity to zero removes item', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);
  await addItemAndOpenCart(page, 0);

  // ACT
  await page.locator('.qty-btn:has-text("−")').first().click();
  await page.waitForTimeout(400);
  const actualCount = (await page.locator('#cart-count').textContent()).trim();
  const actualRows = await page.locator('.cart-row').count();

  // ASSERT
  console.log(`[UI011] Checking: Cart count after removing item | Expected: "0" | Actual: "${actualCount}"`);
  expect(actualCount, `Expected: "0" | Actual: "${actualCount}"`).toBe('0');

  console.log(`[UI011] Checking: Cart rows after removing item | Expected: 0 | Actual: ${actualRows}`);
  expect(actualRows, `Expected: 0 | Actual: ${actualRows}`).toBe(0);
});

// UI012
test('Multiple items show correct combined total', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);
  let expectedTotal = 0;
  for (let i = 0; i < 3; i++) {
    expectedTotal += parseInt((await page.locator('.menu-item').nth(i).locator('.menu-item-price').textContent()).replace(/[^\d]/g, ''));
  }

  // ACT
  for (let i = 0; i < 3; i++) {
    await page.locator('.add-btn').nth(i).click();
    await page.waitForTimeout(900);
  }
  await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  await page.locator('#view-cart-btn').click();
  await page.waitForSelector('.cart-row', { timeout: 5000 });
  const actualRows = await page.locator('.cart-row').count();
  const actualTotal = parseInt((await page.locator('#cart-total').textContent()).replace(/[^\d]/g, ''));

  // ASSERT
  console.log(`[UI012] Checking: Cart row count | Expected: 3 | Actual: ${actualRows}`);
  expect(actualRows, `Expected: 3 | Actual: ${actualRows}`).toBe(3);

  console.log(`[UI012] Checking: Combined total | Expected: ${expectedTotal} | Actual: ${actualTotal}`);
  expect(actualTotal, `Expected: ${expectedTotal} | Actual: ${actualTotal}`).toBe(expectedTotal);
});

// UI013
test('Cart count in header matches items added', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);

  // ACT
  await page.locator('.add-btn').nth(0).click();
  await page.waitForTimeout(900);
  await page.locator('.add-btn').nth(1).click();
  await page.waitForTimeout(900);
  const actual = (await page.locator('#cart-count').textContent()).trim();

  // ASSERT
  console.log(`[UI013] Checking: Header cart count after adding 2 items | Expected: "2" | Actual: "${actual}"`);
  expect(actual, `Expected: "2" | Actual: "${actual}"`).toBe('2');
});
