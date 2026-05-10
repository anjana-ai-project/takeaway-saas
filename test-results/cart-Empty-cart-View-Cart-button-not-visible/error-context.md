# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: cart.spec.js >> Empty cart View Cart button not visible
- Location: tests\e2e\ui\cart.spec.js:29:1

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
  20  | async function addItemAndOpenCart(page, itemIndex = 0) {
  21  |   await page.locator('.add-btn').nth(itemIndex).click();
  22  |   await page.waitForTimeout(900);
  23  |   await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  24  |   await page.locator('#view-cart-btn').click();
  25  |   await page.waitForSelector('.cart-row', { timeout: 5000 });
  26  | }
  27  | 
  28  | // UI007
  29  | test('Empty cart View Cart button not visible', async ({ page }) => {
  30  |   // ARRANGE
  31  |   await gotoMenu(page);
  32  | 
  33  |   // ACT — no items added
  34  | 
  35  |   // ASSERT
  36  |   await expect(page.locator('#view-cart-btn'), 'View Cart should not be visible when cart is empty').toBeHidden();
  37  | });
  38  | 
  39  | // UI008
  40  | test('Cart shows correct item name and price', async ({ page }) => {
  41  |   // ARRANGE
  42  |   await gotoMenu(page);
  43  |   const menuItems = page.locator('.menu-item');
  44  |   const expectedName = await menuItems.first().locator('.menu-item-name').textContent();
  45  |   const expectedPrice = await menuItems.first().locator('.menu-item-price').textContent();
  46  | 
  47  |   // ACT
  48  |   await addItemAndOpenCart(page, 0);
  49  | 
  50  |   // ASSERT
  51  |   const cartName = await page.locator('.cart-row-name').first().textContent();
  52  |   expect(cartName.trim(), 'Item name should appear correctly in cart').toBe(expectedName.trim());
  53  |   const cartPrice = await page.locator('.cart-row-price').first().textContent();
  54  |   expect(cartPrice.trim(), 'Item price should appear correctly in cart').toBe(expectedPrice.trim());
  55  | });
  56  | 
  57  | // UI009
  58  | test('Cart total is sum of all items', async ({ page }) => {
  59  |   // ARRANGE
  60  |   await gotoMenu(page);
  61  |   const menuItems = page.locator('.menu-item');
  62  |   const price1Text = await menuItems.nth(0).locator('.menu-item-price').textContent();
  63  |   const price2Text = await menuItems.nth(3).locator('.menu-item-price').textContent();
  64  |   const price1 = parseInt(price1Text.replace(/[^\d]/g, ''));
  65  |   const price2 = parseInt(price2Text.replace(/[^\d]/g, ''));
  66  |   const expectedTotal = price1 + price2;
  67  | 
  68  |   // ACT
  69  |   await page.locator('.add-btn').nth(0).click();
  70  |   await page.waitForTimeout(900);
  71  |   await page.locator('.add-btn').nth(3).click();
  72  |   await page.waitForTimeout(900);
  73  |   await page.waitForSelector('#view-cart-btn:not(.hidden)', { timeout: 5000 });
  74  |   await page.locator('#view-cart-btn').click();
  75  |   await page.waitForSelector('.cart-row', { timeout: 5000 });
  76  | 
  77  |   // ASSERT
  78  |   const totalText = await page.locator('#cart-total').textContent();
  79  |   const actualTotal = parseInt(totalText.replace(/[^\d]/g, ''));
  80  |   expect(actualTotal, 'Cart total should equal sum of all item prices').toBe(expectedTotal);
  81  | });
  82  | 
  83  | // UI010
  84  | test('Increasing quantity updates total correctly', async ({ page }) => {
  85  |   // ARRANGE
  86  |   await gotoMenu(page);
  87  |   const priceText = await page.locator('.menu-item').first().locator('.menu-item-price').textContent();
  88  |   const unitPrice = parseInt(priceText.replace(/[^\d]/g, ''));
  89  | 
  90  |   // ACT
  91  |   await addItemAndOpenCart(page, 0);
  92  |   await page.locator('.qty-btn:has-text("+")').first().click();
  93  |   await page.waitForTimeout(400);
  94  | 
  95  |   // ASSERT
  96  |   const totalText = await page.locator('#cart-total').textContent();
  97  |   const actualTotal = parseInt(totalText.replace(/[^\d]/g, ''));
  98  |   expect(actualTotal, 'Total should double when quantity increased to 2').toBe(unitPrice * 2);
  99  | });
  100 | 
  101 | // UI011
  102 | test('Decreasing quantity to zero removes item', async ({ page }) => {
  103 |   // ARRANGE
  104 |   await gotoMenu(page);
  105 |   await addItemAndOpenCart(page, 0);
  106 | 
  107 |   // ACT
  108 |   await page.locator('.qty-btn:has-text("−")').first().click();
  109 |   await page.waitForTimeout(400);
  110 | 
  111 |   // ASSERT
```