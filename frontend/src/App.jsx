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

import LandingPage from "./pages/LandingPage.jsx";
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

  // If not authenticated, show the marketing landing page
  if (!isAuthenticated) {
    return <LandingPage onLogin={loginWithRedirect} />;
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


