/**
 * LandingPage.jsx — Marketing landing page shown to unauthenticated visitors.
 */

import { useState, useEffect } from "react";

/* ─── Data ───────────────────────────────────────────────────────────────── */

const FAKE_EDGES = [
  { platform: "Kalshi",      title: "Fed cuts rates in March 2026?",          marketPct: 34, modelPct: 47, edge: 13  },
  { platform: "Polymarket",  title: "BTC above $110k by end of Q2",           marketPct: 41, modelPct: 29, edge: -12 },
  { platform: "Kalshi",      title: "US enters recession in 2026",             marketPct: 28, modelPct: 38, edge: 10  },
  { platform: "Polymarket",  title: "Trump approval >50% by June",             marketPct: 22, modelPct: 31, edge: 9   },
  { platform: "Kalshi",      title: "Nvidia Q1 earnings beat consensus",       marketPct: 67, modelPct: 74, edge: 7   },
  { platform: "Polymarket",  title: "ETH flips BTC market cap in 2026",       marketPct: 8,  modelPct: 4,  edge: -4  },
  { platform: "Kalshi",      title: "CPI above 3% in February 2026",          marketPct: 45, modelPct: 53, edge: 8   },
  { platform: "Polymarket",  title: "Lakers win NBA championship",             marketPct: 12, modelPct: 8,  edge: -4  },
  { platform: "Kalshi",      title: "OpenAI releases GPT-5 before April",     marketPct: 31, modelPct: 42, edge: 11  },
  { platform: "Polymarket",  title: "Ukraine ceasefire by end of 2026",       marketPct: 55, modelPct: 48, edge: -7  },
  { platform: "Kalshi",      title: "S&P 500 above 6,500 by March",           marketPct: 38, modelPct: 46, edge: 8   },
  { platform: "Polymarket",  title: "Musk exits DOGE before July 2026",       marketPct: 44, modelPct: 37, edge: -7  },
  { platform: "Kalshi",      title: "Apple Q1 earnings beat estimate",         marketPct: 62, modelPct: 71, edge: 9   },
  { platform: "Polymarket",  title: "Gold above $3,000/oz in March",          marketPct: 57, modelPct: 65, edge: 8   },
  { platform: "Kalshi",      title: "US unemployment below 4% in Q2",         marketPct: 71, modelPct: 63, edge: -8  },
  { platform: "Polymarket",  title: "Solana surpasses Ethereum TVL",          marketPct: 14, modelPct: 21, edge: 7   },
  { platform: "Kalshi",      title: "Debt ceiling triggers technical default", marketPct: 6,  modelPct: 11, edge: 5   },
  { platform: "Polymarket",  title: "Chiefs win Super Bowl LXI",              marketPct: 23, modelPct: 17, edge: -6  },
  { platform: "Kalshi",      title: "Microsoft Azure beats AWS in Q2 rev",    marketPct: 19, modelPct: 28, edge: 9   },
  { platform: "Polymarket",  title: "Dogecoin above $0.40 by April",          marketPct: 33, modelPct: 24, edge: -9  },
];

// Ticker items — duplicated inside TickerBar for seamless CSS loop
const TICKER_ITEMS = [
  { label: "FED RATE CUT MAR",    prob: 34, delta:  2.1 },
  { label: "BTC >$110K Q2",       prob: 41, delta: -3.2 },
  { label: "CPI >3% FEB",         prob: 45, delta:  1.8 },
  { label: "TRUMP APPROVAL 50%",  prob: 22, delta:  0.9 },
  { label: "NVDA Q1 BEAT",        prob: 67, delta: -0.5 },
  { label: "RECESSION 2026",      prob: 28, delta: -1.4 },
  { label: "GPT-5 BEFORE APR",    prob: 31, delta:  3.2 },
  { label: "S&P 500 >6500",       prob: 38, delta:  2.7 },
  { label: "UKRAINE CEASEFIRE",   prob: 55, delta: -0.8 },
  { label: "GOLD >$3000",         prob: 57, delta:  1.5 },
  { label: "AAPL Q1 BEAT",        prob: 62, delta:  0.3 },
  { label: "BTC >$100K",          prob: 73, delta: -1.9 },
  { label: "US UNEMP <4%",        prob: 71, delta:  0.7 },
  { label: "SOL FLIPS ETH TVL",   prob: 14, delta:  2.4 },
  { label: "DOGE >$0.40",         prob: 33, delta: -2.8 },
  { label: "MUSK EXITS DOGE",     prob: 44, delta:  1.3 },
  { label: "MICROSOFT >AWS REV",  prob: 19, delta:  0.6 },
  { label: "FED PAUSE MAR",       prob: 66, delta: -2.1 },
  { label: "ETH FLIPS BTC CAP",   prob:  8, delta:  1.1 },
  { label: "CHIEFS SB LXI",       prob: 23, delta:  1.0 },
];

// Top 3 signals for the summary panel
const TOP_SIGNALS = [
  { platform: "Kalshi",     title: "Fed cuts rates in March 2026?",     edge: 13, confidence: 87 },
  { platform: "Kalshi",     title: "OpenAI releases GPT-5 before April", edge: 11, confidence: 79 },
  { platform: "Kalshi",     title: "US enters recession in 2026",        edge: 10, confidence: 73 },
];

/* ─── TickerBar ──────────────────────────────────────────────────────────── */
// Fixed strip below the navbar — market items scroll left continuously.
function TickerBar() {
  // Duplicated so the CSS translateX(-50%) loop is seamless
  const items = [...TICKER_ITEMS, ...TICKER_ITEMS];

  return (
    <div
      className="fixed top-14 left-0 right-0 z-40 overflow-hidden border-b border-white/[0.06]"
      style={{ height: "30px", background: "rgba(10,13,28,0.92)", backdropFilter: "blur(8px)" }}
    >
      <div
        className="flex items-center h-full"
        style={{ width: "max-content", animation: "tickerScroll 90s linear infinite" }}
      >
        {items.map((item, i) => (
          <span
            key={i}
            className="inline-flex items-center gap-2 px-5 h-full border-r border-white/[0.06] shrink-0"
          >
            <span className="font-heading text-[9px] text-slate-500 uppercase tracking-wider whitespace-nowrap">
              {item.label}
            </span>
            <span className="font-heading font-tnum text-[10px] text-slate-300 whitespace-nowrap">
              {item.prob}%
            </span>
            <span
              className={`font-heading font-tnum text-[10px] whitespace-nowrap ${
                item.delta > 0 ? "text-emerald-500/80" : "text-rose-500/80"
              }`}
            >
              {item.delta > 0 ? "+" : ""}
              {item.delta.toFixed(1)}%
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}

/* ─── StatCards ──────────────────────────────────────────────────────────── */
function StatCards() {
  return (
    <div className="grid grid-cols-3 gap-2.5">
      {[
        { label: "Markets",    value: "847",  sub: "monitored live",  pulse: false },
        { label: "Live Edges", value: "23",   sub: "detected now",    pulse: true  },
        { label: "Avg Edge",   value: "8.4%", sub: "magnitude",       pulse: false },
      ].map((s) => (
        <div
          key={s.label}
          className="card-glow rounded-lg p-3 border border-white/[0.08] bg-white/[0.025]"
        >
          <p className="font-heading text-[9px] text-slate-600 uppercase tracking-wider mb-2">
            {s.label}
          </p>
          <div className="flex items-center gap-1.5">
            <span className="font-heading font-bold text-xl text-white leading-none">
              {s.value}
            </span>
            {s.pulse && (
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-[edgePing_2.4s_ease-in-out_infinite] shrink-0" />
            )}
          </div>
          <p className="text-[9px] text-slate-600 mt-1">{s.sub}</p>
        </div>
      ))}
    </div>
  );
}

/* ─── TopSignalsPanel ────────────────────────────────────────────────────── */
// Compact panel listing the three highest-edge detections right now.
// Confidence bars animate in from 0→target on mount.
function TopSignalsPanel() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 200);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      className="w-full rounded-xl overflow-hidden border border-white/10"
      style={{ background: "#0d1024" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/[0.08] bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <span className="font-heading text-[10px] text-slate-400 uppercase tracking-wider">
            Top Signals
          </span>
          <span className="text-[9px] text-slate-600">— right now</span>
        </div>
        <span className="text-[9px] text-slate-600 uppercase tracking-widest">
          3 found
        </span>
      </div>

      {/* Rows */}
      <div className="divide-y divide-white/[0.05]">
        {TOP_SIGNALS.map((sig, i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-3">
            <span
              className={`shrink-0 font-heading text-[9px] px-1.5 py-0.5 rounded uppercase tracking-wider ${
                sig.platform === "Kalshi"
                  ? "bg-cyan-400/15 text-cyan-400"
                  : "bg-amber-400/15 text-amber-400"
              }`}
            >
              {sig.platform === "Kalshi" ? "KAL" : "POLY"}
            </span>
            <span className="font-heading text-[11px] text-slate-300 flex-1 truncate min-w-0">
              {sig.title}
            </span>
            <div className="flex items-center gap-2.5 shrink-0">
              {/* Animated confidence bar */}
              <div className="w-16 h-[3px] rounded-full bg-white/[0.08] overflow-hidden">
                <div
                  className="h-full rounded-full bg-cyan-400/50"
                  style={{
                    width: mounted ? `${sig.confidence}%` : "0%",
                    transition: `width 0.9s ease-out ${i * 0.15}s`,
                  }}
                />
              </div>
              <span className="font-heading font-tnum text-[11px] text-cyan-400 w-9 text-right">
                +{sig.edge}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── FeedRow ────────────────────────────────────────────────────────────── */
function FeedRow({ row, isNew }) {
  const edgePositive = row.edge > 0;
  const edgeBig      = Math.abs(row.edge) >= 5;

  return (
    <div
      className={`grid items-center gap-x-2 px-4 py-2.5 ${
        isNew ? "animate-[fadeSlideIn_0.45s_ease-out_both]" : ""
      }`}
      style={{ gridTemplateColumns: "1fr 2.5rem 2.5rem 3rem" }}
    >
      <div className="min-w-0 flex items-center gap-2">
        <span
          className={`shrink-0 font-heading text-[9px] px-1.5 py-0.5 rounded uppercase tracking-wider ${
            row.platform === "Kalshi"
              ? "bg-cyan-400/15 text-cyan-400"
              : "bg-amber-400/15 text-amber-400"
          }`}
        >
          {row.platform === "Kalshi" ? "KAL" : "POLY"}
        </span>
        <span className="font-heading text-[11px] text-slate-300 truncate leading-tight">
          {row.title}
        </span>
      </div>
      <span className="font-heading font-tnum text-[11px] text-slate-400 text-right tabular-nums">
        {row.marketPct}%
      </span>
      <span className="font-heading font-tnum text-[11px] text-slate-300 text-right tabular-nums">
        {row.modelPct}%
      </span>
      <span
        className={`font-heading font-tnum text-[11px] text-right tabular-nums ${
          edgeBig
            ? edgePositive ? "text-cyan-400" : "text-rose-400"
            : "text-slate-500"
        }`}
      >
        {edgePositive ? "+" : ""}
        {row.edge}%
      </span>
    </div>
  );
}

/* ─── LiveFeedDemo ───────────────────────────────────────────────────────── */
function LiveFeedDemo() {
  const [visibleRows, setVisibleRows] = useState([]);

  useEffect(() => {
    setVisibleRows(FAKE_EDGES.slice(0, 5).map((r, i) => ({ ...r, key: i })));
    let idx = 5;
    const id = setInterval(() => {
      const row = { ...FAKE_EDGES[idx % FAKE_EDGES.length], key: Date.now() };
      setVisibleRows((prev) => [row, ...prev].slice(0, 6));
      idx++;
    }, 2500);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      className="relative w-full rounded-xl overflow-hidden border border-white/10"
      style={{ background: "#0d1024" }}
    >
      <div className="scan-pulse" />

      {/* Terminal header */}
      <div className="flex items-center gap-2.5 px-4 py-2.5 border-b border-white/10 bg-white/[0.025]">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-[edgePing_2.4s_ease-in-out_infinite]" />
        <span className="font-heading text-[11px] text-slate-400 flex-1 truncate">
          edge_detection.py &nbsp;—&nbsp; monitoring 847 markets
        </span>
        <span className="font-heading text-[10px] text-cyan-400/70 uppercase tracking-widest shrink-0">
          LIVE
        </span>
      </div>

      {/* Mini probability chart */}
      <div className="px-4 pt-3 pb-1">
        <p className="font-heading text-[9px] text-slate-600 uppercase tracking-widest mb-2">
          Model Confidence — 24h
        </p>
        <svg viewBox="0 0 280 56" className="w-full h-14" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor="rgba(34,211,238,0.18)" />
              <stop offset="100%" stopColor="rgba(34,211,238,0)"    />
            </linearGradient>
          </defs>
          <line x1="0" y1="18" x2="280" y2="18" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
          <line x1="0" y1="36" x2="280" y2="36" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
          <path
            d="M0,48 C25,44 45,40 68,36 S105,30 128,27 S158,22 178,20 S210,15 232,17 S258,12 280,10 L280,56 L0,56 Z"
            fill="url(#chartFill)"
            className="chart-area"
          />
          <path
            d="M0,48 C25,44 45,40 68,36 S105,30 128,27 S158,22 178,20 S210,15 232,17 S258,12 280,10"
            fill="none"
            stroke="rgba(34,211,238,0.85)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="chart-line"
          />
        </svg>
      </div>

      {/* Column headers */}
      <div
        className="grid gap-x-2 px-4 py-1.5 border-y border-white/[0.06]"
        style={{ gridTemplateColumns: "1fr 2.5rem 2.5rem 3rem" }}
      >
        <span className="font-heading text-[9px] text-slate-600 uppercase tracking-wider">Market</span>
        <span className="font-heading text-[9px] text-slate-600 uppercase tracking-wider text-right">Mkt</span>
        <span className="font-heading text-[9px] text-slate-600 uppercase tracking-wider text-right">Model</span>
        <span className="font-heading text-[9px] text-slate-600 uppercase tracking-wider text-right">Edge</span>
      </div>

      {/* Streaming rows */}
      <div className="divide-y divide-white/[0.05]">
        {visibleRows.map((row, i) => (
          <FeedRow key={row.key} row={row} isNew={i === 0} />
        ))}
      </div>
    </div>
  );
}

/* ─── Navbar ─────────────────────────────────────────────────────────────── */
function Navbar({ onLogin }) {
  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 md:px-12 h-14
                 bg-[#151829]/80 backdrop-blur-md border-b border-white/10"
    >
      {/* Wordmark + beta badge */}
      <div className="flex items-center gap-2.5">
        <span className="font-heading text-white text-sm uppercase tracking-wider">Miscalibrated</span>
        <span className="font-heading text-[9px] text-cyan-400/70 border border-cyan-400/25 rounded px-1.5 py-0.5 uppercase tracking-widest">
          Beta
        </span>
      </div>

      {/* Center nav links */}
      <div className="hidden md:flex items-center gap-8">
        {["Features", "How It Works", "Pricing"].map((label) => (
          <span
            key={label}
            className="font-heading text-[11px] text-slate-500 uppercase tracking-wider
                       hover:text-slate-300 transition-colors duration-150 cursor-default"
          >
            {label}
          </span>
        ))}
      </div>

      {/* Sign in */}
      <button
        onClick={onLogin}
        className="font-heading text-[11px] uppercase tracking-wider text-slate-300 border border-white/20 rounded-lg px-4 py-1.5
                   hover:border-cyan-400/50 hover:text-cyan-400 transition-all duration-150"
      >
        Sign In
      </button>
    </nav>
  );
}

/* ─── LandingPage (default export) ──────────────────────────────────────── */
export default function LandingPage({ onLogin }) {
  return (
    <div className="min-h-screen bg-[#151829] relative overflow-hidden">

      {/* ── Background layers ── */}

      {/* Dot grid */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.09) 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      {/* Subtle diagonal stripes — adds tactile texture */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "repeating-linear-gradient(-45deg, rgba(255,255,255,0.022) 0px, rgba(255,255,255,0.022) 1px, transparent 1px, transparent 40px)",
        }}
      />

      {/* Ambient glow — cyan, upper-left */}
      <div
        className="ambient-glow animate-[glowPulse_7s_ease-in-out_infinite]"
        style={{ top: "5%", left: "2%" }}
      />

      {/* Ambient glow — indigo, center-right */}
      <div
        className="ambient-glow animate-[glowPulse_9s_ease-in-out_infinite_2s]"
        style={{
          top: "40%", right: "8%", left: "auto",
          width: "600px", height: "600px",
          background: "radial-gradient(circle, rgba(99,102,241,0.14) 0%, transparent 70%)",
        }}
      />

      {/* Ambient glow — violet, lower-left */}
      <div
        className="ambient-glow animate-[glowPulse_11s_ease-in-out_infinite_4s]"
        style={{
          bottom: "5%", top: "auto", left: "15%",
          width: "480px", height: "480px",
          background: "radial-gradient(circle, rgba(139,92,246,0.11) 0%, transparent 70%)",
        }}
      />

      <Navbar onLogin={onLogin} />
      <TickerBar />

      {/* ── Hero ── */}
      {/* pt-[86px] = 56px fixed navbar + 30px fixed ticker */}
      <section className="relative z-10 flex items-center min-h-screen pt-[86px]">
        <div className="w-full max-w-7xl mx-auto px-6 md:px-12 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

            {/* ── Left column ── */}
            <div className="flex flex-col gap-5">

              {/* System status line */}
              <div className="flex items-center gap-3 text-[10px]">
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-[edgePing_2s_ease-in-out_infinite]" />
                  <span className="text-emerald-400/80 uppercase tracking-wider">System Active</span>
                </span>
                <span className="text-slate-700">·</span>
                <span className="text-slate-600 uppercase tracking-wider">Scanning 847 Markets</span>
                <span className="text-slate-700">·</span>
                <span className="text-slate-600">Last update 0.3s</span>
              </div>

              {/* Eyebrow */}
              <div className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                <span className="font-heading text-[11px] text-cyan-400/80 uppercase tracking-[0.2em]">
                  Prediction Market Intelligence
                </span>
              </div>

              {/* Headline */}
              <h1 className="font-heading font-bold text-5xl md:text-6xl text-white leading-[1.08] tracking-tight">
                The market<br />
                is wrong.<br />
                <span className="text-cyan-400">Find the edge.</span>
              </h1>

              {/* Description */}
              <p className="text-slate-400 text-base leading-relaxed max-w-[400px]">
                Miscalibrated monitors Kalshi and Polymarket in real time,
                running AI models against every open contract to surface
                mispricings before the crowd corrects them.
              </p>

              {/* Stat cards */}
              <StatCards />

              {/* CTA */}
              <div>
                <button
                  onClick={onLogin}
                  className="group font-heading text-[13px] uppercase tracking-wider
                             bg-gradient-to-br from-cyan-300 to-cyan-500
                             hover:from-cyan-200 hover:to-cyan-400
                             text-slate-900 font-semibold
                             rounded-lg px-8 py-3
                             transition-all duration-200
                             shadow-[0_1px_0_rgba(255,255,255,0.3)_inset,0_-2px_0_rgba(0,0,0,0.18)_inset,0_6px_16px_rgba(0,0,0,0.4),0_0_20px_rgba(34,211,238,0.16)]
                             hover:shadow-[0_1px_0_rgba(255,255,255,0.35)_inset,0_-2px_0_rgba(0,0,0,0.18)_inset,0_8px_24px_rgba(0,0,0,0.45),0_0_28px_rgba(34,211,238,0.22)]
                             hover:-translate-y-0.5
                             active:translate-y-px active:brightness-95"
                >
                  <span className="flex items-center gap-2">
                    Get Early Access
                    <span className="group-hover:translate-x-0.5 transition-transform duration-200">→</span>
                  </span>
                </button>
              </div>

              {/* Footer stat strip */}
              <div className="flex items-center gap-3 text-xs text-slate-600">
                <span>3 platforms</span>
                <span className="text-slate-700">·</span>
                <span>Real-time</span>
                <span className="text-slate-700">·</span>
                <span>AI-powered</span>
              </div>
            </div>

            {/* ── Right column — stacked panels ── */}
            <div className="flex flex-col gap-4">
              <LiveFeedDemo />
              <TopSignalsPanel />
            </div>

          </div>
        </div>
      </section>
    </div>
  );
}
