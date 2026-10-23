"""The browser-side behaviour of the page: login forms, the add-bill panels, the dashboard drawing, Watt and the guided tour.
All the maths is NOT here: it is done in Python and fetched from /api/... Served at /assets/app.js."""

JS = r'''/* Smart Energy Advisor — front end. All calculations happen in Python on the Flask server (see app.py). */
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let cur='login', introPhase=true;
/* go() lives with the unlock logic below */
document.addEventListener('click',e=>{const t=e.target.closest('[data-go]'); if(t){e.preventDefault(); go(t.dataset.go);}});


/* reveal + section tracking */
const rio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in'); rio.unobserve(e.target);}}),{threshold:.12});
$$('[data-r]').forEach(el=>rio.observe(el));
const NAMES={login:'Login','add-bill':'Add Bill',dashboard:'Dashboard'};
const sio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){cur=e.target.id;
  $$('#nav a').forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+cur));
  $('#ctx').textContent='● Looking at: '+NAMES[cur]; if(!introPhase) renderChips(); if(cur==='dashboard') runDash();}}),{threshold:.5});
$$('.screen').forEach(s=>sio.observe(s));

/* cursor-follow eyes */
const sets=[{svg:$('#mascot'),w:400,h:420,max:7,div:8,p:[[$('#mpL'),172,195],[$('#mpR'),228,195]]},
            {svg:$('#fab svg'),w:100,h:100,max:2.4,div:14,p:[[$('#fpL'),38,46],[$('#fpR'),62,46]]}];
addEventListener('pointermove',e=>sets.forEach(s=>{const r=s.svg.getBoundingClientRect(); const x=(e.clientX-r.left)*s.w/r.width, y=(e.clientY-r.top)*s.h/r.height;
  s.p.forEach(([el,cx,cy])=>{const dx=x-cx,dy=y-cy,d=Math.hypot(dx,dy)||1,o=Math.min(s.max,d/s.div); el.setAttribute('cx',cx+dx/d*o); el.setAttribute('cy',cy+dy/d*o);});}),{passive:true});

/* mascot shuts its eyes while typing the password */
document.addEventListener('focusin',e=>{if(e.target.matches&&e.target.matches('#loginForm input[type=password]')) $('#mascot').classList.add('shut');});
document.addEventListener('focusout',e=>{if(e.target.matches&&e.target.matches('#loginForm input[type=password]')) $('#mascot').classList.remove('shut');});

/* ================= talking to the Flask server (all the maths happens in Python) ================= */
let ME={user:null,guest:false,has_data:false,csrf:''}, S=null, mode='login', dataReady=false;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path,opts={}){
  const o={credentials:'same-origin',method:opts.method||'GET',headers:{}};
  if(o.method!=='GET') o.headers['X-CSRF-Token']=ME.csrf;
  if(opts.body instanceof FormData) o.body=opts.body;
  else if(opts.body!==undefined){o.headers['Content-Type']='application/json'; o.body=JSON.stringify(opts.body);}
  let r; try{r=await fetch(path,o);}catch(e){throw new Error('Could not reach the server. Is it running?');}
  let j={}; try{j=await r.json();}catch(e){}
  if(!r.ok){const err=new Error(j.error||'Something went wrong ('+r.status+').'); err.status=r.status; err.fallback=!!j.fallback; throw err;}
  if(j.csrf) ME.csrf=j.csrf;
  return j;
}
function applyMe(me){ME=me; S=me.user?{email:me.user.email,name:me.user.name}:(me.guest?{guest:true}:null); dataReady=!!me.has_data;}
async function afterAuth(me){applyMe(me); mode='login'; renderAuth(); renderLogin(); updateNav(); updateGate(); if(dataReady) await render();}
async function logout(){
  try{applyMe(await api('/api/logout',{method:'POST'}));}catch(e){applyMe({user:null,guest:false,has_data:false,csrf:ME.csrf});}
  mode='login'; lockAll(); renderAuth(); renderLogin(); go('login');}
function renderAuth(){const a=$('#auth'); if(!S){a.innerHTML='';return;}
  a.innerHTML=S.guest?'<span>Guest</span><button type="button" id="alog">Log in</button>':'<span>Hi, <b></b></span><button type="button" id="alog">Log out</button>';
  if(!S.guest) a.querySelector('b').textContent=S.name||S.email; $('#alog').onclick=()=>S.guest?go('login'):logout();}
function renderLogin(){
  const c=$('#loginForm');
  if(S&&!S.guest){c.innerHTML='<span class="eyebrow">⚡ Logged in</span><h2></h2><p class="small" style="text-align:left;margin:0 0 18px">Your bills are saved to your account.</p><button class="btn" type="button" data-go="add-bill">Continue →</button><button class="btn ghost" type="button" id="lo">Log out</button>'; c.querySelector('h2').textContent='Hi, '+(S.name||S.email); $('#lo').onclick=logout; return;}
  const su=mode==='signup';
  c.innerHTML=`<span class="eyebrow">⚡ ${su?'Create account':'Welcome back'}</span><h2>${su?'Sign up':'Log in'}</h2>
  <form id="lf" novalidate>${su?'<label>Name<input name="name" autocomplete="name" placeholder="Your name" maxlength="80"></label>':''}
  <label>Email<input name="email" type="email" placeholder="you@example.com" autocomplete="email"></label>
  <label>Password<input name="pw" type="password" placeholder="${su?'At least 6 characters':'••••••••'}" autocomplete="${su?'new-password':'current-password'}"></label>
  <p class="err" id="lerr" role="alert"></p><button class="btn" type="submit" style="margin-top:8px">${su?'Create account':'Log in'} →</button></form>
  <button class="btn ghost" type="button" id="lg">Continue as guest</button>
  <p class="small">${su?'Already have an account?':'New here?'} <a href="#" id="lt">${su?'Log in':'Create an account'}</a></p>
  <p class="small" style="margin-top:6px;font-size:13px">Your password is stored hashed on the server, never as plain text.</p>`;
  $('#lg').onclick=async()=>{try{await afterAuth(await api('/api/guest',{method:'POST'})); go('add-bill');}catch(ex){$('#lerr').textContent=ex.message;}};
  $('#lt').onclick=e=>{e.preventDefault(); mode=su?'login':'signup'; renderLogin();};
  $('#lf').addEventListener('submit',async e=>{e.preventDefault(); const f=new FormData(e.target), email=(f.get('email')||'').trim().toLowerCase(), pw=f.get('pw')||'', name=(f.get('name')||'').trim(), err=$('#lerr');
    if(!/^\S+@\S+\.\S+$/.test(email)){err.textContent='Please enter a valid email address.';return;}
    if(pw.length<6){err.textContent='Password must be at least 6 characters.';return;}
    err.textContent='';
    try{await afterAuth(await api(su?'/api/signup':'/api/login',{method:'POST',body:{email,password:pw,name}})); go('add-bill');}
    catch(ex){err.textContent=ex.message;}});
}

/* ---------- page gating: login -> add bill -> dashboard ---------- */
function updateNav(){$$('#nav a').forEach(a=>{const id=a.getAttribute('href').slice(1), locked=$('#'+id).hidden&&!(id==='add-bill'&&S); a.classList.toggle('locked',locked); a.setAttribute('aria-disabled',locked?'true':'false'); a.title=locked?(id==='add-bill'?'Log in or continue as guest first':'Add your bill data first'):'';});}
function updateGate(){const b=$('#toDash'); if(!b) return; b.disabled=!dataReady; $('#toDashHint').textContent=dataReady?'':'Add your bill data above first, or use the sample data.';}
function unlock(id){const el=$('#'+id); if(!el.hidden) return; el.hidden=false; updateNav(); setTimeout(()=>maybeTour(id),1100);}
function lockAll(){['add-bill','dashboard'].forEach(i=>$('#'+i).hidden=true); resetAdd(); updateNav(); updateGate();}
function go(id){const el=$('#'+id); if(el.hidden){ if(id==='add-bill'&&S) unlock(id); else if(id==='dashboard'&&S&&dataReady) unlock(id); else return; } requestAnimationFrame(()=>el.scrollIntoView({behavior:'smooth'}));}

/* ---------- adding bills: CSV, manual entry, photo (each one is sent to the Python server) ---------- */
const APN={ac:'Air Conditioner',fridge:'Refrigerator',light:'Lighting',wash:'Washing Machine',tv:'Television',misc:'Other / Misc'};
async function afterData(){dataReady=true; ME.has_data=true; updateGate(); await render();}
function panelCSV(p){
  p.innerHTML=`<h4>Upload bill history CSV</h4><div class="s">Needs columns <b>billing_month, units_consumed, bill_amount</b>. Optional appliance columns: ac_units, fridge_units, lighting_units, washing_machine_units, tv_units, misc_units.</div>
  <label class="drop" id="drop" tabindex="0"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 16V4M7 9l5-5 5 5M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/></svg><div style="margin-top:8px"><b>Drag &amp; drop your CSV here</b>, or click to browse</div><input id="csvf" type="file" accept=".csv,text/csv,.txt" hidden></label>
  <p class="err" id="cmsg" role="status"></p>
  <div class="linkrow"><button class="mini-link" id="tpl" type="button">Download a CSV template</button><button class="mini-link" id="smp" type="button">Use the sample data instead</button></div>`;
  const msg=$('#cmsg'), drop=$('#drop');
  const handle=async f=>{ if(!f) return; msg.className='err'; msg.textContent=''; if(f.size>5e6){msg.textContent='That file is too large (max 5 MB).';return;}
    const fd=new FormData(); fd.append('file',f); msg.className='ok-msg'; msg.textContent='Uploading…';
    try{const r=await api('/api/upload/csv',{method:'POST',body:fd}); await afterData(); msg.className='ok-msg';
      msg.textContent='Loaded '+r.months+' month'+(r.months>1?'s':'')+' from '+r.source+(r.skipped?' ('+r.skipped+' row'+(r.skipped>1?'s':'')+' skipped)':'')+'. Tap “See my dashboard” below when you are ready.';}
    catch(ex){msg.className='err'; msg.textContent=ex.message;}};
  $('#csvf').addEventListener('change',e=>{handle(e.target.files[0]); e.target.value='';});
  drop.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault(); $('#csvf').click();}});
  ['dragenter','dragover'].forEach(t=>drop.addEventListener(t,e=>{e.preventDefault(); drop.classList.add('over');}));
  ['dragleave','drop'].forEach(t=>drop.addEventListener(t,e=>{e.preventDefault(); drop.classList.remove('over');}));
  drop.addEventListener('drop',e=>handle(e.dataTransfer.files[0]));
  $('#tpl').onclick=()=>{location.href='/api/template.csv';};
  $('#smp').onclick=async()=>{try{await api('/api/sample',{method:'POST'}); await afterData(); msg.className='ok-msg'; msg.textContent='Sample data loaded. Tap “See my dashboard” below.';}catch(ex){msg.className='err'; msg.textContent=ex.message;}};
}
function savedMsg(el,label,n){el.className='ok-msg'; el.textContent='Saved '+label+'. '+(n<3?'Add '+(3-n)+' more month'+(3-n>1?'s':'')+' to unlock the forecast, or tap “See my dashboard” below.':'Tap “See my dashboard” below when you are ready, or add another month.');}
function panelManual(p){
  const t=new Date(), dm=t.getFullYear()+'-'+String(t.getMonth()+1).padStart(2,'0');
  p.innerHTML=`<h4>Enter a bill</h4><div class="s">Add one month at a time from your paper bill. Adding the same month again updates it.</div>
  <form id="mf" novalidate><div class="row"><div class="f"><label for="mm">Billing month</label><input id="mm" name="m" type="month" value="${dm}"></div>
  <div class="f"><label for="mu">Units consumed (kWh)</label><input id="mu" name="u" type="number" min="0" step="any" inputmode="decimal" placeholder="33"></div>
  <div class="f"><label for="ma">Bill amount (₹)</label><input id="ma" name="a" type="number" min="0" step="any" inputmode="decimal" placeholder="360"></div></div>
  <details class="more"><summary>Appliance split (optional)</summary><div class="row" style="margin-top:12px">${Object.keys(APN).map(k=>`<div class="f"><label>${APN[k]} (units)</label><input name="${k}" type="number" min="0" step="any" inputmode="decimal"></div>`).join('')}</div></details>
  <p class="err" id="mmsg" role="alert"></p><button class="btn auto" type="submit">Add to my data</button></form>`;
  $('#mf').addEventListener('submit',async e=>{e.preventDefault(); const f=new FormData(e.target), msg=$('#mmsg'); msg.className='err'; msg.textContent='';
    if(!f.get('m')){msg.textContent='Pick a billing month.';return;} if(f.get('u')===''){msg.textContent='Enter the units consumed.';return;} if(f.get('a')===''){msg.textContent='Enter the bill amount.';return;}
    const ap={}; for(const k of Object.keys(APN)) if(f.get(k)!=='') ap[k]=f.get(k);
    try{const r=await api('/api/bills',{method:'POST',body:{month:f.get('m'),units:f.get('u'),amount:f.get('a'),appliances:ap,source:'Manual entry'}});
      await afterData(); e.target.elements.u.value=''; e.target.elements.a.value=''; savedMsg(msg,r.month_label,r.months);}
    catch(ex){msg.textContent=ex.message;}});
}
function panelOCR(p){
  p.innerHTML=`<h4>Upload a photo of your bill</h4><div class="s">The server tries to read the billing month, units and amount from the photo (Tesseract OCR). Always check the values before saving.</div>
  <div class="photo"><div><label class="drop" id="pdrop" tabindex="0" style="min-width:200px;padding:26px 16px"><b>Choose a photo</b><div class="sub">JPG or PNG</div><input id="pf" type="file" accept="image/*" hidden></label><img id="pimg" alt="Your bill photo" hidden style="margin-top:12px"></div>
  <form id="of" novalidate style="flex:1;min-width:230px"><p class="sub" id="ost" role="status">Pick a photo to begin.</p>
  <div class="row"><div class="f"><label for="om">Billing month</label><input id="om" name="m" type="month"></div><div class="f"><label for="ou">Units consumed</label><input id="ou" name="u" type="number" min="0" step="any"></div><div class="f"><label for="oa">Bill amount (₹)</label><input id="oa" name="a" type="number" min="0" step="any"></div></div>
  <p class="err" id="omsg" role="alert"></p><button class="btn auto" type="submit">Confirm &amp; add</button></form></div>`;
  $('#pdrop').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault(); $('#pf').click();}});
  $('#pf').addEventListener('change',async e=>{const f=e.target.files[0]; e.target.value=''; if(!f) return; const st=$('#ost'), em=$('#omsg'); em.textContent='';
    if(!f.type.startsWith('image/')){em.textContent='Please choose an image file.';return;}
    const img=$('#pimg'); img.src=URL.createObjectURL(f); img.hidden=false; st.textContent='Reading your bill…';
    try{const fd=new FormData(); fd.append('image',f); const r=await api('/api/ocr',{method:'POST',body:fd});
      if(r.m) $('#om').value=r.m; if(r.u!=null) $('#ou').value=r.u; if(r.a!=null) $('#oa').value=r.a;
      st.textContent=r.found?'Here is what I found. Please check each value, then confirm.':'I couldn’t find the values in this photo. Please type them from the picture.';
    }catch(ex){st.textContent=ex.message;}});
  $('#of').addEventListener('submit',async e=>{e.preventDefault(); const f=new FormData(e.target), msg=$('#omsg'); msg.className='err'; msg.textContent='';
    if(!f.get('m')){msg.textContent='Pick the billing month.';return;} if(f.get('u')===''){msg.textContent='Enter the units consumed.';return;} if(f.get('a')===''){msg.textContent='Enter the bill amount.';return;}
    try{const r=await api('/api/bills',{method:'POST',body:{month:f.get('m'),units:f.get('u'),amount:f.get('a'),source:'Bill photo'}}); await afterData(); savedMsg(msg,r.month_label,r.months);}
    catch(ex){msg.textContent=ex.message;}});
}
const PANELS={csv:panelCSV,manual:panelManual,ocr:panelOCR};
function pick(k){$$('.opt').forEach(o=>o.classList.toggle('sel',o.dataset.opt===k)); const p=$('#panel'); PANELS[k](p); $('#pickhint').hidden=true; p.hidden=false; p.classList.remove('show'); void p.offsetWidth; p.classList.add('show');}
function resetAdd(){$$('.opt').forEach(o=>o.classList.remove('sel')); const p=$('#panel'); p.hidden=true; p.innerHTML=''; p.classList.remove('show'); $('#pickhint').hidden=false;}
$$('.opt').forEach(o=>{o.tabIndex=0; o.setAttribute('role','button'); o.addEventListener('click',()=>pick(o.dataset.opt)); o.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault(); pick(o.dataset.opt);}});});

/* ---------- dashboard: the server sends the numbers, this only draws them ---------- */
function tween(el,a,b,f,ms=900){const t0=performance.now(); (function s(n){const p=Math.min(1,(n-t0)/ms),k=1-Math.pow(1-p,3); el.textContent=f(a+(b-a)*k); if(p<1) requestAnimationFrame(s);})(t0);}
let VIEW={f:null}, simShown={a:0,s:0}, simSeq=0, simTimer=0;
function buildChart(pts){
  const W=600,H=220,P=30,n=pts.length,mx=Math.max(10,Math.ceil(Math.max(...pts.map(p=>p.v))*1.15/5)*5),x=i=>n>1?P+i*(W-2*P)/(n-1):W/2,y=v=>H-34-(v/mx)*(H-64);
  const q=pts.map((p,i)=>[x(i),y(p.v)]), hasF=pts[n-1].fc, k=hasF?n-1:n; let d=`M${q[0][0]},${q[0][1]}`;
  for(let i=1;i<k;i++){const mx2=(q[i-1][0]+q[i][0])/2,my2=(q[i-1][1]+q[i][1])/2; d+=` Q${q[i-1][0]},${q[i-1][1]} ${mx2},${my2}`;} if(k>1) d+=` L${q[k-1][0]},${q[k-1][1]}`;
  let g=''; [0,mx/2,mx].forEach(v=>g+=`<line class="gl" x1="${P}" x2="${W-P}" y1="${y(v)}" y2="${y(v)}"/><text class="tx" x="2" y="${y(v)+4}">${Math.round(v)}</text>`);
  let t=''; pts.forEach((p,i)=>t+=`<text class="tx" x="${x(i)}" y="${H-8}" text-anchor="middle">${esc(p.label)}</text>`);
  let s=g; if(k>1) s+=`<path class="ar" d="${d} L${q[k-1][0]},${y(0)} L${q[0][0]},${y(0)}Z"/><path class="ln" id="lp" d="${d}"/>`;
  if(hasF&&k>=1) s+=`<path class="fc" d="M${q[k-1][0]},${q[k-1][1]} L${q[n-1][0]},${q[n-1][1]}"/><circle cx="${q[n-1][0]}" cy="${q[n-1][1]}" r="6" fill="var(--acc)"/>`;
  pts.forEach((p,i)=>{if(p.an) s+=`<circle cx="${q[i][0]}" cy="${q[i][1]}" r="7" fill="var(--warn)"/>`; else if(!p.fc&&n<=8) s+=`<circle cx="${q[i][0]}" cy="${q[i][1]}" r="3.5" fill="var(--acc)"/>`;});
  $('#chart').innerHTML=s+t;}
async function render(){
  let d; try{d=await api('/api/dashboard');}catch(e){return;}
  const f=d.forecast; VIEW.f=f;
  $('#bm').textContent=d.bill.month; $('#bu').textContent=d.bill.units+' units'; $('#ba').textContent='₹'+d.bill.amount; $('#bs').textContent=d.source;
  const bp=$('#bpill'); bp.textContent=d.sample?'Sample data':'Your data'; bp.className='pill '+(d.sample?'warn':'ok');
  if(f){$('#hl').textContent='NEXT MONTH FORECAST · '+f.month.toUpperCase(); $('#cur').hidden=false; $('#amt').textContent=f.amount;
    $('#hs').innerHTML='≈ <b>'+f.units+' units</b> · likely range '+f.lo+'–'+f.hi+', from your last '+f.months_used+' months';
    $('#rl1').textContent=f.lo+' units'; $('#rl2').textContent=f.units+' (predicted)'; $('#rl3').textContent=f.hi+' units'; $('#rbw').hidden=false; $('#rb').style.width='28%';}
  else{$('#hl').textContent='NEXT MONTH FORECAST'; $('#cur').hidden=true; $('#amt').textContent='—'; $('#hs').textContent='Add at least 3 months of bills to unlock the forecast.'; $('#rbw').hidden=true;}
  $('#m1v').textContent=d.usage.value; $('#m1p').textContent=d.usage.label; $('#m1p').className='pill '+d.usage.tone;
  $('#m2v').textContent=d.anomaly.value; $('#m2p').textContent=d.anomaly.label; $('#m2p').className='pill '+d.anomaly.tone;
  if(d.top_appliance){$('#m3v').textContent=d.top_appliance.name; $('#m3p').textContent=d.top_appliance.label;} else{$('#m3v').textContent='—'; $('#m3p').textContent='No data';}
  buildChart(d.chart.points);
  $('#cnote').className='note'+(d.chart_note.ok?' okn':''); $('#cnt').textContent=d.chart_note.text;
  const box=$('#apl');
  if(d.appliances){$('#apsub').textContent=d.appliances.subtitle; box.innerHTML=d.appliances.items.map(i=>`<div class="ap"><span>${esc(i.name)}</span><div><i data-w="${i.pct}"></i></div><em>${i.pct}%</em></div>`).join('');}
  else{$('#apsub').textContent='Not available for this data'; box.innerHTML='<p class="empty">No appliance data yet. Add columns like ac_units and fridge_units to your CSV, or fill the optional appliance split when adding a bill by hand.</p>';}
  const sim=d.simulator;
  if(sim.enabled){$('#sapp').innerHTML=sim.appliances.map(a=>`<option value="${esc(a.key)}">${esc(a.name)}</option>`).join(''); $('#simctl').hidden=false; $('#simres').hidden=false; $('#simmsg').hidden=true; simShown={a:f.amount,s:0}; upSim(true);}
  else{$('#simctl').hidden=true; $('#simres').hidden=true; $('#simmsg').hidden=false; $('#simmsg').textContent=sim.message;}
  $('#recs').innerHTML=d.recommendations.map(r=>`<div class="rec"><b>${esc(r.title)}</b>${esc(r.text)}</div>`).join('');
  if(cur==='dashboard') animateIn();}
async function upSim(init){
  if(!VIEW.f||$('#simctl').hidden) return; const pc=+$('#sp').value, my=++simSeq;
  try{const r=await api('/api/simulate',{method:'POST',body:{appliance:$('#sapp').value,pct:pc}}); if(my!==simSeq) return; const ms=init?1:350;
    tween($('#sa'),simShown.a,r.amount,v=>'₹'+Math.round(v),ms); tween($('#ss'),simShown.s,r.savings,v=>(v>=0?'₹'+Math.round(v):'-₹'+Math.abs(Math.round(v)))+' / month',ms); simShown={a:r.amount,s:r.savings};}
  catch(e){}}
function animateIn(){const f=VIEW.f;
  if(f){tween($('#amt'),0,f.amount,v=>Math.round(v),1200); $('#rb').style.width='0%'; setTimeout(()=>$('#rb').style.width='28%',250);}
  $$('.ap i').forEach(i=>{i.style.width='0%'; setTimeout(()=>i.style.width=i.dataset.w+'%',300);});
  const lp=$('#lp'); if(lp){const L=lp.getTotalLength(); lp.style.transition='none'; lp.style.strokeDasharray=L; lp.style.strokeDashoffset=L; lp.getBoundingClientRect(); lp.style.transition='stroke-dashoffset 1.5s ease'; lp.style.strokeDashoffset=0;}}
function runDash(){animateIn();}
$('#sapp').addEventListener('change',()=>upSim());
$('#sp').addEventListener('input',()=>{const pc=+$('#sp').value; $('#spl').textContent=(pc>0?'+':'')+pc+'% usage'; clearTimeout(simTimer); simTimer=setTimeout(()=>upSim(),80);});

/* Watt chatbot */
const CHIPS={login:["What can I do here?","Do I need an account?","Is my data safe?"],
 'add-bill':["Which option should I pick?","What does my CSV need?","What if OCR misreads?"],
 dashboard:["How is the forecast made?","What's the anomaly flag?","How do I use the simulator?"]};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const DOTS='<span class="dots"><span></span><span></span><span></span></span>';
function say(t,who){const m=document.createElement('div'); m.className='m '+who; m.textContent=t; $('#msgs').appendChild(m); $('#msgs').scrollTop=1e5; return m;}
async function ask(q){ if(!q.trim()) return; say(q,'me'); const d=say('','bot'); d.innerHTML=DOTS; let r;
  try{r=await api('/api/chat',{method:'POST',body:{message:q,section:cur}});}catch(e){r={reply:'Sorry — I couldn’t reach the server. Please try again in a moment.'};}
  await sleep(500); d.textContent=r.reply; $('#msgs').scrollTop=1e5; if(r.action==='open_dashboard') setTimeout(()=>go('dashboard'),500);}
async function botSay(t){const d=say('','bot'); d.innerHTML=DOTS; await sleep(850); d.textContent=t; $('#msgs').scrollTop=1e5; await sleep(380);}
function renderChips(list){const c=$('#chips'); c.innerHTML=''; const L=list||CHIPS[cur];
  L.forEach((q,i)=>{const b=document.createElement('button'); b.className='chip'; b.type='button'; b.textContent=q; b.style.setProperty('--d',i*.08+'s'); b.onclick=()=>ask(q); c.appendChild(b);});
  const e=document.createElement('button'); e.className='chip ex'; e.type='button'; e.textContent=cur==='dashboard'?'Explain this dashboard':'Explain this page'; e.style.setProperty('--d',L.length*.08+'s'); e.onclick=()=>ask(e.textContent); c.appendChild(e);}
const INTRO_CHIPS=["What is Smart Energy Advisor?","What can you do?","How do I get started?","Is my data safe?","Show me the dashboard"];
let introStarted=false;
async function intro(){ if(introStarted) return; introStarted=true;
  await botSay("Hi, welcome! I'm Watt ⚡ — your guide to Smart Energy Advisor.");
  await botSay("I can help you forecast next month's bill, spot unusual usage and find simple ways to save.");
  await botSay("Tap an option below, or just type your question.");
  renderChips(INTRO_CHIPS); introPhase=false;}
function setOpen(o,focus){$('#chat').classList.toggle('open',o); $('#fab').classList.add('seen'); if(o&&focus) setTimeout(()=>$('#cin').focus({preventScroll:true}),350);}
$('#fab').addEventListener('click',()=>{const o=!$('#chat').classList.contains('open'); setOpen(o,true); if(o) intro();});
$('#cx').addEventListener('click',()=>setOpen(false));
$('#cform').addEventListener('submit',e=>{e.preventDefault(); const v=$('#cin').value; $('#cin').value=''; ask(v);});
/* guided tour: Watt's floating coach marks, the rest of the screen stays blurred */
const TOURS={
 login:[
  {tgt:'#fab',t:"Hi, I'm Watt ⚡",p:"I'm your guide to Smart Energy Advisor. Log in, or continue as a guest, and I'll unlock the next page for you.",b:['got']},
  {tgt:'#loginForm',t:"Log in",p:"Log in to keep your bills saved, or just continue as a guest.",b:['got','try'],act:()=>{const i=$('#loginForm input'); if(i) i.focus({preventScroll:true});}}],
 'add-bill':[
  {tgt:'#fab',t:"You're in! 🎉",p:"Now let's add your bill. I'll show you the three ways to do it.",b:['got']},
  {tgt:'#o-csv',t:"CSV Upload",p:"Got a spreadsheet of past bills? Upload it here. Best when you have several months.",b:['got','try'],act:()=>pick('csv')},
  {tgt:'#o-manual',t:"Manual Entry",p:"Just one paper bill? Type the month, units and amount. It takes seconds.",b:['got','try'],act:()=>{pick('manual'); setTimeout(()=>{const i=$('#panel input'); if(i) i.focus({preventScroll:true});},60);}},
  {tgt:'#o-ocr',t:"Bill Photo (OCR)",p:"Snap a photo of your bill and I'll read the details. You can correct anything before saving.",b:['got','try'],act:()=>pick('ocr')},
  {tgt:'#toDash',t:"Open your dashboard",p:"Once your data is in, tap this button and your dashboard unlocks.",b:['got']}],
 dashboard:[
  {tgt:'#fab',t:"Here's your dashboard",p:"Everything below is calculated from the bills you added.",b:['got']},
  {tgt:'#dashboard .hero',t:"Your forecast",p:"Next month's predicted bill and its likely range, built from your bill history.",b:['got']},
  {tgt:()=>$('#sapp').closest('.card'),t:"What-if simulator",p:"Pick an appliance, drag the slider and watch your bill and savings change instantly.",b:['got','try'],act:()=>{const s=$('#sp'); if(s&&!s.closest('[hidden]')) s.focus({preventScroll:true});}},
  {tgt:'#fab',t:"You're all set 🎉",p:"I'm always here. Tap me, type any question, or hit “Explain this dashboard”.",b:['done']}]};
let STEPS=TOURS.login, grp='login', tourOff=false; const toured={};
const dim=$('#dim'), ring=$('#ring'), tip=$('#tip'), root=document.documentElement;
let ti=0,tok=0,spotEl=null,curEl=null;
const lockUI=on=>{root.classList.toggle('lock',on); $$('main,header.top,#fab,#chat').forEach(e=>e.inert=on);};
const clearSpot=()=>{if(spotEl){spotEl.classList.remove('spot'); spotEl=null;}};
const elOf=s=>typeof s.tgt==='function'?s.tgt():$(s.tgt);
const radOf=(el,r)=>{const v=getComputedStyle(el).borderTopLeftRadius; return v.includes('%')?parseFloat(v)/100*Math.min(r.width,r.height):(parseFloat(v)||0);};
function holePath(r,p,q0){const W=root.clientWidth,H=innerHeight,x=r.left-p,y=r.top-p,w=r.width+2*p,h=r.height+2*p,q=Math.min(q0,w/2,h/2);
  return `path(evenodd,"M0 0H${W}V${H}H0Z M${x+q} ${y}H${x+w-q}A${q} ${q} 0 0 1 ${x+w} ${y+q}V${y+h-q}A${q} ${q} 0 0 1 ${x+w-q} ${y+h}H${x+q}A${q} ${q} 0 0 1 ${x} ${y+h-q}V${y+q}A${q} ${q} 0 0 1 ${x+q} ${y}Z")`;}
async function settle(el){let same=0,lt=NaN,ll=NaN; for(let i=0;i<40&&same<3;i++){await sleep(70); const r=el.getBoundingClientRect(); same=(Math.abs(r.top-lt)<.5&&Math.abs(r.left-ll)<.5)?same+1:0; lt=r.top; ll=r.left;}}
function mk(label,cls,fn){const b=document.createElement('button'); b.type='button'; b.className='btn '+cls; b.textContent=label; b.onclick=fn; return b;}
function place(r){
  const W=root.clientWidth,H=innerHeight,m=12,g=16,tw=tip.offsetWidth,th=tip.offsetHeight; let side,x,y;
  if(H-r.bottom-g-m>=th) side='b'; else if(r.top-g-m>=th) side='t'; else if(W-r.right-g-m>=tw) side='r'; else if(r.left-g-m>=tw) side='l'; else side='n';
  if(side==='b'||side==='t'){x=Math.min(Math.max(m,r.left+r.width/2-tw/2),W-tw-m); y=side==='b'?r.bottom+g:r.top-g-th; tip.style.setProperty('--ax',Math.min(Math.max(22,r.left+r.width/2-x),tw-22)+'px');}
  else if(side==='r'||side==='l'){y=Math.min(Math.max(m,r.top+r.height/2-th/2),H-th-m); x=side==='r'?r.right+g:r.left-g-tw; tip.style.setProperty('--ay',Math.min(Math.max(22,r.top+r.height/2-y),th-22)+'px');}
  else {x=Math.max(m,(W-tw)/2); y=(r.top+r.height/2>H/2)?72:H-th-m-76;}
  tip.style.left=x+'px'; tip.style.top=y+'px'; tip.classList.add(side);
}
function layout(){
  const s=STEPS[ti], r=curEl.getBoundingClientRect(), p=8, rad=radOf(curEl,r)+p;
  dim.style.clipPath=holePath(r,p,rad);
  Object.assign(ring.style,{left:r.left-p+'px',top:r.top-p+'px',width:r.width+2*p+'px',height:r.height+2*p+'px',borderRadius:rad+'px'}); ring.classList.add('on');
  $('#tt').textContent=s.t; $('#tp').textContent=s.p; $('#tcount').textContent=(ti+1)+' / '+STEPS.length;
  const ta=$('#ta'); ta.innerHTML='';
  s.b.forEach(k=>{if(k==='got') ta.appendChild(mk('Got it','',nextStep)); if(k==='try') ta.appendChild(mk('Try it','try',tryIt)); if(k==='done') ta.appendChild(mk('Start exploring','try',endTour));});
  if(!s.b.includes('done')){const k=document.createElement('button'); k.type='button'; k.className='skip'; k.textContent='Skip tour'; k.onclick=skipTour; ta.appendChild(k);}
  tip.classList.remove('b','t','l','r','n'); place(r); tip.classList.add('on'); ta.firstChild.focus({preventScroll:true});
}
async function showStep(i){
  const my=++tok; ti=i; curEl=elOf(STEPS[i]);
  tip.classList.remove('on'); ring.classList.remove('on'); dim.style.clipPath='none';
  if(getComputedStyle(curEl).position!=='fixed') curEl.scrollIntoView({behavior:'smooth',block:'center'});
  await sleep(120); await settle(curEl); if(my!==tok) return;
  layout();
}
const nextStep=()=>{ if(ti<STEPS.length-1) showStep(ti+1); else endTour(); };
function hideTour(){dim.classList.remove('on'); tip.classList.remove('on'); ring.classList.remove('on'); lockUI(false);}
function tryIt(){const s=STEPS[ti]; tok++; hideTour(); clearSpot(); if(s.act) s.act(); spotEl=curEl; spotEl.classList.add('spot'); $('#resume').classList.add('on'); setTimeout(clearSpot,7000);}
function resumeTour(){$('#resume').classList.remove('on'); clearSpot(); dim.classList.add('on'); lockUI(true); showStep(Math.min(ti+1,STEPS.length-1));}
function endTour(){tok++; hideTour(); $('#resume').classList.remove('on'); clearSpot(); $('#fab').classList.remove('hold'); go(grp);}
const skipTour=()=>{tourOff=true; endTour();};
function maybeTour(g){ if(tourOff||toured[g]) return; toured[g]=true; startTour(g); }
function startTour(g){grp=TOURS[g]?g:'login'; STEPS=TOURS[grp]; setOpen(false); $('#resume').classList.remove('on'); clearSpot(); if(grp==='login') window.scrollTo({top:0,behavior:'instant'}); $('#fab').classList.add('hold'); dim.classList.add('on'); lockUI(true); showStep(0);}
$('#rgo').onclick=resumeTour; $('#rx').onclick=skipTour; $('#retour').onclick=()=>startTour(cur);
addEventListener('resize',()=>{if(tip.classList.contains('on')) layout();});
addEventListener('keydown',e=>{if(e.key==='Escape'&&dim.classList.contains('on')) skipTour();});
addEventListener('load',()=>setTimeout(()=>{toured.login=true; startTour('login');},500));


/* ---------- start-up: ask the server who is logged in ---------- */
(async function init(){
  renderAuth(); renderLogin(); updateNav(); updateGate();
  $$('#nav a').forEach(a=>a.addEventListener('click',e=>{e.preventDefault(); go(a.getAttribute('href').slice(1));}));
  try{applyMe(await api('/api/me'));}catch(e){}
  renderAuth(); renderLogin(); updateNav(); updateGate(); if(dataReady) await render();
})();
'''
