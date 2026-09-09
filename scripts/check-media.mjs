import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';
const html=readFileSync('docs/index.html','utf8');
const source=readFileSync('docs/media-home.js','utf8');
const original=JSON.parse(readFileSync('content/media-home.json','utf8'));
function boot(data=structuredClone(original)){
 const dom=new JSDOM(html,{url:'https://100things-project.github.io/poi-days/index.html',runScripts:'outside-only'});
 if(data!==null)dom.window.POI_DAYS_MEDIA=data;
 dom.window.eval(source);
 return dom;
}
let runs=0;
for(const count of [0,1,5,12]){
 const data=structuredClone(original);
 for(const site of data.sites)data.rankings[site.id]=Array.from({length:count},(_,i)=>({...original.rankings.moppy[0],title:'とても長い案件名'.repeat(20)+i}));
 const dom=boot(data),d=dom.window.document;
 for(const site of data.sites){
  const button=d.querySelector('#tab-'+site.id);button.click();
  assert.equal(button.getAttribute('aria-selected'),'true');
  assert.equal(d.querySelectorAll('[aria-selected="true"]').length,1);
  assert.equal(d.querySelectorAll('.ranking-row').length,Math.min(count,5));
  assert.equal(d.querySelector('#ranking-panel').getAttribute('aria-labelledby'),button.id);
  if(!count)assert.match(d.querySelector('#ranking-panel').textContent,/準備中/);
  runs++;
 }
 dom.window.close();
}
for(const data of [null,{}, {rankings:{}}, {rankings:{moppy:[null,{}, {title:'<img src=x onerror=alert(1)>',image:'javascript:alert(1)',sample:true,reward:999999}]}}]){
 const dom=boot(data),d=dom.window.document;
 assert.equal(d.querySelectorAll('img[onerror]').length,0);
 assert.equal(d.querySelectorAll('img[src^="javascript:"]').length,0);
 assert.doesNotMatch(d.querySelector('#ranking-panel').textContent,/999,999/);
 if(!data||!data.rankings)assert.equal(d.querySelector('.ranking-tabs').hidden,true);
 dom.window.close();runs++;
}
const dom=boot(),d=dom.window.document;
const input=d.querySelector('#search-query'); input.value='ゲーム';d.querySelector('#site-search').dispatchEvent(new dom.window.Event('submit',{cancelable:true}));
assert.equal(d.querySelectorAll('#search-results a').length,1);
input.value='存在しない検索語';d.querySelector('#site-search').dispatchEvent(new dom.window.Event('submit',{cancelable:true}));assert.match(d.querySelector('#search-results').textContent,/該当する記事がありません/);
const first=d.querySelector('#tab-moppy');first.focus();first.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));assert.equal(d.querySelector('#tab-hapitas').getAttribute('aria-selected'),'true');
const img=d.querySelector('.lead-image img');img.dispatchEvent(new dom.window.Event('error'));assert.equal(img.getAttribute('data-fallback'),'true');assert.match(img.src,/visuals\/about.svg$/);
img.dispatchEvent(new dom.window.Event('error'));assert.equal(img.getAttribute('src'),null);
dom.window.close();
// Script-disabled HTML has complete content and native menu/search fallback.
const nojs=new JSDOM(html);assert.equal(nojs.window.document.querySelectorAll('.article-row').length,5);assert.equal(nojs.window.document.querySelectorAll('.ranking-row').length,5);assert.equal(nojs.window.document.querySelectorAll('main > section').length,8);nojs.window.close();
console.log(`PASS: ${runs} rank/missing-data cases; 0/1/5/12 items, tabs/keyboard, long text retained, safe rendering, search, image fallback, script-disabled content. DOM tests only; no visual-layout claims.`);
