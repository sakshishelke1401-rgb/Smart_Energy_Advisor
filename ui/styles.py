"""All the CSS of the page (colours, layout, animations, dark mode, the guided tour). Served at /assets/app.css."""

CSS = r''':root{
  --bg:#EAF5EF; --panel:#FFFFFF; --panel2:#F3FAF6; --ink:#0A1F17; --sub:#4F665B; --line:rgba(10,31,23,.1);
  --acc:#49E09B; --accd:#DDF5E8; --acct:#1C8F5E; --warn:#D9A82B; --warnd:#FBF1D6; --glow:.55;
  --head:'Epilogue',system-ui,sans-serif; --body:'DM Sans',system-ui,sans-serif;
  box-sizing:border-box; padding-top:env(safe-area-inset-top,0px); padding-bottom:env(safe-area-inset-bottom,0px);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){--bg:#07130F; --panel:#0F1F19; --panel2:#0B1813; --ink:#E8F4EE; --sub:#93AB9F; --line:rgba(255,255,255,.11); --accd:#12392A; --acct:#49E09B; --warnd:#3D3212; --glow:.28;}
}
:root[data-theme="dark"]{--bg:#07130F; --panel:#0F1F19; --panel2:#0B1813; --ink:#E8F4EE; --sub:#93AB9F; --line:rgba(255,255,255,.11); --accd:#12392A; --acct:#49E09B; --warnd:#3D3212; --glow:.28;}
*{box-sizing:border-box;}
html{scroll-behavior:smooth; scroll-snap-type:y proximity; scroll-padding-top:env(safe-area-inset-top,0px);}
body{margin:0; background:var(--bg); color:var(--ink); font:400 16px/1.55 var(--body);}

/* animated background */
.bg{position:fixed; inset:0; z-index:-2; overflow:hidden; background:var(--bg);}
.blob{position:absolute; filter:blur(70px); opacity:var(--glow); background:radial-gradient(circle at 30% 30%,var(--c1),var(--c2) 70%);}
.b1{--c1:#6EEBAE; --c2:#49E09B; width:50vw; height:50vw; left:-14vw; top:-16vw; animation:m1 14s ease-in-out infinite,d1 22s ease-in-out infinite;}
.b2{--c1:#C7F2D9; --c2:#8FE0B8; width:38vw; height:38vw; right:-10vw; top:4vw; animation:m2 17s ease-in-out infinite,d2 26s ease-in-out infinite;}
.b3{--c1:#F7EFB0; --c2:#F2DD8A; width:42vw; height:42vw; left:18vw; bottom:-20vw; animation:m1 19s ease-in-out infinite reverse,d3 24s ease-in-out infinite;}
@keyframes m1{0%,100%{border-radius:42% 58% 63% 37%/41% 44% 56% 59%;}50%{border-radius:63% 37% 41% 59%/58% 46% 54% 42%;}}
@keyframes m2{0%,100%{border-radius:58% 42% 36% 64%/55% 48% 52% 45%;}50%{border-radius:39% 61% 61% 39%/44% 60% 40% 56%;}}
@keyframes d1{50%{transform:translate(4vw,6vw) scale(1.08);}}
@keyframes d2{50%{transform:translate(-5vw,4vw) scale(1.1);}}
@keyframes d3{50%{transform:translate(3vw,-5vw) scale(1.06);}}

/* top bar */
.top{position:fixed; top:0; left:0; right:0; z-index:40; display:flex; flex-wrap:wrap; gap:8px 20px; justify-content:space-between; align-items:center;
  padding:calc(12px + env(safe-area-inset-top,0px)) 28px 12px; background:color-mix(in srgb,var(--bg) 72%,transparent); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);}
.brand{display:flex; align-items:center; gap:10px; font:900 20px var(--head); color:var(--ink); text-decoration:none;}
.brand svg{width:26px; height:26px;}
nav{display:flex; gap:6px;}
nav a{padding:8px 16px; border-radius:22px; font-weight:600; font-size:15px; color:var(--sub); text-decoration:none; transition:background .2s,color .2s;}
nav a.on{background:var(--accd); color:var(--acct);}

.screen{min-height:100vh; scroll-snap-align:start; max-width:1160px; margin:0 auto; padding:104px 28px 64px; position:relative;}
[data-r]{opacity:0; transform:translateY(24px); transition:opacity .7s var(--e,ease),transform .7s ease; transition-delay:var(--d,0s);}
[data-r].in{opacity:1; transform:none;}
.eyebrow{display:inline-block; background:var(--accd); color:var(--acct); font-weight:600; font-size:14px; padding:6px 14px; border-radius:20px;}
h1,h2,h3,h4{font-family:var(--head); margin:0;}
h1{font-weight:900; letter-spacing:-.02em; line-height:1.08; font-size:clamp(34px,5vw,56px);}
h2{font-weight:900; font-size:clamp(28px,3.6vw,38px); letter-spacing:-.01em; margin:14px 0 8px;}
.lead{font-size:18px; color:var(--sub); max-width:520px; margin:14px 0 0;}
.card{background:var(--panel); border:1.5px solid var(--line); border-radius:22px; padding:26px;}
.btn{display:inline-flex; justify-content:center; align-items:center; gap:8px; width:100%; background:var(--ink); color:var(--bg); border:0; border-radius:14px; padding:14px 22px; font:600 16px var(--body); cursor:pointer; transition:transform .15s;}
.btn:hover{transform:translateY(-2px);}
.btn.ghost{background:transparent; color:var(--ink); border:1.5px solid var(--line); margin-top:10px;}
.btn.auto{width:auto;}
.pill{font-size:12.5px; padding:4px 11px; border-radius:20px; font-weight:600; white-space:nowrap;}
.pill.ok{background:var(--accd); color:var(--acct);} .pill.warn{background:var(--warnd); color:var(--warn);}

/* login */
.login{display:grid; grid-template-columns:1.1fr 1fr; gap:48px; align-items:center; min-height:calc(100vh - 190px);}
.mwrap{width:min(300px,70vw); margin-bottom:22px;}
.mascot{width:100%; height:auto; display:block;}
.mbg{fill:var(--accd);}
.lcard label{display:block; font-weight:600; font-size:14.5px; color:var(--sub); margin-top:16px;}
.lcard input{display:block; width:100%; margin-top:6px; padding:13px 14px; border:1.5px solid var(--line); border-radius:12px; background:var(--panel2); color:var(--ink); font:400 16px var(--body);}
.lcard input:focus{outline:2px solid var(--acc); border-color:transparent;}
.lcard .btn{margin-top:22px;} .lcard .btn.ghost{margin-top:10px;}
.small{font-size:14.5px; color:var(--sub); text-align:center; margin:16px 0 0;} .small a{color:var(--acct); font-weight:600;}
.hint{position:absolute; left:50%; bottom:22px; transform:translateX(-50%); color:var(--sub); font-weight:600; font-size:14px; text-decoration:none; animation:bob 1.8s ease-in-out infinite;}
@keyframes bob{50%{transform:translate(-50%,6px);}}
@keyframes blink{0%,92%,100%{transform:scaleY(1);}96%{transform:scaleY(.1);}}
.eye{animation:blink 4.5s infinite; transform-box:fill-box; transform-origin:center; transition:transform .18s ease;}
#mpL,#mpR{transition:opacity .15s;}
#mascot.shut .eye{animation:none; transform:scaleY(.09);}
#mascot.shut #mpL,#mascot.shut #mpR{opacity:0;}

/* add bill */
.opts{display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:28px;}
.opt{background:var(--panel); border:1.5px solid var(--line); border-radius:22px; padding:26px 22px; cursor:pointer; display:flex; flex-direction:column; gap:12px; transition:transform .2s,border-color .2s,background .2s;}
.opt:hover{transform:translateY(-4px); border-color:var(--acc);}
.opt.sel{border-color:var(--acc); background:var(--accd);}
.ib{width:52px; height:52px; border-radius:15px; background:var(--accd); color:var(--acct); display:flex; align-items:center; justify-content:center;}
.opt.sel .ib{background:var(--panel);}
.opt h3{font-size:19px;} .opt p{margin:0; color:var(--sub); font-size:15px; flex:1;} .opt .t{font-size:13px; font-weight:600; color:var(--acct);}
.panel{margin-top:22px; background:var(--panel); border:1.5px solid var(--line); border-radius:22px; padding:28px;}
.panel h4{font-size:19px; margin-bottom:4px;} .panel .s{color:var(--sub); font-size:15px; margin-bottom:18px;}
.drop{border:2px dashed var(--line); border-radius:16px; padding:34px 18px; text-align:center; color:var(--sub); background:var(--panel2);}
.drop b{color:var(--ink);}
.row{display:flex; gap:14px; flex-wrap:wrap; margin-bottom:14px;}
.f{flex:1; min-width:170px;} .f label{display:block; font-size:14px; font-weight:600; color:var(--sub); margin-bottom:6px;}
.f input{width:100%; padding:12px 14px; border:1.5px solid var(--line); border-radius:12px; background:var(--panel2); color:var(--ink); font:400 16px var(--body);}
.pbox{display:flex; gap:18px; align-items:center; flex-wrap:wrap;}
.pb{width:110px; height:110px; border-radius:16px; border:2px dashed var(--line); display:flex; align-items:center; justify-content:center; color:var(--sub); background:var(--panel2);}
.next{margin-top:22px; display:flex; justify-content:flex-end;}

/* dashboard */
.sub{color:var(--sub); font-size:15px;}
.g{display:grid; gap:16px; margin-top:16px;}
.g2{grid-template-columns:1.4fr 1fr;} .g-h{grid-template-columns:1.3fr 1fr;}
.billrow{display:flex; align-items:center; gap:20px; flex-wrap:wrap; margin-top:14px;}
.billrow .ic{width:58px; height:58px; border-radius:14px; background:var(--accd); color:var(--acct); display:flex; align-items:center; justify-content:center;}
.kv{display:flex; gap:28px; flex-wrap:wrap; flex:1;} .kv small{display:block; color:var(--sub); font-size:13px;} .kv b{font:700 18px var(--head);}
.hero{display:flex; flex-direction:column; justify-content:space-between; gap:16px; background:linear-gradient(160deg,var(--panel),var(--accd));}
.big{font:900 58px/1 var(--head); letter-spacing:-.02em; margin-top:8px;} .big small{font:500 18px var(--body); color:var(--sub); margin-left:8px;}
.bar{height:8px; border-radius:5px; background:var(--accd); overflow:hidden; position:relative;} .bar i{position:absolute; top:0; bottom:0; left:36%; width:0; background:var(--acc); border-radius:5px; transition:width 1.1s cubic-bezier(.2,.7,.2,1);}
.lab{display:flex; justify-content:space-between; font-size:13px; color:var(--sub); margin-top:6px;}
.minis{display:flex; flex-direction:column; gap:12px;}
.mini{background:var(--panel); border:1.5px solid var(--line); border-radius:18px; padding:16px 18px; display:flex; justify-content:space-between; align-items:center;}
.mini small{display:block; color:var(--sub); font-size:13.5px;} .mini b{font:700 20px var(--head);}
.chart svg{width:100%; height:auto; display:block;}
.ln{fill:none; stroke:var(--acc); stroke-width:3.2; stroke-linecap:round;} .fc{fill:none; stroke:var(--acc); stroke-width:3; stroke-dasharray:6 6;}
.ar{fill:var(--acc); opacity:.12;} .gl{stroke:var(--line);} .tx{fill:var(--sub); font:12px var(--body);}
.note{margin-top:12px; padding:12px 14px; border-radius:12px; background:var(--warnd); font-size:14.5px; display:flex; gap:10px;}
.note i{width:8px; height:8px; border-radius:50%; background:var(--warn); margin-top:8px; flex-shrink:0;}
.ap{display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid var(--line); font-size:15px;} .ap:last-child{border:0;}
.ap span:first-child{width:118px; flex-shrink:0;} .ap em{font-style:normal; width:40px; text-align:right; color:var(--sub); font-size:14px;}
.ap div{flex:1; height:8px; background:var(--accd); border-radius:5px; overflow:hidden;} .ap div i{display:block; height:100%; width:0; background:var(--acc); border-radius:5px; transition:width 1.1s cubic-bezier(.2,.7,.2,1);}
.sim{display:flex; gap:18px; align-items:center; flex-wrap:wrap; margin-top:12px;}
select{background:var(--panel2); color:var(--ink); border:1.5px solid var(--line); border-radius:12px; padding:11px 14px; font:400 16px var(--body);}
.sl{flex:1; min-width:200px;} input[type=range]{width:100%; accent-color:var(--acc);}
.sl div{display:flex; justify-content:space-between; font-size:13px; color:var(--sub);}
.res{display:flex; gap:34px; margin-top:18px; flex-wrap:wrap;} .res small{display:block; color:var(--sub); font-size:14px;} .res b{font:900 28px var(--head);} .res .sv b{color:var(--acct);}
.recs{display:flex; flex-direction:column; gap:10px; margin-top:12px;}
.rec{padding:14px 16px; border-radius:14px; background:var(--panel2); border:1px solid var(--line); font-size:15.5px;} .rec b{display:block; color:var(--acct); font-size:14px; margin-bottom:2px;}
.foot{margin-top:26px; text-align:center; color:var(--sub); font-size:14px;}

/* Watt chatbot */
[hidden]{display:none !important;}
:root{--bad:#C0392B;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bad:#FF8A7A;}}
:root[data-theme="dark"]{--bad:#FF8A7A;}
.auth{display:flex; align-items:center; gap:8px; font-size:14px; font-weight:600; color:var(--sub);}
.auth b{color:var(--ink);} .auth button{background:none; border:1.5px solid var(--line); color:var(--ink); border-radius:18px; padding:5px 12px; font:600 13.5px var(--body); cursor:pointer;}
.top nav{margin-left:auto;} @media (max-width:860px){.top nav{margin-left:0;}}
.err{color:var(--bad); font-size:14.5px; min-height:22px; margin:10px 0 0;}
.ok-msg{color:var(--acct); font-weight:600; font-size:15px; min-height:22px; margin:10px 0 0;}
.drop{display:block; cursor:pointer; transition:border-color .2s,background .2s;} .drop.over,.drop:hover,.drop:focus-visible{border-color:var(--acc); background:var(--accd); outline:none;}
.photo{display:flex; gap:22px; flex-wrap:wrap; align-items:flex-start;} .photo img{width:150px; max-height:210px; object-fit:cover; border-radius:14px; border:1.5px solid var(--line);}
details.more{margin:6px 0 14px;} details.more summary{cursor:pointer; font-weight:600; color:var(--acct); font-size:15px;}
.mini-link{color:var(--acct); font-weight:600; font-size:14.5px; background:none; border:0; cursor:pointer; text-decoration:underline; padding:0;}
.linkrow{display:flex; gap:20px; flex-wrap:wrap; margin-top:14px;}
.empty{color:var(--sub); font-size:15px; margin:8px 0;}
.note.okn{background:var(--accd);} .note.okn i{background:var(--acc);}

.next{align-items:center; gap:16px; flex-wrap:wrap;}
.panel.show{animation:mi .35s ease both;}
.btn:disabled{opacity:.45; cursor:not-allowed; transform:none;}
nav a.locked{opacity:.4; cursor:not-allowed;}
/* guided tour: spotlight + floating coach marks */
html.lock{overflow:hidden;}
.dim{position:fixed; inset:0; z-index:90; background:color-mix(in srgb,var(--bg) 38%,transparent); backdrop-filter:blur(6px); -webkit-backdrop-filter:blur(6px); opacity:0; pointer-events:none; transition:opacity .35s,clip-path .5s cubic-bezier(.2,.8,.2,1);}
.dim.on{opacity:1; pointer-events:auto;}
.ring{position:fixed; z-index:91; border:3px solid var(--acc); pointer-events:none; opacity:0; transition:opacity .3s;}
.ring.on{opacity:1;}
.ring::after{content:""; position:absolute; inset:-3px; border-radius:inherit; animation:rp 1.8s ease-out infinite;}
@keyframes rp{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--acc) 55%,transparent);}100%{box-shadow:0 0 0 20px transparent;}}
.tip{position:fixed; z-index:92; left:0; top:0; width:min(340px,calc(100vw - 24px)); background:var(--panel); border:1.5px solid var(--acc); border-radius:20px; padding:16px 18px 14px; box-shadow:0 24px 60px -18px rgba(0,0,0,.5); opacity:0; transform:translateY(8px) scale(.97); pointer-events:none; transition:opacity .3s,transform .3s;}
.tip.on{opacity:1; transform:none; pointer-events:auto;}
.tip::before{content:""; position:absolute; width:14px; height:14px; background:var(--panel); border:1.5px solid var(--acc); transform:rotate(45deg); left:var(--ax,50%); margin-left:-7px;}
.tip.b::before{top:-8px; border-right:0; border-bottom:0;}
.tip.t::before{bottom:-8px; border-left:0; border-top:0;}
.tip.r::before{left:-8px; margin-left:0; top:var(--ay,50%); margin-top:-7px; border-top:0; border-right:0;}
.tip.l::before{left:auto; right:-8px; margin-left:0; top:var(--ay,50%); margin-top:-7px; border-left:0; border-bottom:0;}
.tip.n::before{display:none;}
.th{display:flex; align-items:center; gap:10px; margin-bottom:8px;} .th svg{width:30px; height:30px; flex-shrink:0;}
.th b{font:700 15px var(--head);} .th small{margin-left:auto; color:var(--sub); font-size:13px; font-weight:600;}
.tip h4{font:900 20px/1.25 var(--head); margin:0 0 6px;} .tip p{margin:0; font-size:16px; line-height:1.5;}
.ta{display:flex; gap:10px; margin-top:14px; align-items:center; flex-wrap:wrap;}
.ta .btn{width:auto; padding:10px 20px; font-size:15px;} .btn.try{background:var(--acc); color:#06130D;}
.skip{margin-left:auto; background:none; border:0; color:var(--sub); font:600 14px var(--body); cursor:pointer; text-decoration:underline; padding:4px 2px;}
.resume{position:fixed; left:24px; bottom:calc(24px + env(safe-area-inset-bottom,0px)); z-index:70; display:flex; align-items:center; gap:6px; background:var(--ink); color:var(--bg); border-radius:30px; padding:8px 8px 8px 20px; font-weight:600; font-size:15px; opacity:0; transform:translateY(20px); pointer-events:none; transition:opacity .3s,transform .3s;}
.resume.on{opacity:1; transform:none; pointer-events:auto;}
.resume .btn{width:auto; padding:9px 16px; font-size:14.5px; background:var(--acc); color:#06130D;}
.resume #rx{background:none; border:0; color:inherit; cursor:pointer; font-size:17px; padding:6px 10px;}
.spot{border-radius:22px; outline:3px solid var(--acc); outline-offset:6px; animation:spot 1.6s ease-out 4;}
@keyframes spot{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--acc) 55%,transparent);}100%{box-shadow:0 0 0 24px transparent;}}
.rt{margin-left:auto; background:var(--panel); border:1.5px solid var(--line); color:var(--ink); border-radius:16px; padding:6px 12px; font:600 13.5px var(--body); cursor:pointer;} .rt:hover{border-color:var(--acc);}
.fab.hold{animation:none;}
@media (max-width:860px){.resume{left:14px;}}

.fab{position:fixed; right:22px; bottom:calc(22px + env(safe-area-inset-bottom,0px)); z-index:60; width:68px; height:68px; border-radius:50%; background:var(--panel); border:2px solid var(--acc); cursor:pointer; box-shadow:0 12px 30px -10px rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; animation:fl 3s ease-in-out infinite;}
@keyframes fl{50%{transform:translateY(-6px);}}
.fab svg{width:44px; height:44px;} .fab::after{content:""; position:absolute; inset:-2px; border-radius:50%; border:2px solid var(--acc); animation:ring 2.4s ease-out infinite;}
.fab.seen::after{display:none;}
@keyframes ring{from{transform:scale(1); opacity:.7;}to{transform:scale(1.5); opacity:0;}}
.chat{position:fixed; right:22px; bottom:calc(104px + env(safe-area-inset-bottom,0px)); z-index:60; width:370px; max-width:calc(100vw - 32px); height:min(580px,calc(100vh - 140px)); display:flex; flex-direction:column; background:var(--panel); border:1px solid var(--line); border-radius:22px; box-shadow:0 24px 60px -18px rgba(0,0,0,.45); overflow:hidden; transform:translateY(18px) scale(.96); opacity:0; pointer-events:none; transition:transform .28s cubic-bezier(.2,.8,.2,1),opacity .25s;}
.chat.open{transform:none; opacity:1; pointer-events:auto;}
.ch{display:flex; align-items:center; gap:12px; padding:14px 16px; background:var(--accd);} .ch svg{width:38px; height:38px;}
.ch .x{margin-left:auto; width:34px; height:34px; border-radius:50%; border:0; background:transparent; color:var(--ink); font-size:24px; line-height:1; cursor:pointer;} .ch .x:hover{background:var(--panel);}
.ch b{font:700 17px var(--head); display:block;} .ch small{color:var(--acct); font-size:13px;}
.msgs{flex:1; overflow-y:auto; padding:16px; display:flex; flex-direction:column; gap:10px;}
.m{max-width:86%; padding:11px 14px; border-radius:16px; font-size:15px; line-height:1.5; animation:mi .3s ease both;}
@keyframes mi{from{opacity:0; transform:translateY(8px);}}
.m.bot{background:var(--panel2); border:1px solid var(--line); border-bottom-left-radius:4px; align-self:flex-start;}
.m.me{background:var(--acc); color:#06130D; border-bottom-right-radius:4px; align-self:flex-end; font-weight:500;}
.dots span{display:inline-block; width:7px; height:7px; margin:0 2px; border-radius:50%; background:var(--sub); animation:dt 1s infinite;} .dots span:nth-child(2){animation-delay:.15s;} .dots span:nth-child(3){animation-delay:.3s;}
@keyframes dt{0%,60%,100%{transform:translateY(0);opacity:.4;}30%{transform:translateY(-5px);opacity:1;}}
.chips{padding:4px 14px 10px; display:flex; flex-wrap:wrap; gap:8px;}
.chip{background:var(--panel); border:1.5px solid var(--line); border-radius:18px; padding:8px 13px; font:500 14px var(--body); color:var(--ink); cursor:pointer; transition:border-color .15s,background .15s; animation:mi .35s ease both; animation-delay:var(--d,0s);}
.chip:hover{border-color:var(--acc); background:var(--accd);} .chip.ex{background:var(--accd); border-color:var(--acc); color:var(--acct); font-weight:600;}
.inp{display:flex; gap:8px; padding:12px 14px; border-top:1px solid var(--line);}
.inp input{flex:1; padding:11px 14px; border:1.5px solid var(--line); border-radius:22px; background:var(--panel2); color:var(--ink); font:400 15.5px var(--body); min-width:0;}
.inp input:focus{outline:2px solid var(--acc); border-color:transparent;}
.inp button{width:44px; height:44px; border-radius:50%; border:0; background:var(--acc); color:#06130D; cursor:pointer; display:flex; align-items:center; justify-content:center;}

@media (max-width:860px){
  .login,.g2,.g-h,.opts{grid-template-columns:1fr;} .login{gap:28px;}
  .screen{padding:118px 18px 60px;} .top{padding-left:16px; padding-right:16px;} .brand{font-size:17px;} nav a{padding:6px 12px; font-size:14px;}
  .chat{right:12px; max-width:calc(100vw - 24px);} .fab{right:14px;}
}
@media (prefers-reduced-motion:reduce){
  *,.blob,.fab,.fab::after,.hint{animation:none !important; transition:none !important;} [data-r]{opacity:1; transform:none;} html{scroll-behavior:auto;}
}
'''
