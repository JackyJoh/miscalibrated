/**
 * pages/Dashboard.jsx — Main overview page.
 *
 * Sections (stubs for now):
 *   - Summary stat cards (total markets, edges detected, top edge magnitude)
 *   - Recent edges feed (highest magnitude first)
 *   - Market activity sparklines
 */

export default function Dashboard() {
  // TODO: Fetch summary stats from GET /api/v1/edges and GET /api/v1/markets
  const stats = [
    { label: "Open Markets",   value: "—",  sub: "Kalshi + Polymarket" },
    { label: "Edges Detected", value: "—",  sub: "Last 24 hours" },
    { label: "Top Edge",       value: "—%", sub: "Largest magnitude" },
    { label: "Alerts Sent",    value: "—",  sub: "This week" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* ── Page Header ───────────────────────────────────────────── */}
      <div>
        <h1 className="font-heading font-bold text-2xl text-white tracking-tight">
          Dashboard
        </h1>
        <p className="mt-1 text-slate-400 text-sm font-light">
          Live overview of market edges and alert activity.
        </p>
      </div>

      {/* ── Stat Cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="card-glow bg-white/5 border border-white/10 rounded-lg p-4 space-y-1"
          >
            <p className="font-heading font-semibold text-xs uppercase tracking-wider text-slate-400">
              {stat.label}
            </p>
            <p className="font-bold font-tnum text-2xl text-white">{stat.value}</p>
            <p className="text-xs text-slate-500">{stat.sub}</p>
          </div>
        ))}
      </div>

      {/* ── Recent Edges ────────────────────────────────────────────── */}
      <div className="card-glow bg-white/5 border border-white/10 rounded-lg">
        <div className="px-4 py-3 border-b border-white/10">
          <h2 className="font-heading font-semibold text-sm uppercase tracking-wider text-slate-300">
            Recent Edges
          </h2>
        </div>
        <div className="p-8 text-center text-slate-500 text-sm">
          {/* TODO: Render EdgeRow components from API data */}
          Edge data will appear here once the backend is connected.
        </div>
      </div>
    </div>
  );
}
