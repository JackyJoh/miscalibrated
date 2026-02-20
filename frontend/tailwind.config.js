/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      // ── Brand Colors (from BRAND.md) ─────────────────────────────────────
      colors: {
        brand: {
          base:           "#151829",   // Deepest background (page level)
          bg:             "#1a1f3a",   // Content area, header, dropdowns
          surface:        "rgba(255, 255, 255, 0.05)",  // Cards, inputs
          hover:          "rgba(255, 255, 255, 0.07)",  // Card hover state
          accent:         "#22d3ee",   // Cyan primary accent
          "accent-hover": "#0891b2",   // Cyan hover/pressed
          "accent-muted": "#155e75",   // Subdued/disabled
          border:         "rgba(255, 255, 255, 0.1)",
          "border-active":"rgba(34, 211, 238, 0.3)",
        },
      },
      // ── Font Families (IBM Plex Mono + Inter) ────────────────────────────
      fontFamily: {
        heading: ["IBM Plex Mono", "ui-monospace", "monospace"],
        sans:    ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      // ── Box Shadows (glow effects) ───────────────────────────────────────
      boxShadow: {
        "glow-sm":  "0 0 12px rgba(34, 211, 238, 0.35)",
        "glow-md":  "0 0 20px rgba(34, 211, 238, 0.15)",
        "glow-lg":  "0 0 30px rgba(34, 211, 238, 0.30)",
      },
    },
  },
  plugins: [],
};
