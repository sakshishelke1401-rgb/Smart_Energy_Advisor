"""The page markup (HTML). Served by app.py at "/". __CSS_URL__ / __JS_URL__ are filled in by ui/__init__.py."""

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Smart Energy Advisor</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E%E2%9A%A1%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@700;900&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="__CSS_URL__">
</head>
<body>
<div class="bg" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div>

<header class="top">
  <a class="brand" href="#login"><svg viewBox="0 0 24 24"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z" fill="#49E09B"/></svg>Smart Energy Advisor</a>
  <nav id="nav"><a href="#login" class="on">Login</a><a href="#add-bill">Add Bill</a><a href="#dashboard">Dashboard</a></nav>
  <div class="auth" id="auth"></div>
</header>

<main>
<!-- 1. LOGIN -->
<section class="screen" id="login">
  <div class="login">
    <div data-r>
      <div class="mwrap">
        <svg class="mascot" id="mascot" viewBox="0 0 400 420" fill="none" aria-label="Friendly lightbulb mascot">
          <circle class="mbg" cx="200" cy="230" r="150"/>
          <rect x="178" y="58" width="44" height="22" rx="5" fill="#2F3B35"/><rect x="183" y="80" width="34" height="7" fill="#2F3B35" opacity=".6"/><rect x="183" y="91" width="34" height="7" fill="#2F3B35" opacity=".6"/>
          <line x1="200" y1="58" x2="200" y2="40" stroke="#2F3B35" stroke-width="5" stroke-linecap="round"/><circle cx="200" cy="34" r="7" fill="#F2C94C"/>
          <path d="M200 104c-50 0-88 38-88 88 0 38 23 62 40 78 9 9 13 18 13 29v6h70v-6c0-11 4-20 13-29 17-16 40-40 40-78 0-50-38-88-88-88z" fill="#F7E7A6"/>
          <rect x="173" y="305" width="54" height="10" rx="2" fill="#B7BDC2"/><rect x="176" y="317" width="48" height="9" rx="2" fill="#9CA3A8"/><rect x="179" y="328" width="42" height="9" rx="2" fill="#B7BDC2"/><rect x="183" y="339" width="34" height="10" rx="3" fill="#7B8186"/>
          <circle class="eye" cx="172" cy="195" r="22" fill="#0A1F17"/><circle class="eye" cx="228" cy="195" r="22" fill="#0A1F17"/>
          <circle id="mpL" cx="172" cy="195" r="9" fill="#F7E7A6"/><circle id="mpR" cx="228" cy="195" r="9" fill="#F7E7A6"/>
          <path d="M178 238Q200 256 222 238" stroke="#0A1F17" stroke-width="6" stroke-linecap="round"/>
          <circle cx="152" cy="220" r="10" fill="#F2A7A0" opacity=".6"/><circle cx="248" cy="220" r="10" fill="#F2A7A0" opacity=".6"/>
        </svg>
      </div>
      <h1>Know your bill<br>before it arrives.</h1>
      <p class="lead">Forecast next month's electricity bill, spot unusual usage, and get tips that actually cut costs.</p>
    </div>
    <div class="card lcard" id="loginForm" data-r style="--d:.15s"></div>
  </div>
  
</section>

<!-- 2. ADD BILL -->
<section class="screen" id="add-bill" hidden>
  <div data-r>
    <span class="eyebrow">⚡ Step 1</span>
    <h2>Add your bill data</h2>
    <p class="lead">Upload a file you already have, type in a reading, or just snap a photo of your bill.</p>
  </div>
  <div class="opts">
    <div class="opt" id="o-csv" data-opt="csv" data-r style="--d:.05s">
      <div class="ib"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><path d="M15 2v5h5M8 13h8M8 17h5"/></svg></div>
      <h3>CSV Upload</h3><p>Already have your bill history in a spreadsheet? Upload it directly.</p><span class="t">✓ Best for bulk history</span>
    </div>
    <div class="opt" id="o-manual" data-opt="manual" data-r style="--d:.12s">
      <div class="ib"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg></div>
      <h3>Manual Entry</h3><p>Type units consumed and bill amount straight from your paper bill.</p><span class="t">✓ No file needed</span>
    </div>
    <div class="opt" id="o-ocr" data-opt="ocr" data-r style="--d:.19s">
      <div class="ib"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3.5"/><path d="M8 5l1.5-2h5L16 5"/></svg></div>
      <h3>Bill Photo (OCR)</h3><p>Upload a photo — we read the units, amount and month automatically.</p><span class="t">✓ Fastest, no typing</span>
    </div>
  </div>
  <p class="sub" id="pickhint" style="text-align:center;margin:20px 0 0;font-size:16px">👆 Choose an option above to get started</p>
  <div class="panel" id="panel" hidden></div>
  <div class="next"><span class="sub" id="toDashHint"></span><button class="btn auto" id="toDash" data-go="dashboard" disabled>See my dashboard ↓</button></div>
</section>

<!-- 3. DASHBOARD -->
<section class="screen" id="dashboard" hidden>
  <div data-r><span class="eyebrow">⚡ Step 2</span><h2>Your energy dashboard</h2></div>

  <div class="card" data-r>
    <h3>Uploaded bill</h3><div class="sub">The latest bill behind your forecast</div>
    <div class="billrow">
      <div class="ic"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><path d="M15 2v5h5M8 13h8M8 17h5M8 9h3"/></svg></div>
      <div class="kv"><div><small>Billing month</small><b id="bm">—</b></div><div><small>Units consumed</small><b id="bu">—</b></div><div><small>Bill amount</small><b id="ba">—</b></div><div><small>Source</small><b id="bs">—</b></div></div>
      <span class="pill ok" id="bpill">Your data</span>
    </div>
  </div>

  <div class="g g-h">
    <div class="card hero" data-r>
      <div><div class="sub" id="hl" style="color:var(--acct);font-weight:600;">NEXT MONTH FORECAST</div>
        <div class="big"><span id="cur">₹</span><span id="amt">0</span><small>predicted bill</small></div>
        <div class="sub" id="hs" style="margin-top:8px;"></div></div>
      <div id="rbw"><div class="bar"><i id="rb"></i></div><div class="lab"><span id="rl1"></span><span id="rl2"></span><span id="rl3"></span></div></div>
    </div>
    <div class="minis" data-r style="--d:.12s">
      <div class="mini"><div><small>This month's usage</small><b id="m1v">—</b></div><span class="pill ok" id="m1p">—</span></div>
      <div class="mini"><div><small>Last flagged anomaly</small><b id="m2v">—</b></div><span class="pill ok" id="m2p">—</span></div>
      <div class="mini"><div><small>Top appliance</small><b id="m3v">—</b></div><span class="pill ok" id="m3p">—</span></div>
    </div>
  </div>

  <div class="g g2">
    <div class="card chart" data-r>
      <h3>Consumption trend</h3><div class="sub">Your recent billing months, with the forecast</div>
      <svg id="chart" viewBox="0 0 600 220" role="img" aria-label="Consumption trend with forecast"></svg>
      <div class="note" id="cnote"><i></i><span id="cnt"></span></div>
    </div>
    <div class="card" data-r style="--d:.12s">
      <h3>Appliance breakdown</h3><div class="sub" id="apsub" style="margin-bottom:6px;"></div><div id="apl"></div>
    </div>
  </div>

  <div class="card" style="margin-top:16px;" data-r>
    <h3>What-if simulator</h3><div class="sub">Change one appliance's usage and see next month's bill update</div>
    <p class="empty" id="simmsg" hidden></p>
    <div class="sim" id="simctl"><select id="sapp" aria-label="Appliance"></select>
      <div class="sl"><input type="range" id="sp" min="-50" max="50" value="-20" aria-label="Usage change percent"><div><span>-50%</span><span id="spl">-20% usage</span><span>+50%</span></div></div></div>
    <div class="res" id="simres"><div><small>Simulated bill</small><b id="sa">—</b></div><div class="sv"><small>Estimated savings</small><b id="ss">—</b></div></div>
  </div>

  <div class="card" style="margin-top:16px;" data-r>
    <h3>Personalized recommendations</h3><div class="sub">Based on your appliance mix and recent usage</div>
    <div class="recs" id="recs"></div>
  </div>
  <div class="foot">Smart Energy Advisor — final-year Data Science field project · all calculations run on the server in Python</div>
</section>

</main>

<!-- Guided tour -->
<div class="dim" id="dim" aria-hidden="true"></div>
<div class="ring" id="ring" aria-hidden="true"></div>
<div class="tip" id="tip" role="dialog" aria-label="Watt's guided tour">
  <div class="th"><svg viewBox="0 0 100 100" fill="none" aria-hidden="true"><circle cx="50" cy="50" r="46" fill="#F7E7A6"/><circle class="eye" cx="38" cy="46" r="7" fill="#0A1F17"/><circle class="eye" cx="62" cy="46" r="7" fill="#0A1F17"/><path d="M40 62Q50 71 60 62" stroke="#0A1F17" stroke-width="3" stroke-linecap="round"/><circle cx="31" cy="58" r="4" fill="#F2A7A0" opacity=".6"/><circle cx="69" cy="58" r="4" fill="#F2A7A0" opacity=".6"/></svg><b>Watt</b><small id="tcount"></small></div>
  <h4 id="tt"></h4><p id="tp" aria-live="polite"></p>
  <div class="ta" id="ta"></div>
</div>
<div class="resume" id="resume"><span>Tour paused</span><button class="btn" id="rgo" type="button">Continue tour →</button><button id="rx" type="button" aria-label="End tour">✕</button></div>

<!-- Watt chatbot -->
<button class="fab" id="fab" aria-label="Chat with Watt">
  <svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="50" r="46" fill="#F7E7A6"/><circle class="eye" cx="38" cy="46" r="7" fill="#0A1F17"/><circle class="eye" cx="62" cy="46" r="7" fill="#0A1F17"/><circle id="fpL" cx="38" cy="46" r="2.8" fill="#F7E7A6"/><circle id="fpR" cx="62" cy="46" r="2.8" fill="#F7E7A6"/><path d="M40 62Q50 71 60 62" stroke="#0A1F17" stroke-width="3" stroke-linecap="round"/><circle cx="31" cy="58" r="4" fill="#F2A7A0" opacity=".6"/><circle cx="69" cy="58" r="4" fill="#F2A7A0" opacity=".6"/></svg>
</button>
<div class="chat" id="chat" role="dialog" aria-label="Watt assistant">
  <div class="ch">
    <svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="50" r="46" fill="#F7E7A6"/><circle cx="38" cy="46" r="7" fill="#0A1F17"/><circle cx="62" cy="46" r="7" fill="#0A1F17"/><path d="M40 62Q50 71 60 62" stroke="#0A1F17" stroke-width="3" stroke-linecap="round"/></svg>
    <div><b>Watt</b><small id="ctx">● Looking at: Login</small></div><button class="rt" id="retour" type="button">↻ Tour</button><button class="x" id="cx" type="button" aria-label="Close chat">×</button>
  </div>
  <div class="msgs" id="msgs" aria-live="polite"></div>
  <div class="chips" id="chips"></div>
  <form class="inp" id="cform"><input id="cin" type="text" placeholder="Ask Watt anything…" autocomplete="off" aria-label="Type your question"><button type="submit" aria-label="Send"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button></form>
</div>

<script src="__JS_URL__"></script>
</body>
</html>
'''
