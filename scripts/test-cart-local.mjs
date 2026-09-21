#!/usr/bin/env node
/**
 * Smoke-test local cart mode without a browser.
 * Loads plasico-cart-adapter.js under a minimal window/document mock.
 */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const adapterPath = path.resolve(__dirname, '../plasico/plasico.bg/plasico-cart-adapter.js');
const source = fs.readFileSync(adapterPath, 'utf8');

class MemoryStorage {
  constructor() { this.map = new Map(); }
  getItem(k) { return this.map.has(k) ? this.map.get(k) : null; }
  setItem(k, v) { this.map.set(k, String(v)); }
  removeItem(k) { this.map.delete(k); }
}

function makeWindow(hostname) {
  const localStorage = new MemoryStorage();
  const listeners = {};
  const document = {
    listeners,
    dispatchEvent(ev) {
      (listeners[ev.type] || []).forEach((fn) => fn(ev));
      return true;
    },
    addEventListener(type, fn) {
      (listeners[type] || (listeners[type] = [])).push(fn);
    },
    querySelector() { return null; },
  };
  class CustomEvent {
    constructor(type, init) {
      this.type = type;
      this.detail = init && init.detail;
    }
  }
  const window = {
    location: { hostname, protocol: 'https:', href: `https://${hostname}/`, pathname: '/' },
    localStorage,
    document,
    CustomEvent,
    PlasicoCartConfig: { debug: false },
  };
  window.window = window;
  return { window, document, localStorage };
}

async function runCase(name, hostname, fn) {
  const { window, document } = makeWindow(hostname);
  const context = vm.createContext({
    window,
    document,
    localStorage: window.localStorage,
    console,
    URL,
    DOMParser: class {
      parseFromString() {
        return { getElementById() { return null; }, querySelector() { return null; }, body: {} };
      }
    },
    Object,
    Array,
    String,
    Number,
    Math,
    JSON,
    Promise,
    Error,
    encodeURIComponent,
    decodeURIComponent,
    isFinite,
    parseInt,
    parseFloat,
    setTimeout,
  });
  vm.runInContext(source, context);
  const adapter = context.window.PlasicoCartAdapter;
  if (!adapter) throw new Error(name + ': adapter missing');
  await fn(adapter, context.window);
  console.log('PASS', name);
}

await runCase('vercel local mode', 'plasico.vercel.app', async (adapter) => {
  if (!adapter.isLocal) throw new Error('expected isLocal on vercel host');
  await adapter.init();
  const cart = await adapter.add('6479', 2, {
    title: 'Logitech M185',
    price: 14.99,
    image: 'https://example.com/m.png',
    href: 'logitech-wireless-mouse-m185-blue-6479.html',
  });
  if (cart.quantity !== 2) throw new Error('qty want 2 got ' + cart.quantity);
  if (cart.items.length !== 1) throw new Error('want 1 line');
  if (Math.abs(cart.subtotal - 29.98) > 0.001) throw new Error('subtotal ' + cart.subtotal);
  const again = await adapter.add('6479', 1, { title: 'Logitech M185', price: 14.99 });
  if (again.quantity !== 3) throw new Error('merged qty want 3 got ' + again.quantity);
  const lineId = again.items[0].lineId;
  const updated = await adapter.updateItem(lineId, 1);
  if (updated.quantity !== 1) throw new Error('update qty');
  const cleared = await adapter.removeItem(lineId);
  if (!cleared.isEmpty) throw new Error('expected empty after remove');
});

await runCase('legacy array migration', 'localhost', async (adapter, win) => {
  win.localStorage.setItem(
    'plasico-hss2026-cart',
    JSON.stringify([{ id: '111', title: 'Old', price: 10, qty: 2, image: '', href: '' }])
  );
  await adapter.init();
  const cart = adapter.getCart();
  if (cart.quantity !== 2) throw new Error('migrated qty ' + cart.quantity);
  if (cart.items[0].productId !== '111') throw new Error('migrated id');
});

await runCase('live host stays remote-capable', 'plasico.bg', async (adapter) => {
  if (adapter.isLocal) throw new Error('plasico.bg should not force local up front');
});

await runCase('persist + reload paints items', 'localhost', async (adapter, win) => {
  await adapter.init();
  await adapter.add('6479', 1, {
    title: 'Logitech M185',
    price: 14.99,
    image: 'https://example.com/m.png',
    href: 'logitech-wireless-mouse-m185-blue-6479.html',
  });
  const raw = win.localStorage.getItem('plasico-hss2026-cart');
  const parsed = JSON.parse(raw);
  if (parsed.__source !== 'local-cart') throw new Error('expected local-cart source, got ' + parsed.__source);
  if (!Array.isArray(parsed.items) || parsed.items.length !== 1) throw new Error('cache items');

  // Simulate a fresh page (checkout/drawer boot): new adapter, same storage.
  const { window: win2 } = makeWindow('localhost');
  win2.localStorage.setItem('plasico-hss2026-cart', raw);
  const context2 = vm.createContext({
    window: win2,
    document: win2.document,
    localStorage: win2.localStorage,
    console,
    URL,
    DOMParser: class {
      parseFromString() {
        return { getElementById() { return null; }, querySelector() { return null; }, body: {} };
      }
    },
    Object,
    Array,
    String,
    Number,
    Math,
    JSON,
    Promise,
    Error,
    encodeURIComponent,
    decodeURIComponent,
    isFinite,
    parseInt,
    parseFloat,
    setTimeout,
  });
  vm.runInContext(source, context2);
  const adapter2 = context2.window.PlasicoCartAdapter;

  // Sync getCart before init must not be trusted — checkout used to paint this.
  if (!adapter2.getCart().isEmpty) throw new Error('pre-init should still be empty model');

  let sawItems = false;
  adapter2.subscribe((cart) => {
    if (cart.items.length === 1 && cart.items[0].title === 'Logitech M185') sawItems = true;
  });
  await adapter2.init();
  const cart = adapter2.getCart();
  if (cart.isEmpty) throw new Error('post-init cart empty');
  if (cart.items[0].productId !== '6479') throw new Error('productId');
  if (Math.abs(cart.items[0].lineTotal - 14.99) > 0.001) throw new Error('lineTotal');
  if (!sawItems) throw new Error('subscribe never saw items');
});

await runCase('refresh after add keeps lines', 'plasico.vercel.app', async (adapter) => {
  await adapter.init();
  await adapter.add('111', 2, { title: 'Item', price: 5 });
  const afterRefresh = await adapter.refresh();
  if (afterRefresh.isEmpty || afterRefresh.quantity !== 2) {
    throw new Error('refresh wiped local cart');
  }
});

console.log('All cart local-mode smoke tests passed.');
