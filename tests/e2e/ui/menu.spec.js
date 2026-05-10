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

// UI001
test('Menu loads and displays 6 items', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);

  // ACT
  const actual = await page.locator('.menu-item').count();

  // ASSERT
  console.log(`[UI001] Checking: Menu item count | Expected: 6 | Actual: ${actual}`);
  expect(actual, `Expected: 6 | Actual: ${actual}`).toBe(6);
});

// UI002
test('Each item shows name category and price', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);
  const first = page.locator('.menu-item').first();

  // ACT
  const nameVisible = await first.locator('.menu-item-name').isVisible();
  const categoryVisible = await first.locator('.tag').isVisible();
  const priceText = await first.locator('.menu-item-price').textContent();

  // ASSERT
  console.log(`[UI002] Checking: Item name visible | Expected: true | Actual: ${nameVisible}`);
  expect(nameVisible, `Expected: true | Actual: ${nameVisible}`).toBe(true);

  console.log(`[UI002] Checking: Category visible | Expected: true | Actual: ${categoryVisible}`);
  expect(categoryVisible, `Expected: true | Actual: ${categoryVisible}`).toBe(true);

  const containsRupee = priceText.includes('₹');
  console.log(`[UI002] Checking: Price contains ₹ | Expected: true | Actual: ${containsRupee} (text="${priceText}")`);
  expect(containsRupee, `Expected: true | Actual: ${containsRupee}`).toBe(true);
});

// UI003
test('Add item updates cart count in header', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);

  // ACT
  await page.locator('.add-btn').first().click();
  await page.waitForTimeout(900);
  const actual = await page.locator('#cart-count').textContent();

  // ASSERT
  console.log(`[UI003] Checking: Cart count after adding 1 item | Expected: "1" | Actual: "${actual.trim()}"`);
  expect(actual.trim(), `Expected: "1" | Actual: "${actual.trim()}"`).toBe('1');
});

// UI004
test('Adding same item twice increases quantity not duplicate', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);

  // ACT
  await page.locator('.add-btn').first().click();
  await page.waitForTimeout(900);
  await page.locator('.add-btn').first().click();
  await page.waitForTimeout(900);
  await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  await page.locator('#view-cart-btn').click();
  const rows = await page.locator('.cart-row').count();
  const qty = await page.locator('.qty-num').first().textContent();

  // ASSERT
  console.log(`[UI004] Checking: Cart row count | Expected: 1 | Actual: ${rows}`);
  expect(rows, `Expected: 1 | Actual: ${rows}`).toBe(1);

  console.log(`[UI004] Checking: Item quantity | Expected: "2" | Actual: "${qty.trim()}"`);
  expect(qty.trim(), `Expected: "2" | Actual: "${qty.trim()}"`).toBe('2');
});

// UI005
test('Back to menu retains cart items', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);
  await page.locator('.add-btn').first().click();
  await page.waitForTimeout(900);
  await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  await page.locator('#view-cart-btn').click();

  // ACT
  await page.locator('text=← Back to Menu').click();
  const menuVisible = await page.locator('#section-menu').isVisible();
  const actual = await page.locator('#cart-count').textContent();

  // ASSERT
  console.log(`[UI005] Checking: Menu visible after back | Expected: true | Actual: ${menuVisible}`);
  expect(menuVisible, `Expected: true | Actual: ${menuVisible}`).toBe(true);

  console.log(`[UI005] Checking: Cart count retained | Expected: "1" | Actual: "${actual.trim()}"`);
  expect(actual.trim(), `Expected: "1" | Actual: "${actual.trim()}"`).toBe('1');
});

// UI006
test('All 3 categories visible on menu', async ({ page }) => {
  // ARRANGE
  await gotoMenu(page);

  // ACT
  const tags = await page.locator('.tag').allTextContents();
  const categories = new Set(tags.map(t => t.trim()));
  const hasBurgers = categories.has('Burgers');
  const hasDrinks = categories.has('Drinks');
  const hasSides = categories.has('Sides');

  // ASSERT
  console.log(`[UI006] Checking: Burgers category present | Expected: true | Actual: ${hasBurgers}`);
  expect(hasBurgers, `Expected: true | Actual: ${hasBurgers}`).toBe(true);

  console.log(`[UI006] Checking: Drinks category present | Expected: true | Actual: ${hasDrinks}`);
  expect(hasDrinks, `Expected: true | Actual: ${hasDrinks}`).toBe(true);

  console.log(`[UI006] Checking: Sides category present | Expected: true | Actual: ${hasSides}`);
  expect(hasSides, `Expected: true | Actual: ${hasSides}`).toBe(true);
});
