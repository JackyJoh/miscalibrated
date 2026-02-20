/**
 * pages/Markets.jsx — Full market browser.
 *
 * Features (stubs):
 *   - Platform filter tabs (All / Kalshi / Polymarket)
 *   - Category filter
 *   - Searchable market list sorted by yes_price / volume / close_time
 *   - Click a market → per-market detail panel
 */

import { useState } from "react";

const PLATFORMS = ["All", "Kalshi", "Polymarket"];

export default function Markets() {
  const [activePlatform, setActivePlatform] = useState("All");

  // TODO: Fetch markets from GET /api/v1/markets?platform=...&limit=50

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
      {/* ── Header ────────────────────────────────────────────────── */}
      <div>
        <h1 className="font-heading font-bold text-2xl text-white tracking-tight">
          Markets
        </h1>
        <p className="mt-1 text-slate-400 text-sm font-light">
          Browse all open prediction markets across platforms.
        </p>
      </div>

      {/* ── Platform Filter Tabs ─────────────────────────────────── */}
      <div className="flex gap-2">
        {PLATFORMS.map((p) => (
          <button
            key={p}
            onClick={() => setActivePlatform(p)}
            className={`px-4 py-1.5 rounded-lg text-sm font-heading font-semibold transition-all duration-200 ${
              activePlatform === p
                ? "border border-cyan-400 bg-cyan-500 text-white shadow-[0_0_12px_rgba(34,211,238,0.35)]"
                : "border border-white/10 bg-white/5 hover:bg-white/10 hover:border-cyan-400/30 text-slate-300"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* ── Market List ─────────────────────────────────────────── */}
      <div className="card-glow bg-white/5 border border-white/10 rounded-lg">
        {/* Table header */}
        <div className="grid grid-cols-[1fr_auto_auto_auto] gap-4 px-4 py-2 border-b border-white/10">
          {["Market", "Platform", "Prob.", "Volume"].map((col) => (
            <span key={col} className="font-heading font-semibold text-xs uppercase tracking-wider text-slate-400">
              {col}
            </span>
          ))}
        </div>

        {/* Placeholder rows */}
        <div className="p-8 text-center text-slate-500 text-sm">
          {/* TODO: Map over fetched markets and render MarketRow components */}
          Market data will appear here once the backend is connected.
        </div>
      </div>
    </div>
  );
}
