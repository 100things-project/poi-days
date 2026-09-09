'use strict';
(function loadGA4(){
  const GA_ID='G-0TZ7EH65BW';
  if (typeof window==='undefined' || window.gtag || document.querySelector(`script[src*="${GA_ID}"]`)) return;
  window.dataLayer=window.dataLayer||[];
  window.gtag=function(){window.dataLayer.push(arguments);};
  window.gtag('js',new Date());
  window.gtag('config',GA_ID);
  const s=document.createElement('script');
  s.async=true;
  s.src=`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);
})();
const INVITE_URL = 'https://pc.moppy.jp/entry/invite.php?invite=Jh7He170&openExternalBrowser=1';
const INVITE_CODE = 'Jh7He170';
function getRoute(a) {
  const routes = [];
  let title = 'すきま時間に、コツコツ型';
  let summary = 'まずはアンケートなど、短い時間で取り組めるものから。自分に合うか、少しずつ試してみましょう。';
  if (a.shop !== 'rare') {
    routes.push({id:'shop', title:'予定していた買い物を、モッピー経由に', text:'対象ショップと獲得条件を確認してから利用。ポイントのために買い物を増やさないのがコツです。'});
    title = 'いつもの買い物で、コツコツ型';
    summary = '普段の買い物に、ひと手間だけ。買う予定のものが対象になっているか確認する使い方が合いそうです。';
  }
  if (a.game !== 'no' && a.time !== '5') {
    routes.push({id:'game', title:'気になるゲームを、ひとつから', text:'達成条件と期限、端末の対応状況を確認。必要なプレイ時間や課金の有無も見て、無理のない案件を選びましょう。'});
    if (a.game === 'love') {title = 'ゲームを楽しみながら、ポイ活型';summary = '遊ぶ時間をポイ活にも。いくつも同時にはじめず、まずひとつのゲームで達成条件を確認しながら進めましょう。';}
  }
  if (a.card === 'ok') {
    routes.push({id:'card',title:'必要なカードがあるときだけ比較',text:'ポイント以外の年会費やサービス内容、審査・利用条件を確認。不要なカードを増やさず、必要な一枚を検討しましょう。'});
  }
  routes.push({id:'survey',title:'すきま時間にアンケート',text:'回答時間と獲得条件を見て、少額からコツコツ。短時間で大きな金額が貯まるとは限りません。'});
  let goal = '目標は' + Number(a.goal).toLocaleString('ja-JP') + '円分。利用前に、各案件のポイント数と承認時期を確認しましょう。';
  if (a.goal !== '1000') goal += ' 目標額に届くかは選ぶ案件と達成状況によります。無理な申し込みはせず、小さな獲得から始めて大丈夫です。';
  if (a.time === '5' && a.game !== 'no') goal += ' 1日5分ではゲームの期限達成が難しい場合があるため、今回は時間のかかるゲームをおすすめから外しています。';
  return {title,summary,routes,goal};
}
if (typeof module !== 'undefined') module.exports = {getRoute, INVITE_URL, INVITE_CODE};
if (typeof document !== 'undefined') {
const mechanismContainer = document.querySelector('.mechanism .container');
if (mechanismContainer && !mechanismContainer.querySelector('.moppy-intro')) {
  const intro = document.createElement('p');
  intro.className = 'moppy-intro';
  intro.textContent = 'モッピーは、いつもの買い物やゲーム、サービス利用でポイントを貯められるサイトです。貯まったポイントは、現金や電子マネーなどに交換できます。';
  const mechanismTitle = mechanismContainer.querySelector('h2');
  if (mechanismTitle) mechanismContainer.insertBefore(intro, mechanismTitle);
}
const quiz = document.getElementById('quiz');
const result = document.getElementById('result');
const showResult = document.getElementById('show-result');
const keys = ['card','game','shop','time','goal'];
const answers = () => Object.fromEntries(new FormData(quiz).entries());
quiz.addEventListener('change', () => {
  const a = answers();
  const count = keys.filter(key => a[key]).length;
  document.getElementById('answered').textContent = `${count} / 5 回答`;
  document.getElementById('progress').value = count;
  showResult.disabled = count !== 5;
  result.hidden = true;
});
quiz.addEventListener('submit', event => {
  event.preventDefault();
  const a = answers();
  if (!keys.every(key => a[key]) || !quiz.reportValidity()) return;
  const r = getRoute(a);
  document.getElementById('result-title').textContent = r.title;
  document.getElementById('result-summary').textContent = r.summary;
  document.getElementById('goal-note').textContent = r.goal;
  const container = document.getElementById('routes');
  container.replaceChildren();
  r.routes.forEach((route, i) => {
    const article = document.createElement('article'); article.className = 'route';
    const title = document.createElement('h4'); title.textContent = `${i + 1}. ${route.title}`;
    const text = document.createElement('p'); text.textContent = route.text;
    article.append(title, text); container.append(article);
  });
  result.hidden = false;
  result.focus({preventScroll:true});
  result.scrollIntoView({behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'start'});
});
document.getElementById('retry').addEventListener('click', () => {
  quiz.reset(); quiz.dispatchEvent(new Event('change'));
  quiz.querySelector('input').focus();
});
let toastTimer;
function notifyCopy(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message; toast.classList.add('visible');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove('visible'), 5000);
}
document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
  const isCode = button.dataset.copy === 'code';
  const value = isCode ? INVITE_CODE : INVITE_URL;
  const field = document.getElementById(isCode ? 'invite-code' : 'invite-url');
  let copied = false;
  try { if (navigator.clipboard && window.isSecureContext) {await navigator.clipboard.writeText(value); copied = true;} } catch (_) {}
  if (!copied) {
    field.focus(); field.select(); field.setSelectionRange(0,field.value.length);
    try {copied = document.execCommand('copy');} catch (_) {}
    if (copied) button.focus();
  }
  notifyCopy(copied ? (isCode ? '招待コードをコピーしました' : '招待URLをコピーしました') : 'コピーできませんでした。選択された文字を長押ししてコピーしてください。');
}));
}
function calculatePlan(rows, target) {
  const valid = n => Number.isSafeInteger(n) && n >= 0 && n <= 10000000;
  if (!valid(target) || target === 0 || rows.length !== 3 || !rows.every(r => valid(r.points) && valid(r.cost))) throw new RangeError('整数の範囲を確認してください');
  const points = rows.reduce((sum,r) => sum+r.points,0);
  const cost = rows.reduce((sum,r) => sum+r.cost,0);
  return {points,cost,net:points-cost,remaining:Math.max(0,target-points)};
}
if (typeof module !== 'undefined') module.exports.calculatePlan = calculatePlan;
if (typeof document !== 'undefined') {
  const form = document.getElementById('point-plan');
  const output = document.getElementById('plan-output');
  const format = n => n.toLocaleString('ja-JP');
  form.addEventListener('input', () => {output.hidden = true;});
  form.addEventListener('reset', () => {output.hidden = true;output.replaceChildren();});
  form.addEventListener('submit', e => {
    e.preventDefault();
    if(!form.reportValidity()) return;
    const data = new FormData(form);
    const rows = [1,2,3].map(i=>({points:Number(data.get('points'+i)||0),cost:Number(data.get('cost'+i)||0)}));
    let result;
    try{result=calculatePlan(rows,Number(document.getElementById('point-target').value));}catch(_){return;}
    output.replaceChildren();
    const title=document.createElement('span');title.textContent='条件をすべて達成・承認された場合の合計';
    const total=document.createElement('strong');total.textContent=format(result.points)+' P（'+format(result.points)+'円相当）';
    output.append(title,total);
    const lines=[
      '入力した追加費用：'+format(result.cost)+'円 ／ 費用を差し引いた金額：'+format(result.net)+'円相当',
      result.remaining>0?'目標まで、あと'+format(result.remaining)+'P。':'入力したプランでは目標ポイントに届いています。',
      result.net<0?'追加費用が獲得ポイント相当額を上回っています。支出も含めてプランを見直しましょう。':'ポイントの承認時期と交換条件も確認して、無理のないプランにしましょう。'
    ];
    lines.forEach(line=>{const p=document.createElement('p');p.textContent=line;output.append(p);});
    output.hidden=false;
  });
  const checks=[...document.querySelectorAll('#start-checks input')];
  const updateChecks=()=>{
    const n=checks.filter(c=>c.checked).length;
    document.getElementById('check-progress').textContent=n+' / 7 完了'+(n===7?' おつかれさまでした！':'');
    document.getElementById('check-meter').value=n;
  };
  checks.forEach(c=>c.addEventListener('change',updateChecks));
  document.getElementById('reset-checks').addEventListener('click',()=>{checks.forEach(c=>{c.checked=false;});updateChecks();});
  window.addEventListener('pageshow',updateChecks);
}
