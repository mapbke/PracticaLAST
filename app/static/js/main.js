'use strict';
const $ = (selector) => document.querySelector(selector);
const defaults = {carType:'coupe',target:'wheel',material:'leather',stitchColor:'red',centerMark:false,carbonInserts:false,perforation:false,embroidery:false,quantity:1};
const state = {theme:document.documentElement.dataset.theme,configurator:{...defaults},cart:[],triadMode:{unlocked:false,archetype:null},quote:null,cartBusy:false,cartRestoreFailed:false};
const money = value => new Intl.NumberFormat('ru-RU',{style:'currency',currency:'RUB',maximumFractionDigits:0}).format(value);
let quoteVersion = 0, toastTimer, quantityTimer;
function toast(message) { if (!$('#toast')) return; $('#toast').textContent=message; $('#toast').classList.add('visible'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),3500); }
function syncStateToLocalStorage() { if(state.cartRestoreFailed)return; try { localStorage.setItem('kurotsuki-cart',JSON.stringify(state.cart.map(item=>item.config))); } catch { toast('Браузер не разрешил сохранение. Подборка доступна до закрытия страницы.'); } }
function restoreStateFromLocalStorage() { try { const saved=JSON.parse(localStorage.getItem('kurotsuki-cart')||'[]'); return Array.isArray(saved)?saved.slice(0,30):[]; } catch { return []; } }
async function api(path,data) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, {method:'POST', signal:controller.signal,
      headers:{'Content-Type':'application/json','X-CSRFToken':$('meta[name="csrf-token"]').content},
      body:JSON.stringify(data)});
    let result;
    try { result = await response.json(); }
    catch { throw new Error('Сервер вернул некорректный ответ. Попробуйте ещё раз.'); }
    if(!response.ok) throw new Error(result.error || 'Не удалось выполнить запрос.');
    return result;
  } catch(error) {
    if(error.name === 'AbortError') throw new Error('Сервер не ответил вовремя. Попробуйте ещё раз.');
    if(error instanceof TypeError) throw new Error('Нет связи с сервером. Проверьте подключение и повторите попытку.');
    throw error;
  } finally { clearTimeout(timeout); }
}
function applyTheme() { document.documentElement.dataset.theme=state.theme; $('#theme-toggle').setAttribute('aria-label',state.theme==='dark'?'Включить светлую тему':'Включить тёмную тему'); $('#theme-toggle').setAttribute('aria-pressed',String(state.theme==='dark')); try { localStorage.setItem('kurotsuki-theme',state.theme); } catch { toast('Не удалось сохранить тему в браузере.'); } }
function readConfig() { const form=$('#config-form'); const config={}; for(const key of Object.keys(defaults)) { const input=form.elements[key]; config[key]=input.type==='checkbox'?input.checked:key==='quantity'?Number(input.value):input.value; } return config; }
function renderConfigurationSummary() { const box=$('#spec-summary'); box.replaceChildren(); for(const key of ['carType','material','stitchColor']) { const option=$('#config-form').elements[key].selectedOptions[0]; const tag=document.createElement('span'); tag.textContent=option.textContent; box.append(tag); } for(const key of ['centerMark','carbonInserts','perforation','embroidery']) { if(state.configurator[key]) { const tag=document.createElement('span'); tag.textContent=$('#config-form').elements[key].nextElementSibling.textContent; box.append(tag); } } }
function renderPrice() { $('#config-price').textContent=state.quote?money(state.quote.total):'Считаем…'; $('#config-add').disabled=!state.quote; if(state.quote) $('#visual-title').textContent=state.quote.title; }
async function updateQuote() { const version=++quoteVersion; state.configurator=readConfig(); state.quote=null; renderPrice(); renderConfigurationSummary(); $('#config-error').textContent=''; try { const quote=await api('/api/calculate',state.configurator); if(version!==quoteVersion)return; state.quote=quote; renderPrice(); } catch(error) { if(version!==quoteVersion)return; $('#config-price').textContent='—'; $('#config-error').textContent=error.message; } }
function applyPreset(preset) { state.configurator={...defaults,...preset}; const form=$('#config-form'); for(const [key,value] of Object.entries(state.configurator)) { if(!form.elements[key])continue; if(form.elements[key].type==='checkbox')form.elements[key].checked=value; else form.elements[key].value=value; } updateQuote(); $('#configurator').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}); form.elements.carType.focus({preventScroll:true}); }
function updateCartCounter() { $('#cart-count').textContent=state.cart.reduce((sum,item)=>sum+item.config.quantity,0); }
function renderCart() { $('#cart-retry').hidden=!state.cartRestoreFailed; $('#cart-warning').textContent=state.cartRestoreFailed?'Не удалось проверить всю сохранённую подборку. Она сохранена в браузере; повторите восстановление перед изменением или отправкой.':''; const box=$('#cart-items');box.replaceChildren(); updateCartCounter(); if(!state.cart.length) { const p=document.createElement('p');p.textContent='Здесь начинается ваш интерьер. Добавьте готовое решение или собственную конфигурацию.';box.append(p); } state.cart.forEach((item,index)=>{ const row=document.createElement('article'); row.className='cart-row'; const title=document.createElement('h3');title.textContent=item.title; const summary=document.createElement('p');summary.textContent=[...['carType','stitchColor'].map(key=>Array.from($('#config-form').elements[key].options).find(option=>option.value===item.config[key])?.textContent),...Object.entries(item.config).filter(([key,value])=>value===true).map(([key])=>$('#config-form').elements[key].nextElementSibling.textContent)].filter(Boolean).join(' · '); const controls=document.createElement('div');controls.className='cart-row-controls';const quantity=document.createElement('input');quantity.type='number';quantity.min=1;quantity.max=20;quantity.value=item.config.quantity;quantity.setAttribute('aria-label',`Количество: ${item.title}`);quantity.disabled=state.cartBusy||state.cartRestoreFailed;quantity.addEventListener('input',()=>{clearTimeout(quantityTimer); quantityTimer=setTimeout(()=>changeQuantity(index,Number(quantity.value)),300);}); quantity.addEventListener('change',()=>{clearTimeout(quantityTimer); changeQuantity(index,Number(quantity.value));}); const remove=document.createElement('button');remove.textContent='Удалить';remove.disabled=state.cartBusy||state.cartRestoreFailed;remove.addEventListener('click',()=>{clearTimeout(quantityTimer);state.cart.splice(index,1);renderCart();syncStateToLocalStorage();}); const price=document.createElement('strong');price.textContent=money(item.total);controls.append(quantity,remove,price);row.append(title,summary,controls);box.append(row); }); $('#cart-total').textContent=money(state.cart.reduce((sum,item)=>sum+item.total,0)); $('#cart-checkout').disabled=!state.cart.length||state.cartBusy||state.cartRestoreFailed; }
async function changeQuantity(index,quantity) { clearTimeout(quantityTimer); if(state.cartBusy||state.cartRestoreFailed||!state.cart[index]||state.cart[index].config.quantity===quantity)return;state.cartBusy=true;renderCart();try { state.cart[index]=await api('/api/calculate',{...state.cart[index].config,quantity});syncStateToLocalStorage(); }catch(error){toast(error.message);}finally{state.cartBusy=false;renderCart();} }
async function addToCart(config,button) { if(state.cartRestoreFailed){toast('Сначала повторите восстановление корзины.');return;} if(state.cartBusy){toast('Подождите завершения обновления корзины.');return;} if(state.cart.length>=30){toast('В корзине уже 30 позиций.');return;} state.cartBusy=true;renderCart();if(button)button.disabled=true;try{const item=await api('/api/calculate',config);state.cart.push(item);syncStateToLocalStorage();toast('Конфигурация добавлена в подборку');}catch(error){toast(error.message);}finally{state.cartBusy=false;renderCart();if(button)button.disabled=false;if(button===$('#config-add'))renderPrice();} }
function applyTriadPreset(name) { const presets={machiavellian:{material:'carbon_matte',stitchColor:'black',carbonInserts:true},psychopathic:{material:'alcantara',stitchColor:'red',centerMark:true,perforation:true},narcissistic:{material:'carbon_gloss',stitchColor:'purple',embroidery:true}};state.triadMode.archetype=name;$('#secret-dialog').close();applyPreset(presets[name]);toast(`Применён ${name}`); }
async function initialize() {
  if(!$('#config-form'))return;
  $('#theme-toggle').addEventListener('click',()=>{state.theme=state.theme==='dark'?'light':'dark';applyTheme();});
  $('#theme-toggle').setAttribute('aria-pressed',String(state.theme==='dark'));
  $('#theme-toggle').setAttribute('aria-label',state.theme==='dark'?'Включить светлую тему':'Включить тёмную тему');
  $('#menu-toggle').addEventListener('click',()=>{const open=$('#navigation').classList.toggle('open');$('#menu-toggle').setAttribute('aria-expanded',String(open));});
  document.querySelectorAll('#navigation a').forEach(link=>link.addEventListener('click',()=>{$('#navigation').classList.remove('open');$('#menu-toggle').setAttribute('aria-expanded','false');}));
  window.addEventListener('scroll',()=>$('.header').classList.toggle('compact',window.scrollY>50),{passive:true});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'){$('#navigation').classList.remove('open');$('#menu-toggle').setAttribute('aria-expanded','false');}});
  $('#config-form').addEventListener('input',updateQuote);
  $('#config-form').addEventListener('submit',event=>{event.preventDefault();if(state.quote)addToCart(state.quote.config,$('#config-add'));});
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>applyPreset(JSON.parse(button.dataset.preset))));
  document.querySelectorAll('[data-add]').forEach(button=>button.addEventListener('click',()=>addToCart(JSON.parse(button.dataset.add),button)));
  $('#cart-retry').addEventListener('click',restoreCart);
  $('#cart-open').addEventListener('click',()=>$('#cart-dialog').showModal());
  document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>document.getElementById(button.dataset.close).close()));
  $('#cart-checkout').addEventListener('click',()=>{$('#cart-dialog').close();$('#contact').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});$('#contact-form').elements.name.focus({preventScroll:true});});
  document.querySelectorAll('.faq-item button').forEach(button=>button.addEventListener('click',()=>{const expanded=button.getAttribute('aria-expanded')==='true';button.setAttribute('aria-expanded',String(!expanded));document.getElementById(button.getAttribute('aria-controls')).hidden=expanded;button.querySelector('span').textContent=expanded?'+':'−';}));
  let clicks=0,lastClick=0;$('#secret-trigger').addEventListener('click',()=>{const now=Date.now();clicks=now-lastClick<1500?clicks+1:1;lastClick=now;if(clicks===3){state.triadMode.unlocked=true;$('#secret-dialog').showModal();clicks=0;}});
  document.querySelectorAll('[data-triad]').forEach(button=>button.addEventListener('click',()=>applyTriadPreset(button.dataset.triad)));
  $('#contact-form').addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget;const status=$('#contact-status');if(state.cartBusy||state.cartRestoreFailed){status.textContent='Дождитесь обновления корзины или повторите её восстановление.';return;}const button=form.querySelector('[type=submit]');button.disabled=true;status.textContent='Сохраняем заявку…';try{const data=Object.fromEntries(new FormData(form));data.consent=form.elements.consent.checked;data.configuration=readConfig();data.cart=state.cart.map(item=>item.config);const result=await api('/api/contact',data);status.textContent=`Заявка №${result.id}. ${result.message} Расчёт: ${money(result.total)}.`;form.reset();}catch(error){status.textContent=error.message;}finally{button.disabled=false;}});
  updateQuote();
  await restoreCart();
}
async function restoreCart() {
  if(state.cartBusy)return;
  state.cartBusy=true; $('#cart-retry').disabled=true; renderCart();
  const restored=await Promise.allSettled(restoreStateFromLocalStorage().map(config=>api('/api/calculate',config)));
  state.cartRestoreFailed=restored.some(result=>result.status==='rejected');
  state.cart=restored.filter(result=>result.status==='fulfilled').map(result=>result.value);
  state.cartBusy=false; $('#cart-retry').disabled=false; renderCart();
  if(state.cartRestoreFailed)toast('Не удалось восстановить всю корзину. Сохранённые данные не изменены.');
}
initialize();
