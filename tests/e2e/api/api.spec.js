const { test, expect, request: playwrightRequest } = require('@playwright/test');

const BASE = 'http://localhost:8000';

test.beforeAll(async () => {
  try {
    const context = await playwrightRequest.newContext();
    const response = await context.get(`${BASE}/`);
    if (!response.ok()) {
      throw new Error('Server not running');
    }
    await context.dispose();
  } catch (e) {
    throw new Error('Server not running at localhost:8000. Start server before running API tests.');
  }
});

// API001
test('GET menu returns 200 status', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/menu`);
  const actual = response.status();

  // ASSERT
  console.log(`[API001] Checking: GET /menu status | Expected: 200 | Actual: ${actual}`);
  expect(actual, `Expected: 200 | Actual: ${actual}`).toBe(200);
});

// API002
test('GET menu returns exactly 6 items', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/menu`);
  const body = await response.json();
  const actual = body.length;

  // ASSERT
  console.log(`[API002] Checking: GET /menu item count | Expected: 6 | Actual: ${actual}`);
  expect(actual, `Expected: 6 | Actual: ${actual}`).toBe(6);
});

// API003
test('GET menu items have correct schema', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/menu`);
  const body = await response.json();

  // ASSERT
  for (const item of body) {
    const keys = Object.keys(item);
    const hasId = keys.includes('id');
    const hasName = keys.includes('name');
    const hasCategory = keys.includes('category');
    const hasPrice = keys.includes('price');
    console.log(`[API003] Checking: item id=${item.id} has id/name/category/price | Expected: true/true/true/true | Actual: ${hasId}/${hasName}/${hasCategory}/${hasPrice}`);
    expect(hasId, `Expected: true | Actual: ${hasId} (item id=${item.id} missing 'id')`).toBe(true);
    expect(hasName, `Expected: true | Actual: ${hasName} (item id=${item.id} missing 'name')`).toBe(true);
    expect(hasCategory, `Expected: true | Actual: ${hasCategory} (item id=${item.id} missing 'category')`).toBe(true);
    expect(hasPrice, `Expected: true | Actual: ${hasPrice} (item id=${item.id} missing 'price')`).toBe(true);
  }
});

// API004
test('GET menu all prices greater than zero', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/menu`);
  const body = await response.json();
  const allPositive = body.every(item => item.price > 0);

  // ASSERT
  console.log(`[API004] Checking: All menu prices > 0 | Expected: true | Actual: ${allPositive}`);
  expect(allPositive, `Expected: true | Actual: ${allPositive}`).toBe(true);
});

// API005
test('GET menu valid item ID returns 200', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/menu/1`);
  const actual = response.status();

  // ASSERT
  console.log(`[API005] Checking: GET /menu/1 status | Expected: 200 | Actual: ${actual}`);
  expect(actual, `Expected: 200 | Actual: ${actual}`).toBe(200);
});

// API006
test('GET menu valid item ID returns correct item', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/menu/1`);
  const body = await response.json();
  const actual = body.id;

  // ASSERT
  console.log(`[API006] Checking: GET /menu/1 returns item with id=1 | Expected: 1 | Actual: ${actual}`);
  expect(actual, `Expected: 1 | Actual: ${actual}`).toBe(1);
});

// API007
test('GET menu invalid item ID returns 404', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/menu/999`);
  const actual = response.status();

  // ASSERT
  console.log(`[API007] Checking: GET /menu/999 status | Expected: 404 | Actual: ${actual}`);
  expect(actual, `Expected: 404 | Actual: ${actual}`).toBe(404);
});

// API008
test('POST order with valid items returns 200', async ({ request }) => {
  // ARRANGE
  const payload = { items: [{ item_id: 1, quantity: 1 }] };

  // ACT
  const response = await request.post(`${BASE}/order`, { data: payload });
  const actual = response.status();

  // ASSERT
  console.log(`[API008] Checking: POST /order status with valid items | Expected: 200 | Actual: ${actual}`);
  expect(actual, `Expected: 200 | Actual: ${actual}`).toBe(200);
});

// API009
test('POST order response contains order_id field', async ({ request }) => {
  // ARRANGE
  const payload = { items: [{ item_id: 1, quantity: 1 }] };

  // ACT
  const response = await request.post(`${BASE}/order`, { data: payload });
  const body = await response.json();
  const actual = body.order_id ? body.order_id.trim() : '';

  // ASSERT
  console.log(`[API009] Checking: POST /order response has non-empty order_id | Expected: length > 0 | Actual: "${actual}"`);
  expect(actual.length, `Expected: length > 0 | Actual: "${actual}"`).toBeGreaterThan(0);
});

// API010
test('POST order response total is greater than zero', async ({ request }) => {
  // ARRANGE
  const payload = { items: [{ item_id: 1, quantity: 1 }] };

  // ACT
  const response = await request.post(`${BASE}/order`, { data: payload });
  const body = await response.json();
  const actual = body.total;

  // ASSERT
  console.log(`[API010] Checking: POST /order total > 0 | Expected: > 0 | Actual: ${actual}`);
  expect(actual, `Expected: > 0 | Actual: ${actual}`).toBeGreaterThan(0);
});

// API011
test('POST order new order status is pending', async ({ request }) => {
  // ARRANGE
  const payload = { items: [{ item_id: 1, quantity: 1 }] };

  // ACT
  const response = await request.post(`${BASE}/order`, { data: payload });
  const body = await response.json();
  const actual = body.status;

  // ASSERT
  console.log(`[API011] Checking: POST /order status field | Expected: "pending" | Actual: "${actual}"`);
  expect(actual, `Expected: "pending" | Actual: "${actual}"`).toBe('pending');
});

// API012
test('POST order with empty items returns 400', async ({ request }) => {
  // ARRANGE
  const payload = { items: [] };

  // ACT
  const response = await request.post(`${BASE}/order`, { data: payload });
  const actual = response.status();

  // ASSERT
  console.log(`[API012] Checking: POST /order with empty items | Expected: 400 | Actual: ${actual}`);
  expect(actual, `Expected: 400 | Actual: ${actual}`).toBe(400);
});

// API013
test('POST order with invalid item_id returns 400', async ({ request }) => {
  // ARRANGE
  const payload = { items: [{ item_id: 999, quantity: 1 }] };

  // ACT
  const response = await request.post(`${BASE}/order`, { data: payload });
  const actual = response.status();

  // ASSERT
  console.log(`[API013] Checking: POST /order with invalid item_id 999 | Expected: 400 | Actual: ${actual}`);
  expect(actual, `Expected: 400 | Actual: ${actual}`).toBe(400);
});

// API014
test('POST payment success returns 200 status', async ({ request }) => {
  // ARRANGE
  const payload = { order_id: 'test', amount: 199, simulate_failure: false };

  // ACT
  const response = await request.post(`${BASE}/payment`, { data: payload });
  const actual = response.status();

  // ASSERT
  console.log(`[API014] Checking: POST /payment success status | Expected: 200 | Actual: ${actual}`);
  expect(actual, `Expected: 200 | Actual: ${actual}`).toBe(200);
});

// API015
test('POST payment success status field equals success', async ({ request }) => {
  // ARRANGE
  const payload = { order_id: 'test', amount: 199, simulate_failure: false };

  // ACT
  const response = await request.post(`${BASE}/payment`, { data: payload });
  const body = await response.json();
  const actual = body.status;

  // ASSERT
  console.log(`[API015] Checking: POST /payment success body.status | Expected: "success" | Actual: "${actual}"`);
  expect(actual, `Expected: "success" | Actual: "${actual}"`).toBe('success');
});

// API016
test('POST payment success has order_id and amount_paid', async ({ request }) => {
  // ARRANGE
  const payload = { order_id: 'test', amount: 199, simulate_failure: false };

  // ACT
  const response = await request.post(`${BASE}/payment`, { data: payload });
  const body = await response.json();
  const actualOrderIdType = typeof body.order_id;
  const actualAmountPaid = body.amount_paid;

  // ASSERT
  console.log(`[API016] Checking: POST /payment has order_id type | Expected: "string" | Actual: "${actualOrderIdType}"`);
  expect(actualOrderIdType, `Expected: "string" | Actual: "${actualOrderIdType}"`).toBe('string');
  console.log(`[API016] Checking: POST /payment amount_paid | Expected: 199 | Actual: ${actualAmountPaid}`);
  expect(actualAmountPaid, `Expected: 199 | Actual: ${actualAmountPaid}`).toBe(199);
});

// API017
test('POST payment simulate failure returns failed status', async ({ request }) => {
  // ARRANGE
  const payload = { order_id: 'test', amount: 199, simulate_failure: true };

  // ACT
  const response = await request.post(`${BASE}/payment`, { data: payload });
  const body = await response.json();
  const actual = body.status;

  // ASSERT
  console.log(`[API017] Checking: POST /payment simulate_failure body.status | Expected: "failed" | Actual: "${actual}"`);
  expect(actual, `Expected: "failed" | Actual: "${actual}"`).toBe('failed');
});

// API018
test('POST payment simulate failure response has message', async ({ request }) => {
  // ARRANGE
  const payload = { order_id: 'test', amount: 199, simulate_failure: true };

  // ACT
  const response = await request.post(`${BASE}/payment`, { data: payload });
  const body = await response.json();
  const actual = body.message ? body.message.trim() : '';

  // ASSERT
  console.log(`[API018] Checking: POST /payment failure body.message non-empty | Expected: length > 0 | Actual: "${actual}"`);
  expect(actual.length, `Expected: length > 0 | Actual: "${actual}"`).toBeGreaterThan(0);
});

// API019
test('POST payment with amount zero returns failed status', async ({ request }) => {
  // ARRANGE
  const payload = { order_id: 'test', amount: 0, simulate_failure: false };

  // ACT
  const response = await request.post(`${BASE}/payment`, { data: payload });
  const body = await response.json();
  const actual = body.status;

  // ASSERT
  console.log(`[API019] Checking: POST /payment with amount=0 body.status | Expected: "failed" | Actual: "${actual}"`);
  expect(actual, `Expected: "failed" | Actual: "${actual}"`).toBe('failed');
});

// API020
test('GET summary with invalid order_id returns 404', async ({ request }) => {
  // ACT
  const response = await request.get(`${BASE}/summary/invalidid123`);
  const actual = response.status();

  // ASSERT
  console.log(`[API020] Checking: GET /summary/invalidid123 status | Expected: 404 | Actual: ${actual}`);
  expect(actual, `Expected: 404 | Actual: ${actual}`).toBe(404);
});
