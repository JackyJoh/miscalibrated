/**
 * pages/Edges.jsx — Edge detection feed.
 *
 * Shows markets where the calibration model found significant mispricing.
 * Sorted by edge magnitude descending by default.
 *
 * Features (stubs):
 *   - Edge magnitude filter slider
 *   - Direction filter (YES / NO edge)
 *   - Platform filter
 *   - Each row shows market title, market prob, model prob, edge magnitude, direction
 */

import { useState } from "react";

export default function Edges() {
  const [minMagnitude, setMinMagnitude] = useState(0.05);

  // TODO: Fetch from GET /api/v1/edges?min_magnitude={minMagnitude}

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
      {/* ── Header ────────────────────────────────────────────────── */}
      <div>
        <h1 className="font-heading font-bold text-2xl text-white tracking-tight">
          Edge Feed
        </h1>
        <p className="mt-1 text-slate-400 text-sm font-light">
          Markets where the model's probability diverges from the market price.
        </p>
      </div>

      {/* ── Filters ─────────────────────────────────────────────── */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <label className="font-heading font-semibold text-xs uppercase tracking-wider text-slate-400">
            Min Edge
          </label>
          <input
            type="range"
            min={0.01}
            max={0.5}
            step={0.01}
            value={minMagnitude}
            onChange={(e) => setMinMagnitude(Number(e.target.value))}
            className="accent-cyan-400"
          />
          <span className="font-tnum text-cyan-400 text-sm font-semibold w-12">
            {(minMagnitude * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* ── Edge List ────────────────────────────────────────────── */}
      <div className="card-glow bg-white/5 border border-white/10 rounded-lg">
        {/* Table header */}
        <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-4 px-4 py-2 border-b border-white/10">
          {["Market", "Mkt Prob", "Model Prob", "Edge", "Direction"].map((col) => (
            <span key={col} className="font-heading font-semibold text-xs uppercase tracking-wider text-slate-400">
              {col}
            </span>
          ))}
        </div>

        <div className="p-8 text-center text-slate-500 text-sm">
          {/* TODO: Map over fetched edges and render EdgeRow components */}
          No edges meet the current threshold. Backend connection pending.
        </div>
      </div>
    </div>
  );
}
