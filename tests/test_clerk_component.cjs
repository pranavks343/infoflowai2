const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('frontend/clerk_component.js', 'utf8').replace('export default function', 'componentFactory = function');
const tick = () => new Promise(resolve => setImmediate(resolve));

async function setup({ authenticated = false, token, signOutError, signedOut = false } = {}) {
  const element = () => ({ hidden: false, style: {}, children: [], appendChild(child) { this.children.push(child); }, replaceChildren() { this.children = []; } });
  const nodes = Object.fromEntries(['status', 'controls', 'signin', 'signup', 'user'].map(name => [`.clerk-${name}`, element()]));
  const states = [];
  const redirects = [];
  let listener;
  let signOutCalls = 0;
  const clerk = {
    session: signedOut ? null : { id: 'session', getToken: async () => token || 'jwt' }, user: { fullName: 'Test User' },
    addListener(fn) { listener = fn; return () => {}; },
    mountUserButton() {}, unmountUserButton() {}, mountSignIn() {}, unmountSignIn() {}, mountSignUp() {}, unmountSignUp() {},
    async signOut() { signOutCalls++; if (signOutError) throw Error('offline'); this.session = null; listener(); },
  };
  const window = { infoflowClerkPromise: Promise.resolve(clerk) };
  const context = vm.createContext({ window, document: { createElement: element }, location: { origin: 'https://example.test', replace: url => redirects.push(url) }, atob: input => Buffer.from(input, 'base64').toString(), setInterval: () => 1, clearInterval() {} });
  vm.runInContext(source, context);
  const cleanup = context.componentFactory({ parentElement: { querySelector: selector => nodes[selector] }, data: { publishableKey: 'pk_test_' + Buffer.from('example.clerk.accounts.dev$').toString('base64'), authenticated }, setStateValue: (_, value) => states.push(value) });
  await tick();
  return { nodes, clerk, window, states, redirects, cleanup, notify: () => listener(), calls: () => signOutCalls };
}

test('visible Sign out ends Clerk session and clears app auth before returning home', async () => {
  const app = await setup();
  const button = app.nodes['.clerk-controls'].children[0];
  assert.equal(button.textContent, 'Sign out');
  await button.onclick();
  assert.equal(app.calls(), 1);
  assert.equal(app.clerk.session, null);
  assert.equal(app.states.at(-1), null);
  assert.equal(app.window.infoflowLastToken, null);
  assert.deepEqual(app.redirects, ['https://example.test/']);
  app.cleanup();
});

test('failed sign-out stays signed in and offers retry', async () => {
  const app = await setup({ signOutError: true });
  const button = app.nodes['.clerk-controls'].children[0];
  await button.onclick();
  assert.equal(button.disabled, false);
  assert.equal(button.textContent, 'Sign out');
  assert.match(app.nodes['.clerk-status'].textContent, /Could not sign out/);
  assert.equal(app.states.at(-1).token, 'jwt');
  assert.equal(app.redirects.length, 0);
  app.cleanup();
});

test('a token refresh completing after logout cannot restore app auth', async () => {
  const app = await setup();
  let resolveToken;
  app.clerk.session.getToken = () => new Promise(resolve => { resolveToken = resolve; });
  app.notify();
  await app.nodes['.clerk-controls'].children[0].onclick();
  resolveToken('stale-jwt');
  await tick();
  assert.equal(app.states.at(-1), null);
  app.cleanup();
});

test('Clerk session loss clears saved Streamlit auth even without a cached browser token', async () => {
  const app = await setup({ authenticated: true, signedOut: true });
  assert.equal(app.states.at(-1), null);
  app.cleanup();
});
