/**
 * pages/Settings.jsx — Alert preferences and account info.
 *
 * Lets users configure:
 *   - Alert threshold (minimum edge magnitude to trigger an email)
 *   - Platforms to receive alerts from
 *   - Enable/disable all alerts
 *
 * TODO: Load current preferences from GET /api/v1/alerts/preferences
 * TODO: Save preferences via PATCH /api/v1/alerts/preferences
 */

import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

export default function Settings() {
  const { user, logout } = useAuth0();

  // Local state — will eventually be synced with the API
  const [threshold, setThreshold] = useState(5);           // In percent
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [platforms, setPlatforms] = useState({ kalshi: true, polymarket: true });

  const togglePlatform = (p) =>
    setPlatforms((prev) => ({ ...prev, [p]: !prev[p] }));

  return (
    <div className="max-w-2xl mx-auto px-6 py-8 space-y-8">
      {/* ── Header ──────────────────────────────────────────────── */}
      <div>
        <h1 className="font-heading font-bold text-2xl text-white tracking-tight">
          Settings
        </h1>
        <p className="mt-1 text-slate-400 text-sm font-light">
          Alert preferences and account management.
        </p>
      </div>

      {/* ── Account ─────────────────────────────────────────────── */}
      <Section title="Account">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white text-sm font-medium">{user?.email || "—"}</p>
            <p className="text-slate-500 text-xs mt-0.5">Authenticated via Auth0</p>
          </div>
          <button
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            className="bg-white/10 hover:bg-white/15 text-white font-heading font-semibold rounded-lg
                       border border-white/10 hover:border-cyan-400/50 px-4 py-2 text-sm
                       transition-all duration-200"
          >
            Sign Out
          </button>
        </div>
      </Section>

      {/* ── Alert Configuration ─────────────────────────────────── */}
      <Section title="Email Alerts">
        {/* Enable toggle */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white text-sm font-medium">Enable email alerts</p>
            <p className="text-slate-500 text-xs mt-0.5">
              Receive an email when an edge exceeds your threshold.
            </p>
          </div>
          <button
            onClick={() => setAlertsEnabled((v) => !v)}
            className={`w-10 h-6 rounded-full transition-all duration-200 relative ${
              alertsEnabled ? "bg-cyan-500" : "bg-white/10"
            }`}
          >
            <span
              className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all duration-200 ${
                alertsEnabled ? "left-5" : "left-1"
              }`}
            />
          </button>
        </div>

        {/* Threshold slider */}
        <div className="space-y-2 mt-4">
          <div className="flex items-center justify-between">
            <label className="font-heading font-semibold text-xs uppercase tracking-wider text-slate-400">
              Minimum Edge Threshold
            </label>
            <span className="font-tnum text-cyan-400 text-sm font-bold">{threshold}%</span>
          </div>
          <input
            type="range"
            min={1}
            max={30}
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="w-full accent-cyan-400"
            disabled={!alertsEnabled}
          />
          <p className="text-xs text-slate-500">
            You'll only be alerted when the model finds an edge larger than this value.
          </p>
        </div>

        {/* Platform checkboxes */}
        <div className="space-y-2 mt-4">
          <p className="font-heading font-semibold text-xs uppercase tracking-wider text-slate-400">
            Platforms
          </p>
          {Object.entries(platforms).map(([name, checked]) => (
            <label key={name} className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={checked}
                onChange={() => togglePlatform(name)}
                disabled={!alertsEnabled}
                className="accent-cyan-400 w-4 h-4"
              />
              <span className="text-slate-300 text-sm capitalize">{name}</span>
            </label>
          ))}
        </div>
      </Section>

      {/* ── Save ─────────────────────────────────────────────────── */}
      <button
        className="bg-cyan-500 hover:bg-cyan-600 text-white font-heading font-semibold rounded-lg px-6 py-2.5
                   shadow-[0_0_20px_rgba(34,211,238,0.15)] hover:shadow-[0_0_30px_rgba(34,211,238,0.3)]
                   transition-all duration-200 text-sm"
      >
        Save Preferences
      </button>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="card-glow bg-white/5 border border-white/10 rounded-lg p-5 space-y-4">
      <h2 className="font-heading font-semibold text-sm uppercase tracking-wider text-slate-300 border-b border-white/10 pb-3">
        {title}
      </h2>
      {children}
    </div>
  );
}
