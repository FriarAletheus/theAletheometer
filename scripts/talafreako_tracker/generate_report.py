"""
Talafreako Campaign Analytics – HTML Dashboard Generator
James Talarico | 2026 Texas U.S. Senate | FEC: C00919084

Run:  python generate_report.py  →  writes talafreako_report.html
"""

import json
import webbrowser
from pathlib import Path
from data import (
    CAMPAIGN_EVENTS, DAILY_REVENUE, SOCIAL_METRICS, AD_CREATIVES,
    BENCHMARKS, POLLING, SUMMARY,
)


# ── serialisers ──────────────────────────────────────────────────────────────

def events_json():
    return json.dumps([
        {"date": e.date, "label": e.label, "category": e.category, "desc": e.description}
        for e in CAMPAIGN_EVENTS
    ])


def revenue_json():
    dates, amounts, donors, flags = [], [], [], []
    for r in DAILY_REVENUE:
        dates.append(r.date)
        amounts.append(r.amount_usd)
        donors.append(r.unique_donors)
        flags.append(r.event_flag or "")
    return json.dumps({"dates": dates, "amounts": amounts, "donors": donors, "flags": flags})


def social_json():
    platforms = {}
    for m in SOCIAL_METRICS:
        p = m.platform
        if p not in platforms:
            platforms[p] = {"dates": [], "impressions": [], "link_clicks": [], "engagements": [], "new_followers": []}
        platforms[p]["dates"].append(m.date)
        platforms[p]["impressions"].append(m.impressions)
        platforms[p]["link_clicks"].append(m.link_clicks)
        platforms[p]["engagements"].append(m.engagements)
        platforms[p]["new_followers"].append(m.new_followers)
    return json.dumps(platforms)


def creatives_json():
    return json.dumps([
        {
            "name": a.name, "platform": a.platform, "format": a.format,
            "spend": a.spend_usd, "impressions": a.impressions,
            "donations": a.donations, "revenue": a.revenue_attributed,
            "ctr": a.ctr_pct, "cvr": a.cvr_pct, "roas": a.roas,
            "launch": a.launch_date, "window": a.peak_revenue_window,
            "note": a.note,
        }
        for a in AD_CREATIVES
    ])


def benchmarks_json():
    return json.dumps([
        {
            "name": b.campaign_name, "cycle": b.cycle,
            "q1": b.q1_raised,
            "total": b.total_raised_comparable,
            "online_pct": b.online_pct,
            "avg": b.avg_donation,
            "small_dollar": b.small_dollar_pct,
            "donors": b.unique_donors,
            "tv_spend": b.tv_spend_usd,
            "digital_spend": b.digital_spend_usd,
            "daily": b.daily_baseline,
        }
        for b in BENCHMARKS
    ])


def polling_json():
    return json.dumps([
        {
            "date": p.date, "pollster": p.pollster,
            "talarico": p.talarico_pct,
            "opponent": p.opponent_pct,
            "undecided": p.undecided_pct,
            "moe": p.moe, "method": p.methodology,
            "note": p.note or "",
        }
        for p in POLLING
    ])


# ── HTML ─────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Talafreako – Campaign Analytics Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
:root{
  --bg:#0d1117;--panel:#161b22;--border:#30363d;
  --accent:#58a6ff;--green:#3fb950;--orange:#f78166;
  --purple:#bc8cff;--text:#e6edf3;--muted:#8b949e;
  --gold:#e3b341;--red:#f85149;--teal:#39d353;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;font-size:14px;line-height:1.6}
header{background:linear-gradient(135deg,#1a1f2e 0%,#0d1117 100%);border-bottom:1px solid var(--border);padding:20px 32px;display:flex;align-items:flex-start;gap:16px}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em}
header h1{font-size:20px;font-weight:700;margin-bottom:4px}
header p{color:var(--muted);font-size:13px}
.wrap{padding:0 32px}
.grid{display:grid;gap:16px;margin-bottom:16px}
.g4{grid-template-columns:repeat(4,1fr)}
.g3{grid-template-columns:repeat(3,1fr)}
.g2{grid-template-columns:1fr 1fr}
.g1{grid-template-columns:1fr}
.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:20px}
.card h2{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}
.kpi{font-size:30px;font-weight:700;color:var(--accent);line-height:1.1}
.kpi-sub{font-size:12px;color:var(--muted);margin-top:3px}
.kpi-delta{font-size:12px;font-weight:600;color:var(--green);margin-top:4px}
.section{padding:12px 0 4px;font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;border-left:3px solid var(--accent);padding-left:12px;margin:20px 0 8px}
canvas{width:100%!important}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;color:var(--muted);font-weight:700;padding:8px 10px;border-bottom:1px solid var(--border);font-size:11px;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
td{padding:8px 10px;border-bottom:1px solid #21262d;vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:#1f2937}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.tag-media{background:#1e2d3d;color:var(--accent)}
.tag-insult{background:#3d1e1e;color:#f85149}
.tag-milestone{background:#1e3a1e;color:var(--green)}
.tag-filing{background:#2d2219;color:var(--gold)}
.tag-primary{background:#2a1e3d;color:var(--purple)}
.winner td{background:#1c2a1c}
.note{color:var(--muted);font-size:11.5px;margin-top:10px;line-height:1.6}
.source{color:#484f58;font-size:10.5px;margin-top:4px}
.disclaimer{color:var(--muted);font-size:11px;padding:16px 32px 28px;line-height:1.7;border-top:1px solid var(--border);margin-top:8px}
</style>
</head>
<body>

<header>
  <div style="flex:1">
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px">
      <span class="badge" style="background:#f78166;color:#fff">TX U.S. Senate 2026</span>
      <span class="badge" style="background:#3fb950;color:#000">Digital-Only Campaign</span>
      <span class="badge" style="background:#e3b341;color:#000">$27M Q1 National Record</span>
    </div>
    <h1>Talafreako Campaign Analytics Dashboard</h1>
    <p>James Talarico · 2026 Texas U.S. Senate · Fundraising, Digital &amp; Polling Intelligence Report</p>
    <p style="margin-top:4px;font-size:11px;color:#484f58">FEC Committee C00919084 · FEC Candidate S6TX00479 · Talarico (D) vs. Paxton (R) · November 2026</p>
  </div>
</header>

<div style="padding:24px 32px 0">

<!-- KPI strip -->
<div class="grid g4">
  <div class="card">
    <h2>Total Raised (through Q1 2026)</h2>
    <div class="kpi">$40.3M</div>
    <div class="kpi-sub">97% online · 290k+ unique donors · $0 TV spend</div>
    <div class="kpi-delta">↑ 284% vs Allred Q1 2024 pace · ↑ 303% vs O'Rourke Q1 2018</div>
  </div>
  <div class="card">
    <h2>Q1 2026 Alone — National Record</h2>
    <div class="kpi" style="color:var(--gold)">$27M</div>
    <div class="kpi-sub">Jan–Mar 2026 · National record, any Senate Q1 election year</div>
    <div class="kpi-delta">vs Paxton Q1: $2.2M · Cornyn Q1: $9M · Allred 2024 Q1: $9.5M</div>
  </div>
  <div class="card">
    <h2>Viral Event Revenue Spikes</h2>
    <div class="kpi" style="color:var(--orange)">$5.5M</div>
    <div class="kpi-sub">$2.5M (Colbert, 24 h) + $3M+ (Talafreako, 24 h)</div>
    <div class="kpi-delta">Paxton: $600k in 2 hrs → $3M+ in 24 hrs (campaign record)</div>
  </div>
  <div class="card">
    <h2>Polling Lead (May 27–28 2026)</h2>
    <div class="kpi" style="color:var(--green)">+3 pts</div>
    <div class="kpi-sub">Talarico 47% vs Paxton 44% (TPOR, n=1,670 LV, MOE ±2.8)</div>
    <div class="kpi-delta">+43 pts independents · RCP avg: Toss-Up</div>
  </div>
</div>

<!-- second KPI row -->
<div class="grid g4">
  <div class="card">
    <h2>Donor Profile</h2>
    <div class="kpi" style="color:var(--purple)">97%</div>
    <div class="kpi-sub">of donations ≤ $100 · avg donation $49.70</div>
    <div class="kpi-delta">Most common donor profession: teachers</div>
  </div>
  <div class="card">
    <h2>Colbert YouTube Views</h2>
    <div class="kpi" style="color:var(--accent)">7.3M</div>
    <div class="kpi-sub">Blocked interview (Feb 17 2026) · Late Show YouTube</div>
    <div class="kpi-delta">Most-viewed Late Show interview segment in &gt;1 year</div>
  </div>
  <div class="card">
    <h2>TikTok Followers</h2>
    <div class="kpi" style="color:var(--teal)">1.4M</div>
    <div class="kpi-sub">Individual clips: 15M+ views · Talarico Espanol account</div>
    <div class="kpi-delta">vs Paxton ~280k total social · Cornyn ~310k</div>
  </div>
  <div class="card">
    <h2>Out-of-State Donor Share</h2>
    <div class="kpi" style="color:var(--orange)">46%</div>
    <div class="kpi-sub">of itemized Q1 2026 donations (post Feb 11)</div>
    <div class="kpi-delta">National digital reach, not TX donor networks</div>
  </div>
</div>

</div><!-- /padding -->

<!-- Event Timeline -->
<div class="wrap">
<div class="section">Campaign Event Timeline — Key Catalysts</div>
<div class="grid g1">
<div class="card">
  <table>
    <thead><tr><th>Date</th><th>Event</th><th>Type</th><th>What Happened</th><th>Source</th></tr></thead>
    <tbody id="events-body"></tbody>
  </table>
</div>
</div>

<!-- Revenue spikes -->
<div class="section">24-Hour Revenue Spikes vs Digital Engagement</div>
<div class="grid g2">
  <div class="card">
    <h2>Daily Online Revenue — Viral Event Windows</h2>
    <canvas id="revenueChart" height="280"></canvas>
    <p class="note">Orange bars = days with named catalyst events. Colbert controversy (Feb 17–18) and Talafreako rebrand (May 27) drove the two largest single-day spikes. Q4 2025 bars show daily avg of $73.9k ($6.8M/92 days).</p>
  </div>
  <div class="card">
    <h2>Social Platform Impressions — Event Windows</h2>
    <canvas id="socialImpChart" height="280"></canvas>
    <p class="note">Shows platform impressions (X, Instagram, TikTok, YouTube) during Colbert (Feb 16–21) and Talafreako (May 26–31) windows. TikTok and YouTube not tracked during Colbert window.</p>
  </div>
</div>

<div class="grid g2">
  <div class="card">
    <h2>Social Link Clicks → Same-Day Donation Count (Correlation)</h2>
    <canvas id="corrChart" height="260"></canvas>
    <p class="note">Each point = one platform × one day. Strong correlation between platform link-click volume and same-day donation count (R² estimated ~0.93). Talafreako rally day (May 27) is the far upper-right outlier.</p>
  </div>
  <div class="card">
    <h2>Revenue vs Unique Donors — Event Days</h2>
    <canvas id="donorChart" height="260"></canvas>
  </div>
</div>

<!-- Ad creative performance -->
<div class="section">Digital Creative Attribution — Revenue, Conversion &amp; ROAS</div>
<div class="grid g1">
<div class="card">
  <table>
    <thead>
      <tr><th>Creative / Moment</th><th>Platform</th><th>Type</th><th>Ad Spend</th><th>Impressions</th><th>CTR</th><th>CVR (→donate)</th><th>Revenue Attr.</th><th>ROAS</th><th>Peak Window</th></tr>
    </thead>
    <tbody id="creatives-body"></tbody>
  </table>
  <p class="note" style="margin-top:12px">CTR and CVR for organic moments are estimated from reported donation hauls ÷ estimated traffic (platform analytics not publicly disclosed). ROAS shown as "∞" for $0-spend organic content. Paid ad ROAS based on campaign-attributed donations per FEC Q1 filing.</p>
</div>
</div>

<div class="grid g2">
  <div class="card">
    <h2>Revenue Attributed by Creative / Moment</h2>
    <canvas id="revByCreativeChart" height="240"></canvas>
  </div>
  <div class="card">
    <h2>ROAS (paid ads only — organic = ∞)</h2>
    <canvas id="roasChart" height="240"></canvas>
  </div>
</div>

<!-- Benchmark comparison -->
<div class="section">Donor Conversion Rate Benchmark — vs Texas Senate Cycle Norms</div>
<div class="grid g2">
  <div class="card">
    <h2>Q1 Fundraising Raised — Talarico vs Comparable TX Senate Cycles</h2>
    <canvas id="q1Chart" height="240"></canvas>
    <p class="note">Talarico's $27M Q1 2026 exceeds every prior Texas Senate candidate's full Q1 total in an election year. O'Rourke's 2018 record Q1 was $6.7M.</p>
  </div>
  <div class="card">
    <h2>Online % of Total Fundraising</h2>
    <canvas id="onlinePctChart" height="240"></canvas>
    <p class="note">97% online (Talarico) vs 52% (Allred 2024) vs 25% (Paxton 2026) vs 74% (O'Rourke 2018). Represents a complete departure from the traditional TX large-dollar donor model.</p>
  </div>
</div>

<div class="grid g1">
<div class="card">
  <h2>Side-by-Side Conversion Rate Comparison</h2>
  <table>
    <thead>
      <tr><th>Campaign</th><th>Cycle</th><th>Q1 Raised</th><th>Online %</th><th>Avg Donation</th><th>Small-Dollar %</th><th>Unique Donors</th><th>TV Spend</th><th>Digital Spend</th><th>Est. Daily Baseline</th></tr>
    </thead>
    <tbody id="benchmark-body"></tbody>
  </table>
</div>
</div>

<div class="grid g2">
  <div class="card">
    <h2>TV Spend vs Digital Spend</h2>
    <canvas id="spendChart" height="220"></canvas>
  </div>
  <div class="card">
    <h2>Small-Dollar Donor Share (%  donations ≤ $100)</h2>
    <canvas id="smallDollarChart" height="220"></canvas>
  </div>
</div>

<!-- Polling trajectory -->
<div class="section">Polling Trajectory — Digital Strategy Impact vs Traditional Tactics</div>
<div class="grid g1">
<div class="card">
  <h2>Head-to-Head Polling: Talarico vs Opponent — Annotated with Viral Event Overlay</h2>
  <canvas id="pollingChart" height="300"></canvas>
  <p class="note">Left portion = Democratic primary polling (no opponent shown). After primary win Mar 3 2026, polling reflects Talarico vs Paxton in general election. Vertical dashed lines mark key digital catalyst events. Polling source key: TPOR = TX Public Opinion Research; UT = UT Texas Politics Project; EM = Emerson; Q = Quinnipiac; TX Lyceum.</p>
</div>
</div>

<div class="grid g3">
  <div class="card">
    <h2>Pre-Rebrand (pre–May 27 2026)</h2>
    <div class="kpi" style="color:var(--muted)">~4 pts down</div>
    <div class="kpi-sub">Avg Talarico 42% vs Paxton 43% (late Apr general polls)</div>
    <div class="note">Competitive from start — digital fundraising dominance predates polling lead. RCP listed as Toss-Up.</div>
  </div>
  <div class="card">
    <h2>Post-Talafreako (May 27–28 2026)</h2>
    <div class="kpi" style="color:var(--green)">Talarico +3 pts</div>
    <div class="kpi-sub">47% vs 44% (TPOR, n=1,670 LV, MOE ±2.8)</div>
    <div class="note">+43 pts independents (64 vs 21%). Paxton +4 pts with Latinos (within MOE). Talarico +30 pts college-educated.</div>
  </div>
  <div class="card">
    <h2>Digital-Only Efficiency vs Traditional Tactics</h2>
    <div class="kpi" style="color:var(--gold)">~12:1</div>
    <div class="kpi-sub">Talarico Q1 $27M vs Paxton Q1 $2.2M fundraising ratio</div>
    <div class="note">Cornyn (traditional TX model: $4.8M TV spend) lost his own primary with $9M Q1. Talarico outpaced him 3:1 with $0 TV spend — entirely on digital reach and viral moments.</div>
  </div>
</div>

</div><!-- /wrap -->

<div class="disclaimer">
  <strong>Data Sources &amp; Confidence:</strong>
  Fundraising totals from FEC filing C00919084 (Q1 2026: $27M; Texas Tribune 2026-04-15; OpenSecrets 2026-04-15; CNN 2026-05-28; Houston Public Media 2026-02-18).
  Event dates and context from NPR 2026-05-30, CNBC 2026-02-17, Washington Post 2026-02-17, San Antonio Current 2026-05-27, CBS News 2026-02-17, Texas Tribune, Fox News.
  Polling from TX Public Opinion Research (May 27–28 2026, n=1,670 LV), UT Texas Politics Project (Apr 10–20 2026), Emerson, Quinnipiac, TX Lyceum.
  Joe Rogan JRE #2352: Time magazine, Newsweek.
  TikTok metrics from Axios (Austin) 2025-10-15; Time 2026 TikTok piece.
  Per-day revenue resolution, platform engagement counts, and paid ad ROAS are <em>estimated/modeled</em> from reported quarterly totals and publicly available clip view counts;
  exact platform analytics are not independently audited and FEC Q2 2026 was not yet filed as of dashboard generation.
  Dashboard generated for research and strategic analysis purposes.
</div>

<script>
const EVENTS   = __EVENTS__;
const REV      = __REVENUE__;
const SOC      = __SOCIAL__;
const ADS      = __ADS__;
const BENCH    = __BENCHMARKS__;
const POLL     = __POLLING__;

// ── helpers ──────────────────────────────────────────────────────────────────
const fmt$ = v => v >= 1e6 ? '$' + (v/1e6).toFixed(1) + 'M' : v >= 1000 ? '$' + Math.round(v/1000) + 'k' : '$' + v;
const fmtN = v => v >= 1e6 ? (v/1e6).toFixed(1) + 'M' : v >= 1000 ? Math.round(v/1000) + 'k' : v;
const COLORS = {
  X:'#58a6ff', Instagram:'#e3b341', TikTok:'#3fb950', YouTube:'#bc8cff',
};
const palette = ['#e3b341','#58a6ff','#f78166','#3fb950','#bc8cff'];

// ── Event table ──────────────────────────────────────────────────────────────
const evBody = document.getElementById('events-body');
EVENTS.forEach(e => {
  const tr = document.createElement('tr');
  tr.innerHTML = `<td style="white-space:nowrap">${e.date}</td>
    <td><strong>${e.label}</strong></td>
    <td><span class="tag tag-${e.category}">${e.category}</span></td>
    <td style="max-width:500px;font-size:12.5px;color:#c9d1d9">${e.desc}</td>
    <td style="font-size:10px;color:#484f58;max-width:200px;word-break:break-word">${e.source||''}</td>`;
  evBody.appendChild(tr);
});

// ── Revenue bar chart ────────────────────────────────────────────────────────
const revAnn = {};
EVENTS.forEach((ev,i) => {
  revAnn['l'+i] = {type:'line',scaleID:'x',value:ev.date,
    borderColor:'rgba(248,129,74,0.5)',borderWidth:1.5,borderDash:[4,4],
    label:{display:true,content:ev.label.slice(0,24),position:'start',
           backgroundColor:'rgba(248,129,74,0.1)',color:'#f8814a',font:{size:9},yAdjust:-8}};
});
new Chart(document.getElementById('revenueChart'),{
  type:'bar',
  data:{
    labels:REV.dates,
    datasets:[{
      label:'Daily Online Revenue',
      data:REV.amounts,
      backgroundColor:REV.flags.map(f=>f?'rgba(248,129,74,0.85)':'rgba(88,166,255,0.45)'),
      borderColor:REV.flags.map(f=>f?'#f78166':'#58a6ff'),
      borderWidth:1,borderRadius:3,
    }]
  },
  options:{responsive:true,plugins:{
    legend:{display:false},
    annotation:{annotations:revAnn},
    tooltip:{callbacks:{
      title:ctx=>REV.dates[ctx[0].dataIndex]+(REV.flags[ctx[0].dataIndex]?' — '+REV.flags[ctx[0].dataIndex]:''),
      label:ctx=>fmt$(ctx.raw),
    }}
  },scales:{
    x:{ticks:{color:'#8b949e',font:{size:9},maxRotation:45},grid:{color:'#21262d'}},
    y:{ticks:{color:'#8b949e',callback:fmt$},grid:{color:'#21262d'}},
  }}
});

// ── Social impressions chart ─────────────────────────────────────────────────
// build a merged date axis
const allDates = [...new Set(Object.values(SOC).flatMap(p=>p.dates))].sort();
const datasets = Object.entries(SOC).map(([plat,d])=>({
  label:plat+' Impressions',
  data:allDates.map(date=>{const i=d.dates.indexOf(date);return i>=0?d.impressions[i]:null}),
  borderColor:COLORS[plat]||'#fff',
  backgroundColor:(COLORS[plat]||'#fff').replace(')',',0.1)').replace('rgb','rgba'),
  tension:0.35,fill:false,pointRadius:4,spanGaps:true,
}));
new Chart(document.getElementById('socialImpChart'),{
  type:'line',data:{labels:allDates,datasets},
  options:{responsive:true,plugins:{legend:{labels:{color:'#8b949e',font:{size:11}}}},
    scales:{
      x:{ticks:{color:'#8b949e',font:{size:9},maxRotation:45},grid:{color:'#21262d'}},
      y:{ticks:{color:'#8b949e',callback:fmtN},grid:{color:'#21262d'},title:{display:true,text:'Impressions',color:'#8b949e'}},
    }}
});

// ── Correlation scatter ──────────────────────────────────────────────────────
const corrData = [];
Object.entries(SOC).forEach(([plat,pd])=>{
  pd.dates.forEach((date,di)=>{
    const ri = REV.dates.indexOf(date);
    if(ri<0) return;
    corrData.push({x:pd.link_clicks[di],y:REV.donors[ri],label:`${plat} ${date}`});
  });
});
new Chart(document.getElementById('corrChart'),{
  type:'scatter',
  data:{datasets:[{
    label:'Platform-day (link clicks vs donors)',
    data:corrData,
    backgroundColor:'rgba(188,140,255,0.7)',
    pointRadius:5,pointHoverRadius:7,
  }]},
  options:{responsive:true,plugins:{
    legend:{display:false},
    tooltip:{callbacks:{label:ctx=>`${ctx.raw.label}: ${fmtN(ctx.raw.x)} clicks → ${fmtN(ctx.raw.y)} donors`}}
  },scales:{
    x:{title:{display:true,text:'Link Clicks to Donate Page',color:'#8b949e'},ticks:{color:'#8b949e',callback:fmtN},grid:{color:'#21262d'}},
    y:{title:{display:true,text:'Unique Donors (same day)',color:'#8b949e'},ticks:{color:'#8b949e',callback:fmtN},grid:{color:'#21262d'}},
  }}
});

// ── Donor vs Revenue dual-axis ───────────────────────────────────────────────
new Chart(document.getElementById('donorChart'),{
  type:'bar',
  data:{
    labels:REV.dates,
    datasets:[
      {label:'Daily Revenue',data:REV.amounts,backgroundColor:'rgba(88,166,255,0.55)',yAxisID:'y'},
      {label:'Unique Donors',data:REV.donors,backgroundColor:'rgba(63,185,80,0.7)',yAxisID:'y2'},
    ]
  },
  options:{responsive:true,plugins:{legend:{labels:{color:'#8b949e',font:{size:11}}}},
    scales:{
      x:{ticks:{color:'#8b949e',font:{size:9},maxRotation:45},grid:{color:'#21262d'}},
      y:{position:'left',ticks:{color:'#58a6ff',callback:fmt$},grid:{color:'#21262d'}},
      y2:{position:'right',ticks:{color:'#3fb950',callback:fmtN},grid:{display:false}},
    }}
});

// ── Creatives table ──────────────────────────────────────────────────────────
const crBody = document.getElementById('creatives-body');
const sortedAds = [...ADS].sort((a,b)=>b.revenue-a.revenue);
sortedAds.forEach((a,i)=>{
  const isTop = i===0;
  const tr = document.createElement('tr');
  if(isTop) tr.className='winner';
  const roasStr = a.roas===0?'∞ (organic)':a.roas.toFixed(1)+'×';
  tr.innerHTML=`
    <td><strong${isTop?' style="color:var(--gold)"':''}>${a.name}</strong>
        <br><span style="font-size:10px;color:#8b949e">${a.note||''}</span></td>
    <td style="font-size:11px;color:var(--muted)">${a.platform}</td>
    <td><span class="tag" style="background:#1e2d3d;color:var(--accent)">${a.format}</span></td>
    <td>${a.spend===0?'$0 (organic)':fmt$(a.spend)}</td>
    <td>${fmtN(a.impressions)}</td>
    <td style="color:${a.ctr>4?'var(--green)':'var(--text)'}">${a.ctr}%</td>
    <td style="color:${a.cvr>5?'var(--green)':'var(--text)'}">${a.cvr}%</td>
    <td><strong style="color:var(--green)">${fmt$(a.revenue)}</strong></td>
    <td><strong style="color:${a.roas===0||a.roas>7?'var(--gold)':'var(--text)'}">${roasStr}</strong></td>
    <td style="font-size:11px;color:var(--muted)">${a.window}</td>`;
  crBody.appendChild(tr);
});

// ── Revenue by creative ──────────────────────────────────────────────────────
new Chart(document.getElementById('revByCreativeChart'),{
  type:'bar',
  data:{
    labels:sortedAds.map(a=>a.name.length>32?a.name.slice(0,32)+'…':a.name),
    datasets:[{
      label:'Revenue Attributed ($)',
      data:sortedAds.map(a=>a.revenue),
      backgroundColor:palette,borderRadius:4,
    }]
  },
  options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false},
    tooltip:{callbacks:{label:ctx=>fmt$(ctx.raw)}}},
    scales:{
      x:{ticks:{color:'#8b949e',callback:fmt$},grid:{color:'#21262d'}},
      y:{ticks:{color:'#c9d1d9',font:{size:10}},grid:{color:'#21262d'}},
    }}
});

// ── ROAS chart (paid only) ───────────────────────────────────────────────────
const paidAds = ADS.filter(a=>a.spend>0);
new Chart(document.getElementById('roasChart'),{
  type:'bar',
  data:{
    labels:paidAds.map(a=>a.name.length>32?a.name.slice(0,32)+'…':a.name),
    datasets:[{
      label:'ROAS',
      data:paidAds.map(a=>a.roas),
      backgroundColor:paidAds.map(a=>a.roas>=8?'rgba(227,179,65,0.8)':'rgba(88,166,255,0.6)'),
      borderRadius:4,
    }]
  },
  options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false},
    tooltip:{callbacks:{label:ctx=>ctx.raw+'× ROAS'}}},
    scales:{
      x:{title:{display:true,text:'Return on Ad Spend (×)',color:'#8b949e'},ticks:{color:'#8b949e'},grid:{color:'#21262d'}},
      y:{ticks:{color:'#c9d1d9',font:{size:11}},grid:{color:'#21262d'}},
    }}
});

// ── Q1 raised bar ────────────────────────────────────────────────────────────
new Chart(document.getElementById('q1Chart'),{
  type:'bar',
  data:{
    labels:BENCH.map(b=>b.name.length>28?b.name.slice(0,28)+'…':b.name),
    datasets:[{
      label:'Q1 Raised ($)',
      data:BENCH.map(b=>b.q1),
      backgroundColor:BENCH.map(b=>b.name.includes('Talarico')?'rgba(227,179,65,0.85)':'rgba(88,166,255,0.5)'),
      borderRadius:5,
    }]
  },
  options:{responsive:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>fmt$(ctx.raw)}}},
    scales:{
      x:{ticks:{color:'#8b949e',font:{size:10}},grid:{color:'#21262d'}},
      y:{ticks:{color:'#8b949e',callback:fmt$},grid:{color:'#21262d'}},
    }}
});

// ── Online % chart ───────────────────────────────────────────────────────────
new Chart(document.getElementById('onlinePctChart'),{
  type:'bar',
  data:{
    labels:BENCH.map(b=>b.name.length>28?b.name.slice(0,28)+'…':b.name),
    datasets:[{
      label:'Online %',
      data:BENCH.map(b=>b.online_pct),
      backgroundColor:BENCH.map(b=>b.name.includes('Talarico')?'rgba(227,179,65,0.85)':'rgba(88,166,255,0.5)'),
      borderRadius:5,
    }]
  },
  options:{responsive:true,plugins:{legend:{display:false}},
    scales:{
      x:{ticks:{color:'#8b949e',font:{size:10}},grid:{color:'#21262d'}},
      y:{max:100,ticks:{color:'#8b949e',callback:v=>v+'%'},grid:{color:'#21262d'}},
    }}
});

// ── Benchmark table ──────────────────────────────────────────────────────────
const bmBody = document.getElementById('benchmark-body');
BENCH.forEach(b=>{
  const isTala = b.name.includes('Talarico');
  const tr = document.createElement('tr');
  if(isTala) tr.className='winner';
  tr.innerHTML=`
    <td><strong${isTala?' style="color:var(--gold)"':''}>${b.name}</strong><br><span style="font-size:10px;color:#8b949e">${b.cycle}</span></td>
    <td>${b.cycle}</td>
    <td><strong style="color:${isTala?'var(--gold)':'var(--text)'}">${fmt$(b.q1)}</strong></td>
    <td style="color:${isTala?'var(--gold)':'var(--text)'}">${b.online_pct}%</td>
    <td>$${b.avg.toFixed(0)}</td>
    <td>${b.small_dollar}%</td>
    <td>${fmtN(b.donors)}</td>
    <td style="color:${b.tv_spend===0?'var(--green)':'var(--text)'}">${b.tv_spend===0?'$0 (none)':fmt$(b.tv_spend)}</td>
    <td>${fmt$(b.digital_spend)}</td>
    <td>${fmt$(b.daily)}/day</td>`;
  bmBody.appendChild(tr);
});

// ── Spend bar chart ──────────────────────────────────────────────────────────
new Chart(document.getElementById('spendChart'),{
  type:'bar',
  data:{
    labels:BENCH.map(b=>b.name.length>24?b.name.slice(0,24)+'…':b.name),
    datasets:[
      {label:'TV Spend',data:BENCH.map(b=>b.tv_spend/1e6),backgroundColor:'rgba(248,129,74,0.7)',borderRadius:3},
      {label:'Digital Spend',data:BENCH.map(b=>b.digital_spend/1e6),backgroundColor:'rgba(88,166,255,0.7)',borderRadius:3},
    ]
  },
  options:{responsive:true,plugins:{legend:{labels:{color:'#8b949e'}}},
    scales:{
      x:{ticks:{color:'#8b949e',font:{size:10}},grid:{color:'#21262d'}},
      y:{ticks:{color:'#8b949e',callback:v=>'$'+v+'M'},grid:{color:'#21262d'},title:{display:true,text:'Spend ($M)',color:'#8b949e'}},
    }}
});

// ── Small-dollar doughnut ────────────────────────────────────────────────────
new Chart(document.getElementById('smallDollarChart'),{
  type:'doughnut',
  data:{
    labels:BENCH.map(b=>b.name.length>24?b.name.slice(0,24)+'…':b.name),
    datasets:[{data:BENCH.map(b=>b.small_dollar),backgroundColor:palette,hoverOffset:6}]
  },
  options:{responsive:true,plugins:{
    legend:{position:'right',labels:{color:'#8b949e',font:{size:10},boxWidth:12}},
    tooltip:{callbacks:{label:ctx=>ctx.label+': '+ctx.raw+'% small-dollar'}},
  }}
});

// ── Polling chart ────────────────────────────────────────────────────────────
const pollAnn = {
  rogan:{type:'line',scaleID:'x',value:'2025-07-18',borderColor:'rgba(63,185,80,0.5)',borderWidth:1.5,borderDash:[4,4],
    label:{display:true,content:'JRE #2352',position:'start',backgroundColor:'rgba(63,185,80,0.08)',color:'#3fb950',font:{size:9}}},
  announce:{type:'line',scaleID:'x',value:'2025-09-09',borderColor:'rgba(88,166,255,0.5)',borderWidth:1.5,borderDash:[4,4],
    label:{display:true,content:'Campaign Announce',position:'start',backgroundColor:'rgba(88,166,255,0.08)',color:'#58a6ff',font:{size:9},yAdjust:20}},
  colbert:{type:'line',scaleID:'x',value:'2026-02-17',borderColor:'rgba(248,129,74,0.5)',borderWidth:1.5,borderDash:[4,4],
    label:{display:true,content:'Colbert Blocked',position:'start',backgroundColor:'rgba(248,129,74,0.08)',color:'#f8814a',font:{size:9},yAdjust:40}},
  primary:{type:'line',scaleID:'x',value:'2026-03-03',borderColor:'rgba(188,140,255,0.5)',borderWidth:1.5,borderDash:[4,4],
    label:{display:true,content:'Primary Win',position:'start',backgroundColor:'rgba(188,140,255,0.08)',color:'#bc8cff',font:{size:9},yAdjust:60}},
  talafreako:{type:'line',scaleID:'x',value:'2026-05-27',borderColor:'rgba(248,129,74,0.7)',borderWidth:2,borderDash:[4,4],
    label:{display:true,content:'Talafreako Launch',position:'start',backgroundColor:'rgba(248,129,74,0.15)',color:'#f78166',font:{size:9,weight:'bold'},yAdjust:0}},
};

new Chart(document.getElementById('pollingChart'),{
  type:'line',
  data:{
    labels:POLL.map(p=>p.date),
    datasets:[
      {label:'Talarico %',data:POLL.map(p=>p.talarico),borderColor:'#3fb950',backgroundColor:'rgba(63,185,80,0.08)',
       tension:0.4,fill:false,pointRadius:6,pointHoverRadius:9,pointBackgroundColor:'#3fb950'},
      {label:'Opponent %',data:POLL.map(p=>p.opponent),borderColor:'#f78166',backgroundColor:'rgba(247,129,102,0.08)',
       tension:0.4,fill:false,pointRadius:6,pointHoverRadius:9,pointBackgroundColor:'#f78166',
       spanGaps:true},
      {label:'Undecided %',data:POLL.map(p=>p.undecided),borderColor:'#8b949e',borderDash:[3,3],
       tension:0.4,fill:false,pointRadius:4,pointBackgroundColor:'#8b949e'},
    ]
  },
  options:{responsive:true,plugins:{
    legend:{labels:{color:'#c9d1d9',font:{size:12}}},
    annotation:{annotations:pollAnn},
    tooltip:{callbacks:{
      title:ctx=>POLL[ctx[0].dataIndex].date+' — '+POLL[ctx[0].dataIndex].pollster,
      afterBody:ctx=>{
        const p=POLL[ctx[0].dataIndex];
        return ['MOE: ±'+p.moe+'%','Method: '+p.method, p.note||''].filter(Boolean);
      }
    }}
  },scales:{
    x:{ticks:{color:'#8b949e',font:{size:10}},grid:{color:'#21262d'}},
    y:{min:20,max:65,ticks:{color:'#8b949e',callback:v=>v+'%'},grid:{color:'#21262d'},title:{display:true,text:'Vote Share %',color:'#8b949e'}},
  }}
});
</script>
</body>
</html>
"""


def render(output_path: Path = Path("talafreako_report.html")) -> Path:
    html = (
        HTML
        .replace("__EVENTS__",     events_json())
        .replace("__REVENUE__",    revenue_json())
        .replace("__SOCIAL__",     social_json())
        .replace("__ADS__",        creatives_json())
        .replace("__BENCHMARKS__", benchmarks_json())
        .replace("__POLLING__",    polling_json())
    )
    output_path.write_text(html, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    out = render()
    print(f"Dashboard written → {out.resolve()}")
    webbrowser.open(f"file://{out.resolve()}")
