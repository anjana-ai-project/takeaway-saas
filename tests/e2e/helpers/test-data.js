const data = require('./test-data.json');

function createValidUPIPayment() { return { ...data.upi.valid }; }
function createInvalidUPIPayment() { return { ...data.upi.invalid }; }
function createValidCardPayment() { return { ...data.card.valid }; }
function createInvalidCardNumber() { return { ...data.card.invalidCardNumber }; }
function createInvalidCardExpiry() { return { ...data.card.invalidExpiry }; }
function createInvalidCardCVV() { return { ...data.card.invalidCVV }; }
function createValidOrder() { return { items: data.order.valid.items.map(i => ({ ...i })) }; }
function createMultiItemOrder() { return { items: data.order.multiItem.items.map(i => ({ ...i })) }; }
function createInvalidOrder() { return { items: data.order.invalid.items.map(i => ({ ...i })) }; }
function createEmptyOrder() { return { items: [] }; }
function createValidPayment() { return { ...data.payment.valid }; }
function createFailurePayment() { return { ...data.payment.failure }; }
function createZeroAmountPayment() { return { ...data.payment.zeroAmount }; }

module.exports = {
  createValidUPIPayment,
  createInvalidUPIPayment,
  createValidCardPayment,
  createInvalidCardNumber,
  createInvalidCardExpiry,
  createInvalidCardCVV,
  createValidOrder,
  createMultiItemOrder,
  createInvalidOrder,
  createEmptyOrder,
  createValidPayment,
  createFailurePayment,
  createZeroAmountPayment,
};
