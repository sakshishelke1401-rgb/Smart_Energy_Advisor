"""Organization dashboard using the same design tokens and components as the main app."""
HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Smart Energy Advisor</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@700;900&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/app.css"></head><body>
<div class="bg" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div>
<header class="top"><a class="brand" href="/">⚡ Smart Energy Advisor</a><nav><a class="on" href="/">Dashboard</a></nav></header>
<main class="screen" style="max-width:1160px;padding-top:112px">
<div data-r><span class="eyebrow">⚡ ORGANIZATION ENERGY INSIGHTS</span><h2>Energy dashboard</h2><p class="lead">Upload and understand electricity consumption across your organization.</p></div>
<section class="card" style="margin-top:22px"><h3>Analyze an organization CSV</h3><p class="sub">Supported organizations include schools, colleges, hospitals, hotels, restaurants, offices and factories.</p><div class="row" style="align-items:center"><input id="csvfile" type="file" accept=".csv,text/csv"><button class="btn auto" id="uploadcsv">Detect and analyze CSV</button></div><div id="detection"></div><div id="status" class="err" role="status"></div></section>
<div id="results" hidden>
<div class="g" id="metrics" data-tour="metrics" style="grid-template-columns:repeat(auto-fit,minmax(190px,1fr))"></div>
<section class="card forecast-card" data-tour="forecast-chart" style="margin-top:16px"><div class="forecast-copy"><span class="eyebrow">MAIN HIGHLIGHT · NEXT MONTH</span><h3>Next month consumption prediction</h3><div class="forecast-number" id="forecastUnits">—</div><p class="sub" id="forecastCost">Predicted units and estimated cost will appear here when the dataset has enough monthly history.</p><small class="sub">Indicative estimate based on department-level linear trends.</small></div><div class="forecast-visual"><svg id="forecastChart" viewBox="0 0 720 260" role="img" aria-label="Historical consumption and next month prediction"></svg></div></section>
<section class="g g2"><div class="card chart" data-tour="departments-chart"><h3>Latest consumption by department</h3><svg id="deptChart" viewBox="0 0 720 330"></svg></div><div class="card chart" data-tour="trend-chart"><h3>Monthly consumption trend</h3><svg id="trendChart" viewBox="0 0 720 330"></svg></div></section>
<section class="g g2"><div class="card chart"><h3>Consumption groups</h3><svg id="clusterChart" viewBox="0 0 720 260"></svg></div><div class="card chart"><h3>Average vs latest consumption</h3><svg id="compareChart" viewBox="0 0 720 350"></svg></div></section>
<section class="card" style="margin-top:16px"><h3>Department details</h3><div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;margin-top:12px"><thead><tr><th>Department</th><th>Latest units</th><th>Average</th><th>Forecast</th><th>Group</th><th>After-hours</th></tr></thead><tbody id="departments"></tbody></table></div></section>
<section class="card" data-tour="alerts" style="margin-top:16px"><h3>Alerts</h3><div id="alerts" class="recs"></div></section>
<section class="card" data-tour="recommendations" style="margin-top:16px"><h3>Personalized recommendations</h3><p class="sub">Recommendations combine your organization type with signals found in the uploaded data.</p><div id="recommendations" class="recs"></div></section>
<section class="card" style="margin-top:16px"><h3>Method notes and data limitations</h3><ul id="notes"></ul></section>
</div></main>
<!-- Watt remains available on the organization dashboard and guides the user through its insights. -->
<button class="watt-fab" id="wattFab" type="button" aria-label="Open Watt dashboard guide">
  <svg viewBox="0 0 100 100" aria-hidden="true">
    <circle cx="50" cy="50" r="45" fill="#F7E7A6" stroke="#17231D" stroke-width="2"/>
    <circle cx="38" cy="45" r="7" fill="#0A1F17"/><circle cx="62" cy="45" r="7" fill="#0A1F17"/>
    <path d="M39 62Q50 72 61 62" fill="none" stroke="#0A1F17" stroke-width="3" stroke-linecap="round"/>
    <path d="M12 64Q2 56 8 43" fill="none" stroke="#F7E7A6" stroke-width="8" stroke-linecap="round"/>
    <circle cx="8" cy="41" r="7" fill="#17231D"/>
    <path d="M88 64Q98 56 92 43" fill="none" stroke="#F7E7A6" stroke-width="8" stroke-linecap="round"/>
    <circle cx="92" cy="41" r="7" fill="#17231D"/>
  </svg>
</button>
<div class="watt-tour-card" id="wattTour" hidden role="dialog" aria-live="polite" aria-label="Watt's dashboard tour">
  <div class="watt-tour-head"><span class="watt-mini">⚡</span><div><b>Watt · Dashboard guide</b><small id="wattCount">Step 1 of 6</small></div><button id="wattClose" type="button" aria-label="Close tour">×</button></div>
  <h3 id="wattTitle">Welcome to your dashboard!</h3><p id="wattText">I'll show you how to understand your organization's energy use.</p>
  <div class="watt-tour-actions"><button class="watt-skip" id="wattSkip" type="button">Skip tour</button><button class="btn auto" id="wattNext" type="button">Next →</button></div>
</div>
<div class="watt-dim" id="wattDim" hidden></div>
<section class="watt-chat" id="wattChat" hidden aria-label="Chat with Watt">
 <header><span class="watt-mini">⚡</span><div><b>Watt</b><small>Dashboard assistant · using your CSV data</small></div><button id="wattReplay" type="button">↻ Replay tour</button><button id="wattChatClose" type="button" aria-label="Close chat">×</button></header>
 <div class="watt-chat-messages" id="wattMessages" aria-live="polite"><div class="watt-msg bot">Hi! I'm Watt. Ask me about the prediction, charts, departments, alerts or recommendations in this dashboard.</div></div>
 <div class="watt-quick"><button type="button" data-q="What is next month's prediction?">Next month prediction</button><button type="button" data-q="Which department uses the most?">Highest department</button><button type="button" data-q="Explain the trend chart">Explain trend</button></div>
 <form id="wattChatForm"><input id="wattQuestion" placeholder="Ask Watt a question…" autocomplete="off" aria-label="Ask Watt a question"><button type="submit">Send</button></form>
</section>
<style>
/* Dashboard motion stays subtle and follows the existing yellow-green theme. */
#results:not([hidden]) .mini,#results:not([hidden]) .chart,#results:not([hidden]) > .card{animation:seaRise .58s cubic-bezier(.2,.75,.25,1) both}
#results:not([hidden]) .mini:nth-child(2){animation-delay:.07s}#results:not([hidden]) .mini:nth-child(3){animation-delay:.14s}#results:not([hidden]) .mini:nth-child(4){animation-delay:.21s}
#results:not([hidden]) .chart:nth-child(2){animation-delay:.12s}
@keyframes seaRise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
#results .ln{stroke-dasharray:1200;stroke-dashoffset:1200;animation:seaDraw 1.35s ease forwards .3s}
@keyframes seaDraw{to{stroke-dashoffset:0}}
.watt-fab{position:fixed;right:24px;bottom:24px;z-index:120;width:72px;height:72px;border-radius:50%;border:2px solid var(--acc);background:var(--panel);box-shadow:0 12px 32px #10251b35;display:grid;place-items:center;cursor:pointer;animation:wattFloat 3s ease-in-out infinite}
.watt-fab svg{width:62px;height:62px;overflow:visible}.watt-fab:hover{transform:scale(1.06)}
@keyframes wattFloat{50%{translate:0 -6px}}
.watt-fab.wave svg path:last-of-type{animation:wattWave .7s ease-in-out 2;transform-origin:92px 64px}
@keyframes wattWave{50%{transform:rotate(-28deg)}}
.watt-tour-card{position:fixed;right:24px;bottom:110px;z-index:122;width:min(360px,calc(100vw - 32px));padding:18px;background:var(--panel);color:var(--ink);border:1.5px solid var(--acc);border-radius:20px;box-shadow:0 20px 55px #10251b40;animation:seaRise .28s ease both}
.watt-tour-card[hidden]{display:none}
.watt-tour-head{display:flex;align-items:center;gap:10px}.watt-mini{width:34px;height:34px;border-radius:50%;background:#F7E7A6;display:grid;place-items:center}.watt-tour-head small{display:block;color:var(--sub);font-size:12px}.watt-tour-head #wattClose{margin-left:auto;border:0;background:transparent;color:var(--sub);font-size:24px;cursor:pointer}
.watt-tour-card h3{font:800 19px var(--head);margin:14px 0 5px}.watt-tour-card p{color:var(--sub);line-height:1.5;margin:0}
.watt-tour-actions{display:flex;align-items:center;gap:12px;margin-top:16px}.watt-tour-actions .btn{width:auto}.watt-skip{border:0;background:transparent;color:var(--sub);text-decoration:underline;cursor:pointer}
.watt-focus{position:relative;z-index:1;outline:3px solid var(--acc)!important;outline-offset:5px;border-radius:18px;animation:wattPulse 1.5s ease-in-out 2}
@keyframes wattPulse{50%{box-shadow:0 0 0 10px #a5d63c30}}

.forecast-card{display:grid;grid-template-columns:minmax(230px,.85fr) minmax(0,1.5fr);gap:20px;align-items:center;background:linear-gradient(120deg,var(--panel),color-mix(in srgb,var(--accd) 55%,var(--panel)));overflow:hidden}
.forecast-copy h3{margin:8px 0}.forecast-number{font:900 clamp(30px,4vw,48px) var(--head);color:var(--acct);margin:8px 0}.forecast-visual svg{width:100%;height:auto;min-height:170px}.forecast-visual .forecast-line{fill:none;stroke:var(--acc);stroke-width:5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1400;stroke-dashoffset:1400;animation:seaDraw 1.5s ease forwards}.forecast-visual .forecast-pred{fill:none;stroke:var(--warn);stroke-width:5;stroke-dasharray:10 9;stroke-linecap:round}
.watt-dim{position:fixed;inset:0;z-index:110;background:#07170f40;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);pointer-events:none}.watt-dim[hidden]{display:none}
.watt-focus{position:relative!important;z-index:111!important;outline:3px solid var(--acc)!important;outline-offset:5px;border-radius:18px;box-shadow:0 0 0 8px #a5d63c35,0 12px 45px #10251b35!important}
.watt-tour-card{z-index:125}
.watt-chat{position:fixed;right:24px;bottom:108px;z-index:124;width:min(390px,calc(100vw - 28px));height:min(560px,calc(100vh - 150px));display:flex;flex-direction:column;background:var(--panel);color:var(--ink);border:1.5px solid var(--acc);border-radius:20px;box-shadow:0 20px 55px #10251b40;overflow:hidden;animation:seaRise .25s ease both}
.watt-chat[hidden]{display:none}.watt-chat header{display:flex;align-items:center;gap:9px;padding:13px;border-bottom:1px solid var(--line)}.watt-chat header small{display:block;color:var(--sub);font-size:11px}.watt-chat header button{border:0;background:transparent;color:var(--sub);cursor:pointer}.watt-chat header #wattReplay{margin-left:auto;text-decoration:underline;font-size:12px}.watt-chat header #wattChatClose{font-size:23px}.watt-chat-messages{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px}.watt-msg{max-width:92%;padding:11px 13px;border-radius:15px;line-height:1.45;font-size:14px;white-space:pre-wrap}.watt-msg.bot{background:var(--panel2);align-self:flex-start}.watt-msg.user{background:var(--accd);align-self:flex-end}.watt-quick{display:flex;gap:6px;flex-wrap:wrap;padding:8px 12px}.watt-quick button{border:1px solid var(--line);background:var(--panel2);color:var(--ink);border-radius:18px;padding:6px 9px;font-size:11px;cursor:pointer}.watt-chat form{display:flex;gap:7px;padding:12px;border-top:1px solid var(--line)}.watt-chat input{min-width:0;flex:1;border:1px solid var(--line);border-radius:22px;padding:10px 13px;background:var(--panel2);color:var(--ink)}.watt-chat form button{border:0;border-radius:22px;padding:0 16px;background:var(--acc);color:var(--ink);font-weight:700;cursor:pointer}
@media(max-width:700px){.forecast-card{grid-template-columns:1fr}.watt-chat{right:12px;bottom:88px}}

@media(max-width:600px){.watt-fab{right:14px;bottom:14px;width:62px;height:62px}.watt-tour-card{right:12px;bottom:88px}}
</style>
<script>
const $=s=>document.querySelector(s); const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function txt(x,y,t,cls='tx',anchor='start'){return `<text x="${x}" y="${y}" class="${cls}" text-anchor="${anchor}">${esc(t)}</text>`}
const colors={bar:'var(--acc)',line:'var(--acc)',secondary:'var(--warn)'}; let CURRENT_ANALYSIS=null;
async function getCsrf(){return fetch('/api/me').then(r=>r.json())}
$('#uploadcsv').onclick=async()=>{const f=$('#csvfile').files[0];if(!f){$('#status').textContent='Choose a CSV file first.';return;}$('#status').textContent='Detecting dataset and validating rows…';try{const me=await getCsrf(),fd=new FormData();fd.append('file',f);if($('#confirmtype'))fd.append('confirm_type',$('#confirmtype').value);const res=await fetch('/api/upload/auto',{method:'POST',headers:{'X-CSRF-Token':me.csrf},body:fd}),d=await res.json();if(!res.ok){if(d.detection){const x=d.detection;$('#detection').innerHTML=`<div class="note"><i></i><span><b>Detected: ${esc(x.dataset_label)}</b> · confidence ${x.confidence}/99<br>${esc(d.error)}<br><label for="confirmtype">Confirm organization type</label><select id="confirmtype">${[['school','School'],['college','College'],['hospital','Hospital'],['hotel','Hotel'],['restaurant','Restaurant'],['office','Office'],['factory','Factory'],['other_organization','Other organization']].map(([v,l])=>`<option value="${v}" ${x.dataset_type===v?'selected':''}>${l}</option>`).join('')}</select><p class="sub">Select the correct type, then upload again.</p></span></div>`;}throw Error(d.error||'Upload failed');}
$('#detection').innerHTML=`<div class="note okn"><i></i><span><b>${esc(d.dataset_label)} detected</b> · ${d.data_quality.rows} rows × ${d.data_quality.columns} columns · quality ${d.data_quality.quality_score}/100</span></div>`;
if(d.route==='household_dashboard'){location.href='/';return;}render(d.analysis);$('#status').textContent='Analysis completed successfully.';if(window.startWattTour)window.startWattTour();
}catch(e){$('#status').textContent=e.message;}};
function render(d){CURRENT_ANALYSIS=d;$('#results').hidden=false;const m=d.summary;$('#metrics').innerHTML=[['Departments',m.departments],['Latest consumption',m.latest_total_units+' units'],['Estimated cost','₹'+Number(m.latest_total_amount).toLocaleString('en-IN')],['Records analyzed',d.records_analyzed]].map(x=>`<div class="mini"><div><small>${x[0]}</small><b>${x[1]}</b></div><span class="pill ok">Dataset</span></div>`).join('');
$('#departments').innerHTML=d.departments.map(x=>`<tr><td>${esc(x.department)}</td><td>${x.latest_units}</td><td>${x.average_units}</td><td>${x.forecast_next_month_units??'Insufficient history'}</td><td><span class="pill ok">${esc(x.consumption_group)}</span></td><td>${x.after_hours_available?x.after_hours_share_pct+'%':'Not supplied'}</td></tr>`).join('');
drawPrediction(d);drawDept(d);drawTrend(d);drawClusters(d);drawCompare(d);
$('#alerts').innerHTML=d.alerts.length?d.alerts.map(x=>`<div class="rec"><b>${esc(x.department)}</b> ${esc(x.message)}</div>`).join(''):'<p class="empty">No significant month-to-month change was detected in the available history.</p>';
$('#recommendations').innerHTML=d.recommendations.length?d.recommendations.map(x=>`<div class="rec"><b>${esc(x.target)} · ${esc(x.basis)}</b><span class="pill ok">${esc(x.priority)}</span><div>${esc(x.recommendation)}</div></div>`).join(''):'<p class="empty">Not enough relevant information to generate recommendations. Add monthly consumption and department/building details.</p>';
$('#notes').innerHTML=d.method_notes.map(x=>`<li>${esc(x)}</li>`).join('');}
function drawPrediction(d){const m=d.summary||{},u=m.forecast_next_month_units,amt=m.forecast_next_month_amount;$('#forecastUnits').textContent=u==null?'Not enough history':Number(u).toLocaleString('en-IN',{maximumFractionDigits:1})+' units';$('#forecastCost').textContent=amt==null?'Add at least 3 months of department readings to unlock the prediction.':'Estimated electricity cost: ₹'+Number(amt).toLocaleString('en-IN',{maximumFractionDigits:2});let months={};(d.departments||[]).forEach(dep=>(dep.history||[]).forEach(r=>months[r.month]=(months[r.month]||0)+Number(r.units||0)));let e=Object.entries(months).sort(),v=e.map(x=>x[1]);if(!v.length){$('#forecastChart').innerHTML=txt(20,50,'Monthly history is not available');return;}let max=Math.max(1,...v,u||0),all=[...v,...(u==null?[]:[u])],pts=all.map((n,i)=>[35+i*650/Math.max(1,all.length-1),220-n/max*175]);let hist=pts.slice(0,v.length);let line=`<polyline class="forecast-line" points="${hist.map(p=>p.join(',')).join(' ')}"/>`;if(u!=null&&pts.length>v.length){line+=`<line x1="${hist[hist.length-1][0]}" y1="${hist[hist.length-1][1]}" x2="${pts[pts.length-1][0]}" y2="${pts[pts.length-1][1]}" class="forecast-pred"/><circle cx="${pts[pts.length-1][0]}" cy="${pts[pts.length-1][1]}" r="8" fill="var(--warn)"/>`;line+=txt(pts[pts.length-1][0],245,'Predicted','tx','middle');}hist.forEach((p,i)=>{if(i===0||i===hist.length-1||i%Math.ceil(hist.length/4)===0)line+=txt(p[0],245,e[i][0],'tx','middle')});$('#forecastChart').innerHTML='<line x1="30" y1="222" x2="690" y2="222" class="gl"/>'+line;}
function drawDept(d){let items=d.departments.slice(0,8),max=Math.max(1,...items.map(x=>x.latest_units)),s='';items.forEach((x,i)=>{let y=28+i*36,w=440*x.latest_units/max;s+=txt(4,y+15,x.department.length>20?x.department.slice(0,19)+'…':x.department);s+=`<rect x="210" y="${y}" width="${w}" height="20" rx="7" fill="${colors.bar}"/>`;s+=txt(220+w,y+15,Number(x.latest_units).toLocaleString(),'tx');});$('#deptChart').innerHTML=s||txt(20,40,'No department data');}
function drawTrend(d){let months={};d.departments.forEach(dep=>(dep.history||[]).forEach(r=>months[r.month]=(months[r.month]||0)+r.units));let e=Object.entries(months).sort(),v=e.map(x=>x[1]);if(!v.length){$('#trendChart').innerHTML=txt(20,40,'No monthly history');return;}let max=Math.max(1,...v),pts=v.map((n,i)=>[40+i*640/Math.max(1,v.length-1),275-n/max*225]);let s='<line x1="40" y1="275" x2="680" y2="275" class="gl"/>';s+=`<polyline class="ln" points="${pts.map(p=>p.join(',')).join(' ')}"/>`;pts.forEach((p,i)=>{s+=`<circle cx="${p[0]}" cy="${p[1]}" r="5" fill="var(--acc)"/>`;if(i===0||i===v.length-1||i%Math.ceil(v.length/5)===0)s+=txt(p[0],305,e[i][0],'tx','middle')});$('#trendChart').innerHTML=s;}
function drawClusters(d){let names=['Low consumption','Medium consumption','High consumption'],counts=names.map(n=>d.clusters.filter(x=>x.group===n).length),max=Math.max(1,...counts);$('#clusterChart').innerHTML=names.map((n,i)=>{let y=35+i*68,w=440*counts[i]/max;return txt(5,y+17,n)+`<rect x="210" y="${y}" width="${w}" height="28" rx="7" fill="var(--acc)"/>`+txt(220+w,y+19,String(counts[i]));}).join('');}
function drawCompare(d){let items=d.departments.slice(0,6),max=Math.max(1,...items.flatMap(x=>[x.average_units,x.latest_units]));$('#compareChart').innerHTML=items.map((x,i)=>{let y=25+i*48,w1=420*x.average_units/max,w2=420*x.latest_units/max;return txt(4,y+14,x.department)+`<rect x="210" y="${y}" width="${w1}" height="12" rx="5" fill="var(--accd)"/><rect x="210" y="${y+17}" width="${w2}" height="12" rx="5" fill="var(--acc)"/>`;}).join('');}
try{const saved=sessionStorage.getItem('sea_enterprise_analysis');if(saved){render(JSON.parse(saved));window.__seaDashboardReady=true;$('#status').textContent=(sessionStorage.getItem('sea_enterprise_type')||'Organization')+' dataset analyzed.';sessionStorage.removeItem('sea_enterprise_analysis');sessionStorage.removeItem('sea_enterprise_type');}}catch(e){$('#status').textContent='Could not restore analysis. Please upload the CSV again.';}
</script>
<script>
(function(){
 const steps=[
  {selector:'#metrics',title:'Your energy at a glance',text:'These four cards show department count, latest electricity use, estimated cost and number of CSV records.'},
  {selector:'[data-tour="forecast-chart"]',title:'Next month prediction · main highlight',text:'This is the main prediction. The large number is the combined next-month units. The solid green line shows recorded months; the dotted yellow segment points to the predicted month. The cost is estimated using the latest average rate.'},
  {selector:'[data-tour="departments-chart"]',title:'Latest consumption by department',text:'Look at the green horizontal bars in THIS chart. Each bar is one department. The longer the bar, the more electricity that department used in the latest month. The department name is written on the left.'},
  {selector:'[data-tour="trend-chart"]',title:'Monthly consumption trend',text:'This is the line chart on the RIGHT. It adds consumption from all departments for each month. A line moving upward means total electricity use is increasing.'},
  {selector:'[data-tour="alerts"]',title:'Energy alerts',text:'This section lists departments where the latest month changed sharply compared with the previous month. Read the department name and the percentage in each alert.'},
  {selector:'[data-tour="recommendations"]',title:'Recommendations based on your CSV',text:'These suggestions combine your organization type with actual readings. Each recommendation names the department and explains which data signal triggered it.'},
  {selector:'#notes',title:'Method notes',text:'This section explains how the calculations work and which information was missing. After the tour, click Watt to ask questions about any chart or result.'}
 ];
 let index=0,active=false,last=null,completed=false;
 const card=document.getElementById('wattTour'),fab=document.getElementById('wattFab'),dim=document.getElementById('wattDim'),chat=document.getElementById('wattChat');
 const title=document.getElementById('wattTitle'),body=document.getElementById('wattText'),count=document.getElementById('wattCount'),next=document.getElementById('wattNext');
 function clear(){if(last){last.classList.remove('watt-focus');last=null;}}
 function show(i){clear();index=i;if(i>=steps.length){finish();return;}const step=steps[i],target=document.querySelector(step.selector);if(!target){show(i+1);return;}last=target;target.classList.add('watt-focus');target.scrollIntoView({behavior:'smooth',block:'center'});title.textContent=step.title;body.textContent=step.text;count.textContent='Step '+(i+1)+' of '+steps.length;next.textContent=i===steps.length-1?'Finish ✓':'Next →';card.hidden=false;dim.hidden=false;fab.classList.add('wave');setTimeout(()=>fab.classList.remove('wave'),1500);}
 function finish(){active=false;completed=true;clear();card.hidden=true;dim.hidden=true;fab.classList.remove('wave');}
 function advance(){if(index===steps.length-1)finish();else show(index+1);}
 window.startWattTour=function(){if(!document.getElementById('results')||document.getElementById('results').hidden)return;active=true;chat.hidden=true;show(0);};
 function addMessage(text,who){const el=document.createElement('div');el.className='watt-msg '+who;el.textContent=text;$('#wattMessages').appendChild(el);$('#wattMessages').scrollTop=$('#wattMessages').scrollHeight;}
 async function askWatt(question){if(!question.trim())return;addMessage(question,'user');$('#wattQuestion').value='';try{const me=await getCsrf();const res=await fetch('/api/enterprise/chat',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':me.csrf},body:JSON.stringify({message:question,analysis:CURRENT_ANALYSIS})});const data=await res.json();if(!res.ok)throw Error(data.error||'Could not contact Watt.');addMessage(data.reply||'I could not prepare an answer.','bot');}catch(err){addMessage(err.message,'bot');}}
 next.addEventListener('click',advance);$('#wattSkip').addEventListener('click',finish);$('#wattClose').addEventListener('click',finish);
 fab.addEventListener('click',()=>{if(active){finish();return;}if(!completed){window.startWattTour();return;}chat.hidden=!chat.hidden;if(!chat.hidden)$('#wattQuestion').focus();});
 $('#wattChatClose').addEventListener('click',()=>chat.hidden=true);$('#wattReplay').addEventListener('click',()=>window.startWattTour());
 $('#wattChatForm').addEventListener('submit',e=>{e.preventDefault();askWatt($('#wattQuestion').value);});
 document.querySelectorAll('.watt-quick [data-q]').forEach(b=>b.addEventListener('click',()=>askWatt(b.dataset.q)));
 if(window.__seaDashboardReady){setTimeout(()=>window.startWattTour(),650);}
})();;
</script>
</body></html>'''
