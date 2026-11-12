// Payment reconciliation.
//
// Reads payments.jsonl and works out how much money we actually collected.
// Run:  node reconcile.js

const fs = require("fs");

function parseAmount(val) {
  if (typeof val === "number") return val;
  if (typeof val === "string") {
    return parseFloat(val.replace(/,/g, "").trim());
  }
  return Number(val);
}

const latestAttempts = new Map();

const lines = fs.readFileSync("payments.jsonl", "utf8").split("\n");
for (const line of lines) {
  const trimmed = line.trim();
  if (!trimmed) continue;

  let event;
  try {
    event = JSON.parse(trimmed);
  } catch (err) {
    // Ignore lines that can't be read
    continue;
  }

  // Ignore events without a txn_id
  if (!event || typeof event !== "object" || !event.txn_id) {
    continue;
  }

  const existing = latestAttempts.get(event.txn_id);
  if (!existing || (event.ts || "") > (existing.ts || "")) {
    latestAttempts.set(event.txn_id, event);
  }
}

let count = 0;
let total = 0;

for (const event of latestAttempts.values()) {
  if (event.status === "success") {
    count += 1;
    total += parseAmount(event.amount);
  }
}

const expected = parseInt(fs.readFileSync("expected.txt", "utf8").trim(), 10);

if (count !== expected) {
  console.log(`Check failed: counted ${count} successful payments, expected ${expected}.`);
  console.log("Something in the data isn't being handled the way the README describes.");
} else {
  console.log(`Check passed: ${count} successful payments.`);
  console.log(`Your code: KOYA-${Math.round(total)}`);
}
