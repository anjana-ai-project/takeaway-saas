# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: menu.spec.js >> Menu loads and displays 6 items
- Location: tests\e2e\ui\menu.spec.js:21:1

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
  15  | async function gotoMenu(page) {
  16  |   await page.goto(PAGE);
  17  |   await page.waitForSelector('.menu-item', { timeout: 10000 });
  18  | }
  19  | 
  20  | // UI001
  21  | test('Menu loads and displays 6 items', async ({ page }) => {
  22  |   // ARRANGE
  23  |   await gotoMenu(page);
  24  | 
  25  |   // ACT
  26  |   const count = await page.locator('.menu-item').count();
  27  | 
  28  |   // ASSERT
  29  |   expect(count, 'Menu should display exactly 6 items').toBe(6);
  30  | });
  31  | 
  32  | // UI002
  33  | test('Each item shows name category and price', async ({ page }) => {
  34  |   // ARRANGE
  35  |   await gotoMenu(page);
  36  |   const first = page.locator('.menu-item').first();
  37  | 
  38  |   // ACT
  39  |   const name = first.locator('.menu-item-name');
  40  |   const category = first.locator('.tag');
  41  |   const price = first.locator('.menu-item-price');
  42  | 
  43  |   // ASSERT
  44  |   await expect(name, 'Item name should all be visible').toBeVisible();
  45  |   await expect(category, 'Item category and price should all be visible').toBeVisible();
  46  |   const priceText = await price.textContent();
  47  |   expect(priceText, 'Item name, category and price should all be visible').toContain('₹');
  48  | });
  49  | 
  50  | // UI003
  51  | test('Add item updates cart count in header', async ({ page }) => {
  52  |   // ARRANGE
  53  |   await gotoMenu(page);
  54  | 
  55  |   // ACT
  56  |   await page.locator('.add-btn').first().click();
  57  |   await page.waitForTimeout(900);
  58  | 
  59  |   // ASSERT
  60  |   const actual = await page.locator('#cart-count').textContent();
  61  |   expect(actual.trim(), 'Cart count should update to 1 after adding item').toBe('1');
  62  | });
  63  | 
  64  | // UI004
  65  | test('Adding same item twice increases quantity not duplicate', async ({ page }) => {
  66  |   // ARRANGE
  67  |   await gotoMenu(page);
  68  | 
  69  |   // ACT
  70  |   await page.locator('.add-btn').first().click();
  71  |   await page.waitForTimeout(900);
  72  |   await page.locator('.add-btn').first().click();
  73  |   await page.waitForTimeout(900);
  74  |   await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  75  |   await page.locator('#view-cart-btn').click();
  76  | 
  77  |   // ASSERT
  78  |   const rows = await page.locator('.cart-row').count();
  79  |   expect(rows, 'Cart should show one row with quantity 2 not duplicates').toBe(1);
  80  |   const qty = await page.locator('.qty-num').first().textContent();
  81  |   expect(qty.trim(), 'Cart should show one row with quantity 2 not duplicates').toBe('2');
  82  | });
  83  | 
  84  | // UI005
  85  | test('Back to menu retains cart items', async ({ page }) => {
  86  |   // ARRANGE
  87  |   await gotoMenu(page);
  88  |   await page.locator('.add-btn').first().click();
  89  |   await page.waitForTimeout(900);
  90  |   await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  91  |   await page.locator('#view-cart-btn').click();
  92  | 
  93  |   // ACT
  94  |   await page.locator('text=← Back to Menu').click();
  95  | 
  96  |   // ASSERT
  97  |   await expect(page.locator('#section-menu'), 'Menu should be visible after back navigation').toBeVisible();
  98  |   const actual = await page.locator('#cart-count').textContent();
  99  |   expect(actual.trim(), 'Cart should retain items after back navigation').toBe('1');
  100 | });
  101 | 
  102 | // UI006
  103 | test('All 3 categories visible on menu', async ({ page }) => {
  104 |   // ARRANGE
  105 |   await gotoMenu(page);
  106 | 
  107 |   // ACT
  108 |   const tags = await page.locator('.tag').allTextContents();
  109 | 
  110 |   // ASSERT
  111 |   const categories = new Set(tags.map(t => t.trim()));
```