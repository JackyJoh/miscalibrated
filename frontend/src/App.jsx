/**
 * App.jsx — Root component. Owns the router and top-level layout.
 *
 * Route structure:
 *   /              → Dashboard (market feed overview + edge summary)
 *   /markets       → Full market browser with filters
 *   /edges         → Edge detection feed with magnitude sorting
 *   /agent         → AI agent chat interface
 *   /settings      → Alert preferences and account settings
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";

import Sidebar from "./components/layout/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Markets from "./pages/Markets.jsx";
import Edges from "./pages/Edges.jsx";
import Agent from "./pages/Agent.jsx";
import Settings from "./pages/Settings.jsx";

export default function App() {
  const { isLoading, isAuthenticated, loginWithRedirect } = useAuth0();

  // Show a minimal loading state while Auth0 initializes
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#151829] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-6 h-6 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />
          <span className="text-slate-400 text-sm font-heading">Loading...</span>
        </div>
      </div>
    );
  }

  // If not authenticated, show a login gate
  if (!isAuthenticated) {
    return <LoginGate onLogin={loginWithRedirect} />;
  }

  // Authenticated: render the full app with sidebar layout
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#151829] flex">
        {/* Persistent sidebar navigation */}
        <Sidebar />

        {/* Main content area */}
        <main className="flex-1 bg-[#1a1f3a] min-h-screen overflow-y-auto">
          <Routes>
            <Route path="/"          element={<Dashboard />} />
            <Route path="/markets"   element={<Markets />} />
            <Route path="/edges"     element={<Edges />} />
            <Route path="/agent"     element={<Agent />} />
            <Route path="/settings"  element={<Settings />} />
            {/* Catch-all: redirect unknown routes to dashboard */}
            <Route path="*"          element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

/** Simple login gate shown to unauthenticated visitors. */
function LoginGate({ onLogin }) {
  return (
    <div className="min-h-screen bg-[#151829] flex items-center justify-center relative overflow-hidden">
      {/* Ambient glow orb */}
      <div className="ambient-glow" style={{ top: "20%", left: "50%", transform: "translateX(-50%)" }} />

      <div className="relative z-10 flex flex-col items-center gap-8 text-center max-w-md px-6">
        {/* Logo / wordmark */}
        <div>
          <h1 className="font-heading font-bold text-3xl text-white tracking-tight">
            Miscalibrated
          </h1>
          <p className="mt-2 text-slate-400 text-sm font-light">
            Real-time edge detection for prediction markets.
          </p>
        </div>

        {/* Login CTA */}
        <button
          onClick={() => onLogin()}
          className="bg-cyan-500 hover:bg-cyan-600 text-white font-heading font-semibold rounded-lg px-8 py-3
                     shadow-[0_0_20px_rgba(34,211,238,0.15)] hover:shadow-[0_0_30px_rgba(34,211,238,0.3)]
                     transition-all duration-200"
        >
          Sign In
        </button>
      </div>
    </div>
  );
}
