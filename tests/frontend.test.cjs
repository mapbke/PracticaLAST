// Regression checks for the actual client state functions, without a browser dependency.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('app/static/js/main.js', 'utf8').replace(/initialize\(\);\s*$/, '');

function setup(saved = []) {
  const storage = new Map([['kurotsuki-cart', JSON.stringify(saved)]]);
  const elements = new Map();
  const element = selector => {
    if (!elements.has(selector)) elements.set(selector, {
      content: 'test-csrf', hidden: false, disabled: false, textContent: '',
      setAttribute() {}, classList: {add() {}, remove() {}},
    });
    return elements.get(selector);
  };
  const context = vm.createContext({
    Intl, AbortController, TypeError, setTimeout, clearTimeout,
    document: {documentElement: {dataset: {theme:'light'}}, querySelector: element},
    localStorage: {getItem:key=>storage.get(key),setItem:(key,value)=>storage.set(key,value)},
    fetch: async () => { throw new Error('Unexpected network request'); },
  });
  vm.runInContext(source, context);
  // Isolate data flow from DOM drawing; browser checks cover the real rendering.
  vm.runInContext('renderCart=()=>{}; renderPrice=()=>{}; renderConfigurationSummary=()=>{}; toast=()=>{};',context);
  return {context,storage,run:code=>vm.runInContext(code,context)};
}

test('theme changes do not overwrite an unrestored cart', () => {
  const env=setup([{quantity:3,material:'alcantara'}]);
  const before=env.storage.get('kurotsuki-cart');
  env.run("state.theme='dark'; applyTheme()");
  assert.equal(env.storage.get('kurotsuki-cart'),before);
  assert.equal(env.storage.get('kurotsuki-theme'),'dark');
});

test('partial restoration failure preserves storage and blocks cart mutation', async () => {
  const env=setup([{quantity:1},{quantity:2}]);
  const before=env.storage.get('kurotsuki-cart');
  env.run("api=async(path,config)=>{if(config.quantity===2)throw Error('offline');return {config,total:100}};");
  await env.run('restoreCart()');
  assert.equal(env.run('state.cartRestoreFailed'),true);
  await env.run('addToCart({quantity:3})');
  env.run('syncStateToLocalStorage()');
  assert.equal(env.storage.get('kurotsuki-cart'),before);
  assert.equal(env.run('state.cart.length'),1);
});

test('restoration retry recovers all items and uses fresh server prices', async () => {
  const env=setup([{quantity:2,total:1}]);
  env.run("api=async()=>{throw Error('offline')}");
  await env.run('restoreCart()');
  env.run('api=async(path,config)=>({config,total:86400})');
  await env.run('restoreCart()');
  assert.equal(env.run('state.cartRestoreFailed'),false);
  assert.equal(env.run('state.cart[0].total'),86400);
});

test('an earlier quote response cannot replace the latest configuration', async () => {
  const env=setup();
  env.run('readConfig=()=>({...defaults}); pending=[]; api=()=>new Promise(resolve=>pending.push(resolve));');
  const first=env.run('updateQuote()');
  const second=env.run('updateQuote()');
  env.run('pending[1]({total:90000})'); await second;
  env.run('pending[0]({total:10000})'); await first;
  assert.equal(env.run('state.quote.total'),90000);
});

test('rejected quantity keeps the last valid cart and persisted data', async () => {
  const env=setup([{quantity:2}]);
  env.run("state.cart=[{config:{quantity:2},total:86400}];api=async()=>{throw Error('invalid')}");
  await env.run('changeQuantity(0,0)');
  assert.equal(env.run('state.cart[0].config.quantity'),2);
  assert.equal(env.run('state.cartBusy'),false);
  assert.equal(JSON.parse(env.storage.get('kurotsuki-cart'))[0].quantity,2);
});

test('simultaneous adds cannot race past the 30 item limit', async () => {
  const env=setup();
  env.run('state.cart=Array.from({length:29},()=>({config:{quantity:1}})); api=()=>new Promise(resolve=>{finishAdd=resolve});');
  const first=env.run('addToCart({quantity:1})');
  await env.run('addToCart({quantity:1})');
  env.run('finishAdd({config:{quantity:1},total:100})'); await first;
  assert.equal(env.run('state.cart.length'),30);
});

test('network errors receive a useful message', async () => {
  const env=setup();
  env.context.fetch=async()=>{throw new TypeError('Failed to fetch')};
  await assert.rejects(env.run("api('/api/calculate',{})"),/Нет связи с сервером/);
});

test('non-JSON server responses are handled without exposing parser errors', async () => {
  const env=setup();
  env.context.fetch=async()=>({ok:false,json:async()=>{throw new SyntaxError('Unexpected token <')}});
  await assert.rejects(env.run("api('/api/calculate',{})"),/некорректный ответ/);
});
