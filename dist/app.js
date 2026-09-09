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
const mechanism = document.getElementById('mechanism');
const inviteWrap = document.querySelector('.invite-wrap');
if (inviteWrap && !document.getElementById('invite-campaign')) {
  const campaign = document.createElement('section');
  campaign.id = 'invite-campaign';
  campaign.className = 'invite-campaign';
  campaign.innerHTML = '<div class="invite-campaign-inner"><span class="invite-campaign-badge">9月限定</span><p class="invite-campaign-kicker">今登録すると、ちょっとおトク。</p><h2>紹介からの新規登録で、<br>ボーナスのチャンス</h2><div class="invite-campaign-benefits"><div><strong>30P</strong><span>入会日から3日連続ログイン</span></div><div><strong>＋2,000P</strong><span>入会月の翌々月末までに、広告利用で5,000P以上獲得</span></div></div><p class="invite-campaign-note">9月中に友達紹介から新規入会した方が対象です。特典にはそれぞれ条件があります。</p><div class="invite-campaign-actions"><a class="button primary invite-link" href="'+INVITE_URL+'" target="_blank" rel="sponsored noopener">紹介リンクから無料登録 →</a><a class="text-link" href="https://pc.moppy.jp/friend/" target="_blank" rel="noopener">モッピー公式のキャンペーン詳細を見る →</a></div></div>';
  inviteWrap.insertAdjacentElement('afterend', campaign);
  if (!document.getElementById('invite-campaign-style')) {
    const style = document.createElement('style');
    style.id = 'invite-campaign-style';
    style.textContent = '.invite-campaign{padding:0 20px 28px;background:#fff}.invite-campaign-inner{max-width:980px;margin:0 auto;padding:24px 28px;border:1px solid #f1ddcf;border-radius:20px;background:linear-gradient(135deg,#fffaf3,#fff 58%,#f5faf7);text-align:center}.invite-campaign-badge{display:inline-block;padding:5px 12px;border-radius:999px;background:#fff0e7;color:#e85d35;font-size:12px;font-weight:700;letter-spacing:.08em}.invite-campaign-kicker{margin:12px 0 4px;color:#e85d35;font-weight:700}.invite-campaign h2{margin:0;font:700 28px/1.5 var(--serif);color:var(--ink)}.invite-campaign-benefits{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;max-width:700px;margin:20px auto 14px}.invite-campaign-benefits div{padding:16px;border-radius:14px;background:#fff;border:1px solid #eee7df}.invite-campaign-benefits strong{display:block;color:var(--teal);font-size:25px}.invite-campaign-benefits span{display:block;margin-top:6px;font-size:13px;line-height:1.6;color:var(--muted)}.invite-campaign-note{margin:0 auto 16px;max-width:720px;font-size:12px;line-height:1.7;color:var(--muted)}.invite-campaign-actions{display:flex;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap}.invite-campaign-actions .button{margin:0}.invite-campaign-actions .text-link{font-size:13px}@media(max-width:700px){.invite-campaign{padding:0 12px 22px}.invite-campaign-inner{padding:20px 16px;border-radius:18px}.invite-campaign h2{font-size:24px;line-height:1.55}.invite-campaign-benefits{grid-template-columns:1fr;gap:10px;margin-top:16px}.invite-campaign-benefits div{padding:14px}.invite-campaign-actions{display:grid;grid-template-columns:1fr;gap:10px}.invite-campaign-actions .button{width:100%}}';
    document.head.appendChild(style);
  }
}
if (mechanism && inviteWrap && !document.getElementById('moppy-fit')) {
  const fit = document.createElement('section');
  fit.className = 'section moppy-fit';
  fit.id = 'moppy-fit';
  fit.innerHTML = '<div class="container"><p class="eyebrow">IS MOPPY FOR ME?</p><h2>モッピー、私にも合う？</h2><div class="moppy-fit-copy"><p>ポイ活と聞くと、クレジットカードを作ったり、たくさんのサービスに申し込んだりしないと貯まらないイメージがあるかもしれません。</p><p>でもモッピーには、ゲームを楽しんだり、いつもの買い物を経由したり、無料で利用できるサービスを試したりと、いろいろな貯め方があります。</p><p>大きく稼ぐことだけがポイ活ではありません。生活や使える時間に合わせて、無理のない方法を選ぶこともできます。</p><p><strong>「自分なら、どんな使い方ができそう？」</strong> まずは5つの質問から、あなたに合いそうな始め方を探してみましょう。</p></div><a class="text-link" href="#diagnosis">5つの質問で自分に合う使い方を見る →</a></div>';
  mechanism.parentNode.insertBefore(fit, mechanism);
}
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
