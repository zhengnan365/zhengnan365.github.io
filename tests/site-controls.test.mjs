import test from 'node:test';
import assert from 'node:assert/strict';
import { copyCitation, nextLanguage, nextTheme, initializeSiteControls } from '../assets/js/site-controls.mjs';

test('language toggles between Chinese and English', () => {
  assert.equal(nextLanguage('zh'), 'en');
  assert.equal(nextLanguage('en'), 'zh');
});

test('theme toggles between light and dark', () => {
  assert.equal(nextTheme('light'), 'dark');
  assert.equal(nextTheme('dark'), 'light');
});

test('copyCitation uses the Clipboard API when available', async () => {
  let copied = '';
  await copyCitation('citation text', { writeText: async value => { copied = value; } });
  assert.equal(copied, 'citation text');
});

test('copyCitation falls back to the selection copy command', async () => {
  let selected = false;
  let removed = false;
  const area = { style: {}, setAttribute() {}, select() { selected = true; }, remove() { removed = true; } };
  const doc = {
    createElement() { return area; },
    body: { appendChild() {} },
    execCommand(command) { assert.equal(command, 'copy'); return true; },
  };
  await copyCitation('fallback text', null, doc);
  assert.equal(area.value, 'fallback text');
  assert.equal(selected, true);
  assert.equal(removed, true);
});

test('copyCitation retries with the selection command when Clipboard API rejects', async () => {
  let copied = false;
  const area = { style: {}, setAttribute() {}, select() {}, remove() {} };
  const doc = {
    createElement() { return area; },
    body: { appendChild() {} },
    execCommand(command) { assert.equal(command, 'copy'); copied = true; return true; },
  };
  await copyCitation('citation text', { writeText: async () => { throw new Error('Denied'); } }, doc);
  assert.equal(area.value, 'citation text');
  assert.equal(copied, true);
});

test('controls restore saved preferences and persist toggles', () => {
  const listeners = {};
  const language = { addEventListener(type, listener) { listeners.language = listener; }, replaceChildren(value) { this.label = value; }, setAttribute(name, value) { this[name] = value; } };
  const theme = { addEventListener(type, listener) { listeners.theme = listener; }, replaceChildren(value) { this.label = value; }, setAttribute(name, value) { this[name] = value; } };
  const root = { dataset: {} };
  const doc = {
    documentElement: root,
    querySelector(selector) { return selector === '[data-language-toggle]' ? language : theme; },
    querySelectorAll() { return []; },
  };
  const saved = new Map([['site-language', 'en'], ['site-theme', 'dark']]);
  const storage = { getItem: key => saved.get(key), setItem: (key, value) => saved.set(key, value) };
  initializeSiteControls(doc, storage);
  assert.deepEqual(root.dataset, { lang: 'en', theme: 'dark' });
  assert.equal(root.lang, 'en');
  assert.equal(language.label, '中');
  assert.match(theme.innerHTML, /fa-sun/);
  listeners.language();
  listeners.theme();
  assert.equal(saved.get('site-language'), 'zh');
  assert.equal(saved.get('site-theme'), 'light');
  assert.equal(root.lang, 'zh-CN');
  assert.match(theme.innerHTML, /fa-moon/);
});

test('controls initialize when the localStorage getter throws', () => {
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'localStorage');
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, get() { throw new Error('Storage blocked'); } });
  try {
    const root = { dataset: {} };
    const doc = { documentElement: root, querySelector() { return null; }, querySelectorAll() { return []; } };
    assert.doesNotThrow(() => initializeSiteControls(doc));
    assert.deepEqual(root.dataset, { lang: 'zh', theme: 'light' });
  } finally {
    if (previous) Object.defineProperty(globalThis, 'localStorage', previous);
    else delete globalThis.localStorage;
  }
});
